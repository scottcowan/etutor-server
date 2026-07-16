"""
Thin wrapper over db/crud.py for session and interaction event operations.

All functions accept an explicit AsyncSession parameter — callers inject via
Depends(get_db) in API route handlers (Plan 06-07).

Importing this module causes zero DB I/O and no side effects.
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import (
    log_turn as db_log_turn,
    get_session_history as db_get_session_history,
    create_session as db_create_session,
    get_session as db_get_session,
)


async def log_turn(
    child_id: str,
    question: str,
    answer: str,
    session: AsyncSession,
    topic: Optional[str] = None,
    session_id: Optional[str] = None,
    kc_id: Optional[str] = None,
    correct: Optional[bool] = None,
):
    """Thin wrapper over db.crud.log_turn — forwards all parameters including Phase 2 BKT fields."""
    return await db_log_turn(
        child_id, question, answer, session,
        topic=topic, session_id=session_id,
        kc_id=kc_id, correct=correct,
    )


async def get_session_history(child_id: str, session: AsyncSession, limit: int = 50):
    return await db_get_session_history(child_id, session, limit)


async def create_session(child_id: str, session: AsyncSession):
    return await db_create_session(child_id, session)


async def get_session(session_id: str, session: AsyncSession):
    return await db_get_session(session_id, session)
