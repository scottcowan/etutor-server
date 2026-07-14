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
                "id": c.id,
                "name": c.name,
                "age": c.age,
                "device_id": c.device_id,
                "reading_level": c.reading_level,
                "interests": c.interests,
                "current_topic": c.current_topic,
                "session_count": c.session_count,
            }
            for c in children
        ],
        "sessions": {},
    }
