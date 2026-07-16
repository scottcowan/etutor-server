"""
CRUD functions for etutor-server (DB-02, DB-03, DB-04, DB-05).

All functions are async and accept an explicit AsyncSession parameter.
Parameter order follows D-03 / PATTERNS.md convention: (id_or_key, session)
so Plan 05's thin service wrapper can delegate without reordering.

Security note (T-1-04): all WHERE clauses use SQLAlchemy ORM select() with
typed column comparisons — parameterised, never string-interpolated.

Security note (T-1-07): get_session_history is child_id-scoped — no
cross-child data access is possible via these CRUD functions.

Security note (T-1-08): update_mastery_state accepts **fields via setattr;
SQLAlchemy will raise AttributeError on unknown column names. Internal-only
callers in Phase 1.
"""
import uuid
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChildFSRSParamsModel, ChildProfileModel, InteractionEventModel, MasteryStateModel, SessionModel


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


# ---------------------------------------------------------------------------
# Session CRUD (DB-03)
# ---------------------------------------------------------------------------

async def create_session(child_id: str, session: AsyncSession) -> SessionModel:
    """Insert a new tutoring session row and return the refreshed model."""
    model = SessionModel(id=str(uuid.uuid4()), child_id=child_id)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def get_session(session_id: str, session: AsyncSession) -> Optional[SessionModel]:
    """Return the SessionModel for session_id, or None if not found."""
    result = await session.execute(
        select(SessionModel).where(SessionModel.id == session_id)
    )
    return result.scalar_one_or_none()


# ---------------------------------------------------------------------------
# InteractionEvent CRUD (DB-04)
# ---------------------------------------------------------------------------

async def log_turn(
    child_id: str,
    question: str,
    answer: str,
    session: AsyncSession,
    *,
    topic: Optional[str] = None,
    session_id: Optional[str] = None,
    kc_id: Optional[str] = None,
    correct: Optional[bool] = None,
) -> InteractionEventModel:
    """Insert a new InteractionEvent (turn) row and return the refreshed model.

    topic, session_id, kc_id, and correct are keyword-only to prevent positional-argument
    breakage when services/sessions.py wraps this function.

    kc_id and correct are Phase 2 BKT parameters (KT-04). Pass kc_id to associate the
    turn with a knowledge component; pass correct=True/False to enable BKT batch update.
    Both default to None — existing callers are unaffected (T-2-01: parameterised INSERT).
    """
    model = InteractionEventModel(
        id=str(uuid.uuid4()),
        child_id=child_id,
        question=question,
        answer=answer,
        topic=topic,
        session_id=session_id,
        kc_id=kc_id,
        correct=correct,
    )
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def get_session_history(
    child_id: str,
    session: AsyncSession,
    limit: int = 50,
) -> list[InteractionEventModel]:
    """Return the most recent `limit` interaction events for child_id, ordered ASC by timestamp.

    Fetches the most recent `limit` rows using SQL ORDER BY DESC LIMIT, then
    reverses to return ASC order for callers (T-1-07: child_id-scoped).
    """
    result = await session.execute(
        select(InteractionEventModel)
        .where(InteractionEventModel.child_id == child_id)
        .order_by(InteractionEventModel.timestamp.desc())
        .limit(limit)
    )
    rows = list(result.scalars().all())
    return list(reversed(rows))  # restore ASC order for callers


# ---------------------------------------------------------------------------
# MasteryState CRUD (DB-05)
# ---------------------------------------------------------------------------

async def create_or_get_mastery_state(
    child_id: str,
    kc_id: str,
    session: AsyncSession,
) -> MasteryStateModel:
    """Return existing MasteryState row, or create one with BKT defaults if absent."""
    existing = await session.get(MasteryStateModel, (child_id, kc_id))
    if existing:
        return existing
    model = MasteryStateModel(child_id=child_id, kc_id=kc_id)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def update_mastery_state(
    child_id: str,
    kc_id: str,
    session: AsyncSession,
    **fields,
) -> None:
    """Update BKT/FSRS fields on an existing MasteryState row.

    Raises ValueError if the row does not exist.
    SQLAlchemy will raise AttributeError on unknown column names — no validation needed
    for Phase 1 internal callers (T-1-08).
    """
    model = await session.get(MasteryStateModel, (child_id, kc_id))
    if model is None:
        raise ValueError(f"MasteryState not found for ({child_id}, {kc_id})")
    for k, v in fields.items():
        setattr(model, k, v)
    model.updated_at = datetime.now(timezone.utc)
    await session.commit()


# ---------------------------------------------------------------------------
# ChildFSRSParams CRUD (D-06)
# ---------------------------------------------------------------------------

async def get_child_fsrs_params(
    child_id: str,
    session: AsyncSession,
) -> Optional[ChildFSRSParamsModel]:
    """Return ChildFSRSParamsModel for child_id, or None if not found (cold-start)."""
    return await session.get(ChildFSRSParamsModel, child_id)


async def upsert_child_fsrs_params(
    child_id: str,
    weights: list,
    session: AsyncSession,
) -> None:
    """Insert or update the per-child FSRS-5 weight vector.

    Uses session.get() PK lookup (parameterised) — no string-interpolation risk (T-2-02).
    Follows the get-or-create pattern from create_or_get_mastery_state().
    """
    existing = await session.get(ChildFSRSParamsModel, child_id)
    if existing:
        existing.weights = weights
        existing.updated_at = datetime.now(timezone.utc)
    else:
        session.add(ChildFSRSParamsModel(
            child_id=child_id,
            weights=weights,
            updated_at=datetime.now(timezone.utc),
        ))
    await session.commit()
