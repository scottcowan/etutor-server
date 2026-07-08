from fastapi import APIRouter
from services.profiles import list_children
from services.sessions import get_all_sessions

router = APIRouter()


@router.get("/dashboard")
async def dashboard():
    children = await list_children()
    sessions = await get_all_sessions()
    return {
        "children": [vars(c) for c in children],
        "sessions": {k: [vars(t) for t in v] for k, v in sessions.items()},
    }
