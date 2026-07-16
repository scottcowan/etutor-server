"""
TDD tests for BKT knowledge tracing service (KT-01).

RED phase: imports will fail until services/knowledge_tracing.py is created.

Covers:
  - update_bkt() pure function: correct observation raises p_mastery
  - update_bkt() pure function: incorrect observation lowers p_mastery
  - update_bkt() output clamped to [0.0, 1.0]
  - update_bkt_for_session() batch-processes kc_id-tagged events in a session
  - update_bkt_for_session() returns {} when no kc_id-tagged events exist
"""
import pytest

from services.knowledge_tracing import update_bkt, update_bkt_for_session
from db.crud import create_child, create_session, log_turn, create_or_get_mastery_state


# ---------------------------------------------------------------------------
# update_bkt() — pure function unit tests
# ---------------------------------------------------------------------------

def test_bkt_correct_increases_mastery():
    """correct=True observation raises p_mastery from baseline."""
    result = update_bkt(
        p_mastery=0.1,
        p_learn=0.2,
        p_slip=0.1,
        p_guess=0.2,
        correct=True,
    )
    assert result > 0.1
    assert result <= 1.0


def test_bkt_incorrect_decreases_mastery():
    """correct=False observation does not raise p_mastery above the given value."""
    result = update_bkt(
        p_mastery=0.5,
        p_learn=0.2,
        p_slip=0.1,
        p_guess=0.2,
        correct=False,
    )
    assert result < 0.5


def test_bkt_near_certain_correct_stays_high():
    """Near-certain mastery stays near 1.0 after a correct observation."""
    result = update_bkt(
        p_mastery=0.99,
        p_learn=0.2,
        p_slip=0.1,
        p_guess=0.2,
        correct=True,
    )
    assert result >= 0.95
    assert result <= 1.0


def test_bkt_near_zero_incorrect_stays_low():
    """Near-zero mastery does not spike to high values after an incorrect observation.

    With p_mastery=0.01 and correct=False, the BKT posterior is ~0 but the
    forward transition step adds approximately p_learn (0.2), so the output
    is ~0.2 — not a spike. Threshold is set to 0.3 to guard against genuine
    spurious increases while tolerating the p_learn floor.
    """
    result = update_bkt(
        p_mastery=0.01,
        p_learn=0.2,
        p_slip=0.1,
        p_guess=0.2,
        correct=False,
    )
    assert result < 0.3  # does not spike; p_learn floor ≈ 0.2 is expected


def test_bkt_output_clamped_to_unit_interval():
    """Output is always in [0.0, 1.0] for any valid inputs."""
    for correct in (True, False):
        for p_mastery in (0.0, 0.5, 1.0):
            result = update_bkt(
                p_mastery=p_mastery,
                p_learn=0.2,
                p_slip=0.1,
                p_guess=0.2,
                correct=correct,
            )
            assert 0.0 <= result <= 1.0, f"Out of range: {result} for p_mastery={p_mastery}, correct={correct}"


# ---------------------------------------------------------------------------
# update_bkt_for_session() — async integration tests
# ---------------------------------------------------------------------------

async def test_update_bkt_for_session_raises_mastery(db_session):
    """Two correct events for a KC in one session raise p_mastery above the default 0.1."""
    child = await create_child(db_session, id="child-bkt-01", name="Alice", age=9)
    session_row = await create_session(child.id, db_session)

    # Log two correct events for kc-fractions
    await log_turn(
        child.id,
        "What is 1/2 + 1/4?",
        "3/4",
        db_session,
        session_id=session_row.id,
        kc_id="kc-fractions",
        correct=True,
    )
    await log_turn(
        child.id,
        "Simplify 4/8.",
        "1/2",
        db_session,
        session_id=session_row.id,
        kc_id="kc-fractions",
        correct=True,
    )

    result = await update_bkt_for_session(session_row.id, db_session)

    assert "kc-fractions" in result
    assert result["kc-fractions"] > 0.1


async def test_update_bkt_for_session_empty_returns_empty_dict(db_session):
    """Session with no kc_id-tagged events returns {} without raising."""
    child = await create_child(db_session, id="child-bkt-02", name="Bob", age=10)
    session_row = await create_session(child.id, db_session)

    # Log a turn WITHOUT kc_id
    await log_turn(
        child.id,
        "Tell me about fractions.",
        "A fraction has numerator and denominator.",
        db_session,
        session_id=session_row.id,
        kc_id=None,
        correct=None,
    )

    result = await update_bkt_for_session(session_row.id, db_session)

    assert result == {}


async def test_update_bkt_for_session_returns_dict(db_session):
    """Return value is a dict mapping kc_id to the new float p_mastery."""
    child = await create_child(db_session, id="child-bkt-03", name="Carol", age=8)
    session_row = await create_session(child.id, db_session)

    await log_turn(
        child.id,
        "What sound does 'ph' make?",
        "/f/",
        db_session,
        session_id=session_row.id,
        kc_id="kc-phonics-ph",
        correct=True,
    )

    result = await update_bkt_for_session(session_row.id, db_session)

    assert isinstance(result, dict)
    assert "kc-phonics-ph" in result
    assert isinstance(result["kc-phonics-ph"], float)


async def test_update_bkt_for_session_persists_to_db(db_session):
    """update_bkt_for_session writes the new p_mastery back to mastery_state."""
    child = await create_child(db_session, id="child-bkt-04", name="Dan", age=11)
    session_row = await create_session(child.id, db_session)

    await log_turn(
        child.id,
        "What is 7 x 8?",
        "56",
        db_session,
        session_id=session_row.id,
        kc_id="kc-times-tables",
        correct=True,
    )

    result = await update_bkt_for_session(session_row.id, db_session)

    # Re-fetch from DB and confirm the value matches what was returned
    ms = await create_or_get_mastery_state(child.id, "kc-times-tables", db_session)
    assert ms.p_mastery == pytest.approx(result["kc-times-tables"])
    assert ms.p_mastery > 0.1
