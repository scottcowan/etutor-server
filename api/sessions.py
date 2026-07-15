from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from services.sessions import get_session_history

router = APIRouter()


@router.get("/sessions/{child_id}")
async def get_sessions(
    child_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
):
    turns = await get_session_history(child_id, session, limit)
    return {
        "child_id": child_id,
        "turns": [
            {
                "id": t.id,
                "child_id": t.child_id,
                "session_id": t.session_id,
                "question": t.question,
                "answer": t.answer,
                "topic": t.topic,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            }
            for t in turns
        ],
    }
