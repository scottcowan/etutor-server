from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from services.profiles import list_children

router = APIRouter()


@router.get("/dashboard")
async def dashboard(session: AsyncSession = Depends(get_db)):
    children = await list_children(session)
    return {
        "children": [
            {
                "id": c.id, "name": c.name, "age": c.age,
                "device_id": c.device_id, "interests": c.interests,
                "reading_level": c.reading_level, "current_topic": c.current_topic,
                "current_books": c.current_books, "session_count": c.session_count,
                "neurodivergence": c.neurodivergence,
            }
            for c in children
        ],
        "sessions": {},  # Phase 1: session replay deferred to Phase 4
    }
