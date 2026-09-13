from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from typing import Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import create_session
from db.session import get_db
from services.tutor import build_system_prompt, route_model
from services.profiles import get_child_by_device_id, get_child_by_id
from services.sessions import log_turn
from services.knowledge_tracing import mastery_context_for_prompt
from services.session_intelligence import (
    build_24hr_history_context,
    build_prereq_tree_context,
    get_session_prereq_state,
    increment_prereq_turn,
    reset_prereq_turn,
    extract_and_update_interests,
)
from db.crud import get_most_recent_ended_session

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "etutor"
    messages: list[Message]
    stream: bool = False
    child_id: Optional[str] = None

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v):
        if not v:
            raise ValueError("messages must not be empty")
        return v


@router.post("/chat/completions")
async def chat(
    req: ChatRequest,
    x_device_id: str = Header(None),
    x_child_id: str = Header(None),
    session: AsyncSession = Depends(get_db),
):
    child_id = x_child_id or req.child_id
    if not child_id and x_device_id:
        child = await get_child_by_device_id(x_device_id, session)
        if child:
            child_id = str(child.id)

    if not child_id:
        raise HTTPException(status_code=400, detail="No child identity — provide X-Child-ID or X-Device-ID header")

    child = await get_child_by_id(child_id, session)
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    mastery_ctx = await mastery_context_for_prompt(child_id, session, limit=5)

    # Phase 3 session intelligence (HIST-01, HIST-02, CURR-02)
    history_ctx = await build_24hr_history_context(child_id, session)
    prereq_tree = await build_prereq_tree_context(child_id, session, limit=5)
    prereq_state = get_session_prereq_state(child_id)

    # D-07: advance escalation counter for each unmet prereq on this turn
    for _entry in (prereq_tree or []):
        increment_prereq_turn(child_id, _entry["prereq_kc_id"])

    # D-08 catch-up: extract interests from previous session that missed /end call
    prev_session = await get_most_recent_ended_session(child_id, session)
    if prev_session and prev_session.id:
        await extract_and_update_interests(prev_session.id, child_id, session)

    system_prompt = await build_system_prompt(
        child,
        mastery_context=mastery_ctx or None,
        history_context=history_ctx or None,
        prereq_tree=prereq_tree or None,
        session_prereq_state=prereq_state or None,
    )
    model = route_model(child)

    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": m.role, "content": m.content} for m in req.messages]

    import litellm
    if req.stream:
        async def generate():
            db_session_row = await create_session(child_id, session)
            full_content = []
            response = await litellm.acompletion(model=model, messages=messages, stream=True)
            async for chunk in response:
                delta = chunk.choices[0].delta.content or ""
                full_content.append(delta)
                yield f"data: {json.dumps({'choices': [{'delta': {'content': delta}}]})}\n\n"
            yield "data: [DONE]\n\n"
            await log_turn(child_id, req.messages[-1].content, "".join(full_content),
                           session, session_id=db_session_row.id)
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        response = await litellm.acompletion(model=model, messages=messages)
        content = response.choices[0].message.content
        db_session_row = await create_session(child_id, session)
        turn = await log_turn(child_id, req.messages[-1].content, content, session, session_id=db_session_row.id)
        # D-06 reset: clear escalation counter when child answers a prereq probe correctly.
        # correct and kc_id are not yet resolved in this path (Phase 4 will wire BKT probe detection).
        # Guard is non-operative until then — included to complete D-06 wiring.
        _correct = turn.correct
        _kc_id = turn.kc_id
        if _correct and _kc_id and _kc_id in [_e.get("prereq_kc_id") for _e in (prereq_tree or [])]:
            reset_prereq_turn(child_id, _kc_id)
        return {
            "choices": [{"message": {"role": "assistant", "content": content}}]
        }
