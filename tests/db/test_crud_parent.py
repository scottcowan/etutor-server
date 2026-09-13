"""
TDD tests for parent-dashboard CRUD functions (04-02).

Tests cover:
  - update_child_profile: field-patch, partial update, not-found
  - create_alert: persist and return
  - get_alerts_for_child: 30-day window, DESC ordering
  - get_all_mastery_for_child: dict keyed by kc_id
  - run_frustration_tally: frustrated alert created when hint_count > 3 on same kc_id
  - log_turn safety_flag: set on keyword match, not set on clean text
  - log_turn sensitive alert: AlertModel row created when safety_flag=True

All tests use the shared db_session fixture from conftest.py.
"""
import pytest
from db.crud import (
    create_alert,
    create_child,
    create_session,
    get_alerts_for_child,
    get_all_mastery_for_child,
    log_turn,
    run_frustration_tally,
    update_child_profile,
)
from db.crud import create_or_get_mastery_state
from db.models import AlertModel, InteractionEventModel


# ---------------------------------------------------------------------------
# update_child_profile tests
# ---------------------------------------------------------------------------

async def test_update_child_profile_name(db_session):
    """update_child_profile updates the name field and returns the updated child."""
    await create_child(db_session, id="child-p1", name="Alice", age=8)
    updated = await update_child_profile("child-p1", db_session, name="Alicia")
    assert updated is not None
    assert updated.name == "Alicia"


async def test_update_child_profile_partial(db_session):
    """update_child_profile with reading_level only — other fields remain unchanged."""
    await create_child(
        db_session,
        id="child-p2",
        name="Bob",
        age=10,
        reading_level="beginner",
        interests=["math"],
    )
    updated = await update_child_profile("child-p2", db_session, reading_level="fluent")
    assert updated is not None
    assert updated.reading_level == "fluent"
    assert updated.name == "Bob"
    assert updated.age == 10
    assert updated.interests == ["math"]


async def test_update_child_profile_not_found(db_session):
    """update_child_profile returns None for an unknown child_id."""
    result = await update_child_profile("nonexistent-child", db_session, name="Ghost")
    assert result is None


# ---------------------------------------------------------------------------
# create_alert tests
# ---------------------------------------------------------------------------

async def test_create_alert_persists(db_session):
    """create_alert persists a row and returns it with correct fields."""
    await create_child(db_session, id="child-a1", name="Alice", age=8)
    alert = await create_alert("child-a1", "frustrated", db_session)
    assert alert is not None
    assert alert.child_id == "child-a1"
    assert alert.alert_type == "frustrated"
    assert alert.id is not None
    assert alert.triggered_at is not None


# ---------------------------------------------------------------------------
# get_alerts_for_child tests
# ---------------------------------------------------------------------------

