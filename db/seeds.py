"""
Dev seed data for etutor-server.

Provides seed_dev_data(session) — an idempotent async function that upserts
two generic child profiles (KidA, KidB) using INSERT OR IGNORE so it can be
called on every startup without error.

Called from api/main.py lifespan handler when settings.env != 'production' (D-06, D-07).
"""
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChildProfileModel


async def seed_dev_data(session: AsyncSession) -> None:
    """Idempotent upsert of KidA and KidB dev profiles (D-08: generic identifiers only)."""
    profiles = [
        dict(
            id="child-kida",
            name="KidA",
            age=7,
            device_id="device-001",
            interests=["dinosaurs", "space", "Minecraft"],
            reading_level="grade 2",
            current_topic="prehistoric life",
            current_books=[],
            session_count=0,
            neurodivergence=[],
        ),
        dict(
            id="child-kidb",
            name="KidB",
            age=10,
            device_id="device-002",
            interests=["volcanoes", "ocean animals", "coding"],
            reading_level="grade 5",
            current_topic="earth science",
            current_books=[],
            session_count=0,
            neurodivergence=[],
        ),
    ]
    for profile in profiles:
        stmt = sqlite_insert(ChildProfileModel).values(**profile).prefix_with("OR IGNORE")
        await session.execute(stmt)
    await session.commit()
