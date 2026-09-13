"""
TDD tests for Phase 3 CRUD data layer (03-01).

Covers:
  - get_24hr_history: time-window filtering, DESC order, empty case
  - get_turns_by_session_id: session scoping, ASC order
  - get_most_recent_ended_session: filters by ended_at, returns None when absent

Uses direct model insertion with explicit timestamps for time-sensitive tests.
"""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import pytest

from db.crud import (
    create_child,
    create_session,
    get_24hr_history,
    get_most_recent_ended_session,
    get_turns_by_session_id,
    log_turn,
)
from db.models import InteractionEventModel, SessionModel


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _event(child_id: str, session_id: Optional[str], offset_hours: float) -> InteractionEventModel:
    """Build an InteractionEventModel with an explicit timestamp offset from now."""
    return InteractionEventModel(
        id=str(uuid.uuid4()),
        child_id=child_id,
        session_id=session_id,
        question="Q",
        answer="A",
        timestamp=_now() - timedelta(hours=offset_hours),
    )


# ---------------------------------------------------------------------------
# get_24hr_history
# ---------------------------------------------------------------------------


async def test_get_24hr_history_excludes_old_events(db_session):
    """Events older than 24 hours are excluded; event within 24 hours is returned."""
    await create_child(db_session, id="child-si-01", name="Alice", age=8)

    # Insert old event (25h ago) directly to control timestamp
    old_event = _event("child-si-01", None, offset_hours=25)
    recent_event = _event("child-si-01", None, offset_hours=1)
    db_session.add(old_event)
    db_session.add(recent_event)
    await db_session.commit()

    result = await get_24hr_history("child-si-01", db_session)

    assert len(result) == 1
    assert result[0].child_id == "child-si-01"
    # The returned event should be the recent one
    assert abs((result[0].timestamp - recent_event.timestamp).total_seconds()) < 5


async def test_get_24hr_history_returns_desc_order(db_session):
    """get_24hr_history returns events in DESC timestamp order."""
    await create_child(db_session, id="child-si-02", name="Bob", age=9)

    # Insert three events with varying timestamps (not in chronological insert order)
    e3h = _event("child-si-02", None, offset_hours=3)
    e6h = _event("child-si-02", None, offset_hours=6)
    e1h = _event("child-si-02", None, offset_hours=1)
    db_session.add(e3h)
    db_session.add(e6h)
    db_session.add(e1h)
    await db_session.commit()

    result = await get_24hr_history("child-si-02", db_session)

    assert len(result) == 3
    assert result[0].timestamp > result[1].timestamp > result[2].timestamp


async def test_get_24hr_history_empty_for_no_events(db_session):
    """get_24hr_history returns [] when no events exist for the child."""
    await create_child(db_session, id="child-si-03", name="Carol", age=10)

    result = await get_24hr_history("child-si-03", db_session)

    assert result == []


# ---------------------------------------------------------------------------
# get_turns_by_session_id
# ---------------------------------------------------------------------------


async def test_get_turns_by_session_id_scoped(db_session):
    """get_turns_by_session_id returns only events for the given session_id."""
    await create_child(db_session, id="child-si-04", name="Dan", age=11)
    session_a = await create_session("child-si-04", db_session)
    session_b = await create_session("child-si-04", db_session)

    await log_turn("child-si-04", "Q1", "A1", db_session, session_id=session_a.id)
    await log_turn("child-si-04", "Q2", "A2", db_session, session_id=session_a.id)
    await log_turn("child-si-04", "Q3", "A3", db_session, session_id=session_b.id)

    result = await get_turns_by_session_id(session_a.id, db_session)

    assert len(result) == 2
    assert all(e.session_id == session_a.id for e in result)


async def test_get_turns_by_session_id_asc_order(db_session):
    """get_turns_by_session_id returns events in ASC timestamp order."""
    await create_child(db_session, id="child-si-05", name="Eve", age=9)
    session = await create_session("child-si-05", db_session)

    # Insert with explicit timestamps to ensure order is deterministic
    e5m = _event("child-si-05", session.id, offset_hours=5 / 60)
    e2m = _event("child-si-05", session.id, offset_hours=2 / 60)
    db_session.add(e5m)
    db_session.add(e2m)
    await db_session.commit()

    result = await get_turns_by_session_id(session.id, db_session)

    assert len(result) == 2
    assert result[0].timestamp < result[1].timestamp


# ---------------------------------------------------------------------------
# get_most_recent_ended_session
# ---------------------------------------------------------------------------


async def test_get_most_recent_ended_session_returns_ended(db_session):
    """get_most_recent_ended_session returns the most recent ended session, ignoring open ones."""
    await create_child(db_session, id="child-si-06", name="Frank", age=10)

    session_a = SessionModel(
        id=str(uuid.uuid4()),
        child_id="child-si-06",
        ended_at=_now() - timedelta(hours=2),
    )
    session_b = SessionModel(
        id=str(uuid.uuid4()),
        child_id="child-si-06",
        ended_at=None,  # open session
    )
    db_session.add(session_a)
    db_session.add(session_b)
    await db_session.commit()

    result = await get_most_recent_ended_session("child-si-06", db_session)

    assert result is not None
    assert result.id == session_a.id


async def test_get_most_recent_ended_session_returns_none_when_no_ended(db_session):
    """get_most_recent_ended_session returns None when no ended sessions exist."""
    await create_child(db_session, id="child-si-07", name="Grace", age=7)

    open_session = SessionModel(
        id=str(uuid.uuid4()),
        child_id="child-si-07",
        ended_at=None,
    )
    db_session.add(open_session)
    await db_session.commit()

    result = await get_most_recent_ended_session("child-si-07", db_session)

    assert result is None