async def test_get_alerts_for_child_returns_30_day_window(db_session):
    """Alerts older than 30 days are excluded; alerts within 30 days are included."""
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import text

    await create_child(db_session, id="child-w1", name="Alice", age=8)

    # Insert an alert within the window (1 day ago)
    recent = AlertModel(
        id="alert-recent",
        child_id="child-w1",
        alert_type="frustrated",
        triggered_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(recent)

    # Insert an alert outside the window (31 days ago)
    old = AlertModel(
        id="alert-old",
        child_id="child-w1",
        alert_type="frustrated",
        triggered_at=datetime.now(timezone.utc) - timedelta(days=31),
    )
    db_session.add(old)
    await db_session.commit()

    results = await get_alerts_for_child("child-w1", db_session)
    ids = [r.id for r in results]
    assert "alert-recent" in ids
    assert "alert-old" not in ids


async def test_get_alerts_ordered_desc(db_session):
    """get_alerts_for_child returns alerts most-recent-first."""
    from datetime import datetime, timedelta, timezone

    await create_child(db_session, id="child-ord", name="Alice", age=8)

    older = AlertModel(
        id="alert-older",
        child_id="child-ord",
        alert_type="frustrated",
        triggered_at=datetime.now(timezone.utc) - timedelta(days=2),
    )
    newer = AlertModel(
        id="alert-newer",
        child_id="child-ord",
        alert_type="new-interest",
        triggered_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    db_session.add(older)
    db_session.add(newer)
    await db_session.commit()

    results = await get_alerts_for_child("child-ord", db_session)
    assert len(results) >= 2
    assert results[0].id == "alert-newer"
    assert results[1].id == "alert-older"


# ---------------------------------------------------------------------------
# get_all_mastery_for_child tests
# ---------------------------------------------------------------------------

async def test_get_all_mastery_for_child_returns_dict(db_session):
    """get_all_mastery_for_child returns a dict keyed by kc_id with all mastery rows."""
    await create_child(db_session, id="child-m1", name="Alice", age=8)
    await create_or_get_mastery_state("child-m1", "kc-001", db_session)
    await create_or_get_mastery_state("child-m1", "kc-002", db_session)

    mastery_dict = await get_all_mastery_for_child("child-m1", db_session)
    assert isinstance(mastery_dict, dict)
    assert "kc-001" in mastery_dict
    assert "kc-002" in mastery_dict
    assert mastery_dict["kc-001"].kc_id == "kc-001"
    assert mastery_dict["kc-002"].kc_id == "kc-002"


# ---------------------------------------------------------------------------
# Frustration tally tests
# ---------------------------------------------------------------------------

async def test_frustration_alert_created_at_end_session(db_session):
    """4 hint_used=True events on same kc_id → AlertModel row with alert_type='frustrated'."""
    await create_child(db_session, id="child-f1", name="Alice", age=8)
    session_row = await create_session("child-f1", db_session)

    # Insert 4 interaction events with hint_used=True on kc-fr1
    for i in range(4):
        event = InteractionEventModel(
            id=f"evt-{i}",
            child_id="child-f1",
            session_id=session_row.id,
            question="hint question",
            answer="some answer",
            kc_id="kc-fr1",
            hint_used=True,
        )
        db_session.add(event)
    await db_session.commit()

    await run_frustration_tally(session_row.id, "child-f1", db_session)

    alerts = await get_alerts_for_child("child-f1", db_session)
    alert_types = [a.alert_type for a in alerts]
    assert "frustrated" in alert_types
    frustrated_alerts = [a for a in alerts if a.alert_type == "frustrated"]
    assert len(frustrated_alerts) == 1
    assert frustrated_alerts[0].kc_id == "kc-fr1"


# ---------------------------------------------------------------------------
# Safety flag tests
# ---------------------------------------------------------------------------

async def test_safety_flag_set_on_keyword_match(db_session):
    """log_turn with a question containing 'suicide' sets safety_flag=True on the event row."""
    await create_child(db_session, id="child-sf1", name="Alice", age=8)
    session_row = await create_session("child-sf1", db_session)

    event = await log_turn(
        "child-sf1",
        "I want to suicide",
        "some answer",
        db_session,
        session_id=session_row.id,
    )
    assert event.safety_flag is True


async def test_safety_flag_not_set_on_clean_text(db_session):
    """log_turn with clean question text does not set safety_flag."""
    await create_child(db_session, id="child-sf2", name="Bob", age=9)
    session_row = await create_session("child-sf2", db_session)

    event = await log_turn(
        "child-sf2",
        "what is photosynthesis",
        "some answer",
        db_session,
        session_id=session_row.id,
    )
    assert not event.safety_flag


async def test_sensitive_alert_created_on_keyword_match(db_session):
    """log_turn with a flagged keyword creates an AlertModel row with alert_type='sensitive'."""
    await create_child(db_session, id="child-sf3", name="Carol", age=10)
    session_row = await create_session("child-sf3", db_session)

    await log_turn(
        "child-sf3",
        "I want to hurt myself",
        "some answer",
        db_session,
        session_id=session_row.id,
    )

    alerts = await get_alerts_for_child("child-sf3", db_session)
    sensitive = [a for a in alerts if a.alert_type == "sensitive"]
    assert len(sensitive) == 1
    assert sensitive[0].child_id == "child-sf3"
