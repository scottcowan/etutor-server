"""
Tests for Session CRUD functions (DB-03).

Covers:
  - create_session / get_session round-trip
  - get_session with unknown ID returns None
  - FK constraint: child_id must reference an existing ChildProfile
"""
import pytest
from sqlalchemy.exc import IntegrityError

from db.crud import create_child, create_session, get_session


async def test_create_and_get_session(db_session):
    """create_session returns SessionModel with id (UUID4 str), started_at datetime, ended_at None."""
    await create_child(db_session, id="child-a1", name="Alice", age=9)
    session_row = await create_session("child-a1", db_session)

    assert session_row.id is not None
    assert isinstance(session_row.id, str)
    assert len(session_row.id) == 36  # UUID4 hyphenated
    assert session_row.child_id == "child-a1"
    assert session_row.started_at is not None
    assert session_row.ended_at is None

    fetched = await get_session(session_row.id, db_session)
    assert fetched is not None
    assert fetched.id == session_row.id


async def test_get_nonexistent_session_returns_none(db_session):
    """get_session with an unknown ID returns None."""
    result = await get_session("no-such-id", db_session)
    assert result is None


async def test_session_foreign_key(db_session):
    """create_session with a child_id not in child_profiles raises IntegrityError (FK violation)."""
    # SQLite enforces FK constraints only with PRAGMA foreign_keys = ON
    from sqlalchemy import text
    await db_session.execute(text("PRAGMA foreign_keys = ON"))

    with pytest.raises(IntegrityError):
        await create_session("child-kida", db_session)
