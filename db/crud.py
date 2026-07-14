"""
ChildProfile CRUD functions for etutor-server (DB-02).

All functions are async and accept an explicit AsyncSession parameter.
Parameter order follows D-03 / PATTERNS.md convention: (id_or_key, session)
so Plan 05's thin service wrapper can delegate without reordering.

Security note (T-1-04): all WHERE clauses use SQLAlchemy ORM select() with
typed column comparisons — parameterised, never string-interpolated.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChildProfileModel


async def create_child(
    session: AsyncSession,
    *,
    id: str,
    name: str,
    age: int,
    device_id: Optional[str] = None,
    interests: Optional[list] = None,
    reading_level: str = "age-appropriate",
    current_topic: Optional[str] = None,
    current_books: Optional[list] = None,
    session_count: int = 0,
    neurodivergence: Optional[list] = None,
) -> ChildProfileModel:
    """Insert a new ChildProfile row and return the refreshed model."""
    child = ChildProfileModel(
        id=id,
        name=name,
        age=age,
        device_id=device_id,
        interests=interests if interests is not None else [],
        reading_level=reading_level,
        current_topic=current_topic,
        current_books=current_books if current_books is not None else [],
        session_count=session_count,
        neurodivergence=neurodivergence if neurodivergence is not None else [],
    )
    session.add(child)
    await session.commit()
    await session.refresh(child)
    return child


async def get_child_by_id(
    child_id: str, session: AsyncSession
) -> Optional[ChildProfileModel]:
    """Return the ChildProfile for child_id, or None if not found."""
    result = await session.execute(
        select(ChildProfileModel).where(ChildProfileModel.id == child_id)
    )
    return result.scalar_one_or_none()


async def get_child_by_device_id(
    device_id: str, session: AsyncSession
) -> Optional[ChildProfileModel]:
    """Return the ChildProfile for device_id, or None if not found."""
    result = await session.execute(
        select(ChildProfileModel).where(ChildProfileModel.device_id == device_id)
    )
    return result.scalar_one_or_none()


async def list_children(session: AsyncSession) -> list[ChildProfileModel]:
    """Return all ChildProfile rows."""
    result = await session.execute(select(ChildProfileModel))
    return list(result.scalars().all())


async def update_interests(
    child_id: str, new_interests: list, session: AsyncSession
) -> None:
    """Merge new_interests with the child's existing interests (set union) and commit."""
    child = await get_child_by_id(child_id, session)
    if child is None:
        return
    existing = set(child.interests or [])
    merged = list(existing | set(new_interests))
    child.interests = merged
    await session.commit()
