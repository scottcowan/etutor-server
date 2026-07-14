"""
Tests for InteractionEvent CRUD functions (DB-04).

Covers:
  - log_turn basic round-trip
  - log_turn with optional topic
  - log_turn with optional session_id
  - get_session_history ordering and limit (most-recent-N semantics)
  - get_session_history for unknown child returns []
  - DB-04 nullable scaffold columns (schema-shape test, no insert)
"""
from datetime import datetime

import pytest
from sqlalchemy import inspect as sa_inspect

from db.crud import create_child, create_session, get_session_history, log_turn
from db.models import InteractionEventModel


async def test_log_turn_creates_row(db_session):
    """log_turn returns InteractionEventModel with correct child_id, question, answer, datetime timestamp."""
    await create_child(db_session, id="child-b1", name="Bob", age=8)
    event = await log_turn("child-b1", "What is gravity?", "A force.", db_session)

    assert event.id is not None
    assert isinstance(event.id, str)
    assert event.child_id == "child-b1"
    assert event.question == "What is gravity?"
    assert event.answer == "A force."
    assert isinstance(event.timestamp, datetime)
    assert event.topic is None


async def test_log_turn_with_topic(db_session):
    """log_turn with topic keyword arg stores the topic field."""
    await create_child(db_session, id="child-b2", name="Cara", age=10)
    event = await log_turn("child-b2", "Why do volcanoes erupt?", "Magma pressure.", db_session, topic="volcanoes")

    assert event.topic == "volcanoes"


async def test_log_turn_with_session_id(db_session):
    """log_turn with session_id keyword arg stores the session_id field."""
    await create_child(db_session, id="child-b3", name="Dan", age=11)
    session_row = await create_session("child-b3", db_session)
    event = await log_turn("child-b3", "How big is the Sun?", "Very big.", db_session, session_id=session_row.id)

    assert event.session_id == session_row.id


async def test_get_session_history_returns_turns(db_session):
    """get_session_history returns all turns for a child in timestamp-ascending order."""
    await create_child(db_session, id="child-b4", name="Eve", age=9)
    await log_turn("child-b4", "Q1", "A1", db_session)
    await log_turn("child-b4", "Q2", "A2", db_session)
    await log_turn("child-b4", "Q3", "A3", db_session)

    history = await get_session_history("child-b4", db_session)
    assert len(history) == 3
    # Check ascending timestamp order
    timestamps = [e.timestamp for e in history]
    assert timestamps == sorted(timestamps)


async def test_get_session_history_limit(db_session):
    """get_session_history with limit=2 returns the 2 most recent turns."""
    await create_child(db_session, id="child-b5", name="Frank", age=10)
    await log_turn("child-b5", "Q1", "A1", db_session)
    await log_turn("child-b5", "Q2", "A2", db_session)
    await log_turn("child-b5", "Q3", "A3", db_session)
    await log_turn("child-b5", "Q4", "A4", db_session)
    await log_turn("child-b5", "Q5", "A5", db_session)

    history = await get_session_history("child-b5", db_session, limit=2)
    assert len(history) == 2
    # The 2 most recent = Q4 and Q5
    questions = [e.question for e in history]
    assert "Q4" in questions
    assert "Q5" in questions


async def test_get_session_history_empty(db_session):
    """get_session_history for an unknown child_id returns an empty list."""
    history = await get_session_history("unknown-child", db_session)
    assert history == []


async def test_interaction_event_db04_columns(db_session):
    """Schema-shape test: InteractionEventModel table has the 4 DB-04 nullable scaffold columns."""
    mapper = sa_inspect(InteractionEventModel)
    col_map = {col.key: col for col in mapper.mapper.column_attrs}

    # kc_id: String, nullable
    assert "kc_id" in col_map
    kc_id_col = InteractionEventModel.__table__.c["kc_id"]
    assert kc_id_col.nullable is True

    # correct: Boolean, nullable
    assert "correct" in col_map
    correct_col = InteractionEventModel.__table__.c["correct"]
    assert correct_col.nullable is True

    # response_ms: Integer, nullable
    assert "response_ms" in col_map
    response_ms_col = InteractionEventModel.__table__.c["response_ms"]
    assert response_ms_col.nullable is True

    # hint_used: Boolean, nullable
    assert "hint_used" in col_map
    hint_used_col = InteractionEventModel.__table__.c["hint_used"]
    assert hint_used_col.nullable is True
