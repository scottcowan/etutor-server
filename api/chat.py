from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from services.tutor import build_system_prompt, route_model
from services.profiles import get_child_by_device_id, get_child_by_id
from services.sessions import log_turn

router = APIRouter()


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    model: str = "etutor"
    messages: list[Message]
    stream: bool = False
    child_id: Optional[str] = None


@router.post("/chat/completions")
async def chat(
    req: ChatRequest,
    x_device_id: str = Header(None),
    x_child_id: str = Header(None),
):
    child_id = x_child_id or req.child_id
    if not child_id and x_device_id:
        child = await get_child_by_device_id(x_device_id)
        if child:
            child_id = str(child.id)

    if not child_id:
        raise HTTPException(status_code=400, detail="No child identity — provide X-Child-ID or X-Device-ID header")

    child = await get_child_by_id(child_id)
    system_prompt = await build_system_prompt(child)
    model = route_model(child)

    messages = [{"role": "system", "content": system_prompt}]
    messages += [{"role": m.role, "content": m.content} for m in req.messages]

    import litellm
    if req.stream:
        async def generate():
            response = await litellm.acompletion(model=model, messages=messages, stream=True)
            async for chunk in response:
                delta = chunk.choices[0].delta.content or ""
                yield f"data: {json.dumps({'choices': [{'delta': {'content': delta}}]})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(generate(), media_type="text/event-stream")
    else:
        response = await litellm.acompletion(model=model, messages=messages)
        content = response.choices[0].message.content
        await log_turn(child_id, req.messages[-1].content, content)
        return {
            "choices": [{"message": {"role": "assistant", "content": content}}]
        }
