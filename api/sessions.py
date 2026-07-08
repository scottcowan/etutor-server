from fastapi import APIRouter
from services.sessions import get_session_history

router = APIRouter()


@router.get("/sessions/{child_id}")
async def get_sessions(child_id: str, limit: int = 50):
    turns = await get_session_history(child_id, limit)
    return {"child_id": child_id, "turns": [vars(t) for t in turns]}
