from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from services.profiles import get_child_by_device_id
from services.recommender import build_recommendation_message

router = APIRouter()


@router.get("/devices/{device_id}/sync")
async def sync_device(device_id: str, session: AsyncSession = Depends(get_db)):
    child = await get_child_by_device_id(device_id, session)
    if not child:
        return {"status": "unknown_device", "packages": []}

    recommendation = await build_recommendation_message(child)

    return {
        "status": "ok",
        "child_id": child.id,
        "child_name": child.name,
        "child_age": child.age,
        "interests": child.interests,
        "current_topic": child.current_topic,
        "reading_level": child.reading_level,
        "current_books": child.current_books,
        "book_recommendation": recommendation,
        "packages": [],  # content packages — populated when learning plan system is built
    }
