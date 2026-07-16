"""
TDD tests for BKT + FSRS knowledge tracing service (KT-01, KT-02).

RED phase: imports will fail until services/knowledge_tracing.py is created.

Covers:
  - update_bkt() pure function: correct observation raises p_mastery
  - update_bkt() pure function: incorrect observation lowers p_mastery
  - update_bkt() output clamped to [0.0, 1.0]
  - update_bkt_for_session() batch-processes kc_id-tagged events in a session
  - update_bkt_for_session() returns {} when no kc_id-tagged events exist
  - update_fsrs_schedule() writes FSRS fields to mastery_state (KT-02)
  - fit_fsrs_params() cold-start guard and weights write (KT-02)
"""
import pytest

from services.knowledge_tracing import (
    update_bkt,
    update_bkt_for_session,
    update_fsrs_schedule,
    fit_fsrs_params,
    FSRS_MIN_REVIEWS_FOR_FIT,
)
from db.crud import (
    create_child,
    create_session,
    log_turn,
    create_or_get_mastery_state,
    get_child_fsrs_params,
)


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


# ---------------------------------------------------------------------------
# KT-02: update_fsrs_schedule() — FSRS scheduling integration tests
# ---------------------------------------------------------------------------

async def test_update_fsrs_schedule_correct(db_session):
    """After a correct review, FSRS fields are written to mastery_state."""
    child = await create_child(db_session, id="child-fsrs-01", name="Eve", age=10)

    await update_fsrs_schedule(child.id, "kc-fractions", correct=True, db=db_session)

    ms = await create_or_get_mastery_state(child.id, "kc-fractions", db_session)

    # stability must be a positive float after first review
    assert ms.stability is not None
    assert ms.stability > 0.0

    # difficulty_d must be a positive float
    assert ms.difficulty_d is not None
    assert ms.difficulty_d > 0.0

    # card_state must be a non-empty string
    assert ms.card_state is not None
    assert ms.card_state in ("Learning", "Review", "Relearning")

    # next_review must be a UTC-aware datetime in the future
    from datetime import datetime, timezone
    assert ms.next_review is not None
    nr = ms.next_review
    if nr.tzinfo is None:
        nr = nr.replace(tzinfo=timezone.utc)
    assert nr > datetime.now(timezone.utc)


async def test_update_fsrs_schedule_incorrect_shorter_interval(db_session):
    """After Again rating (correct=False), next_review is closer than after Good (correct=True)."""
    from datetime import datetime, timezone

    child_good = await create_child(db_session, id="child-fsrs-02", name="Fred", age=10)
    child_again = await create_child(db_session, id="child-fsrs-03", name="Gina", age=10)

    now = datetime.now(timezone.utc)

    await update_fsrs_schedule(child_good.id, "kc-spelling", correct=True, db=db_session, review_datetime=now)
    await update_fsrs_schedule(child_again.id, "kc-spelling", correct=False, db=db_session, review_datetime=now)

    ms_good = await create_or_get_mastery_state(child_good.id, "kc-spelling", db_session)
    ms_again = await create_or_get_mastery_state(child_again.id, "kc-spelling", db_session)

    nr_good = ms_good.next_review
    nr_again = ms_again.next_review

    # Normalise timezone
    if nr_good.tzinfo is None:
        nr_good = nr_good.replace(tzinfo=timezone.utc)
    if nr_again.tzinfo is None:
        nr_again = nr_again.replace(tzinfo=timezone.utc)

    # Again should schedule sooner than Good (shorter interval)
    assert nr_again < nr_good


# ---------------------------------------------------------------------------
# KT-02: fit_fsrs_params() — cold-start guard and weights write
# ---------------------------------------------------------------------------

def test_fsrs_min_reviews_constant():
    """FSRS_MIN_REVIEWS_FOR_FIT is the expected integer 10."""
    assert FSRS_MIN_REVIEWS_FOR_FIT == 10


async def test_fit_fsrs_cold_start_guard_zero_events(db_session):
    """Given 0 rated events, fit_fsrs_params() returns without writing to child_fsrs_params."""
    child = await create_child(db_session, id="child-fit-01", name="Hal", age=9)

    await fit_fsrs_params(child.id, db_session)

    params = await get_child_fsrs_params(child.id, db_session)
    assert params is None


async def test_fit_fsrs_cold_start_guard_nine_events(db_session):
    """Given 9 rated events (below threshold), fit_fsrs_params() returns without writing."""
    child = await create_child(db_session, id="child-fit-02", name="Iris", age=10)

    for i in range(9):
        await log_turn(
            child.id,
            f"Question {i}",
            f"Answer {i}",
            db_session,
            kc_id="kc-reading",
            correct=(i % 2 == 0),
        )

    await fit_fsrs_params(child.id, db_session)

    params = await get_child_fsrs_params(child.id, db_session)
    assert params is None


async def test_fit_fsrs_writes_params_with_fifteen_events(db_session):
    """Given 15 rated events, fit_fsrs_params() writes a 21-float weights list."""
    from datetime import datetime, timezone, timedelta

    child = await create_child(db_session, id="child-fit-03", name="Jake", age=11)

    for i in range(15):
        await log_turn(
            child.id,
            f"Question {i}",
            f"Answer {i}",
            db_session,
            kc_id="kc-maths",
            correct=(i % 2 == 0),
        )

    await fit_fsrs_params(child.id, db_session)

    params = await get_child_fsrs_params(child.id, db_session)
    assert params is not None
    assert isinstance(params.weights, list)
    assert len(params.weights) == 21
    assert all(isinstance(w, float) for w in params.weights)


# ---------------------------------------------------------------------------
# KT-03: next_topics() — ranking and filtering (RED phase — will fail until
# next_topics and mastery_context_for_prompt are added to knowledge_tracing.py)
# ---------------------------------------------------------------------------

from services.knowledge_tracing import next_topics, mastery_context_for_prompt


async def test_next_topics_due_first(db_session):
    """Overdue KC appears before a KC with a future next_review."""
    from datetime import datetime, timezone, timedelta

    child = await create_child(db_session, id="child-kt03-01", name="Leah", age=6)
    now = datetime.now(timezone.utc)

    # KC-A: overdue (next_review = yesterday)
    ms_a = await create_or_get_mastery_state(child.id, "phonics_phase1", db_session)
    ms_a.p_mastery = 0.4
    ms_a.next_review = now - timedelta(days=1)
    await db_session.commit()

    # KC-B: future review (next_review = tomorrow)
    ms_b = await create_or_get_mastery_state(child.id, "counting_numbers", db_session)
    ms_b.p_mastery = 0.4
    ms_b.next_review = now + timedelta(days=1)
    await db_session.commit()

    result = await next_topics(child.id, db_session, limit=10)

    ids = [t.id for t in result]
    assert "phonics_phase1" in ids
    assert "counting_numbers" in ids
    assert ids.index("phonics_phase1") < ids.index("counting_numbers")


async def test_next_topics_bucket_ranking(db_session):
    """Fragile KC (p_mastery=0.3) ranked before in_progress KC (p_mastery=0.8) when both due."""
    from datetime import datetime, timezone, timedelta

    child = await create_child(db_session, id="child-kt03-02", name="Maya", age=6)
    now = datetime.now(timezone.utc)

    # KC-X: fragile (p_mastery=0.3), due today
    ms_x = await create_or_get_mastery_state(child.id, "phonics_phase1", db_session)
    ms_x.p_mastery = 0.3
    ms_x.next_review = now - timedelta(hours=1)
    await db_session.commit()

    # KC-Y: in_progress (p_mastery=0.8), due today
    ms_y = await create_or_get_mastery_state(child.id, "counting_numbers", db_session)
    ms_y.p_mastery = 0.8
    ms_y.next_review = now - timedelta(hours=1)
    await db_session.commit()

    result = await next_topics(child.id, db_session, limit=10)

    ids = [t.id for t in result]
    assert "phonics_phase1" in ids
    assert "counting_numbers" in ids
    assert ids.index("phonics_phase1") < ids.index("counting_numbers")


async def test_next_topics_excludes_solid_future(db_session):
    """Solid KC (p_mastery=0.97) with future next_review is excluded from results."""
    from datetime import datetime, timezone, timedelta

    child = await create_child(db_session, id="child-kt03-03", name="Nora", age=6)
    now = datetime.now(timezone.utc)

    # KC-Z: solid with future review — should be excluded
    ms_z = await create_or_get_mastery_state(child.id, "phonics_phase1", db_session)
    ms_z.p_mastery = 0.97
    ms_z.next_review = now + timedelta(days=7)
    await db_session.commit()

    result = await next_topics(child.id, db_session, limit=10)

    ids = [t.id for t in result]
    assert "phonics_phase1" not in ids


async def test_next_topics_no_mastery_row(db_session):
    """KC with no mastery_state row is treated as not_started and included (D-09)."""
    child = await create_child(db_session, id="child-kt03-04", name="Owen", age=6)

    # No mastery rows created — all KCs are "not started"
    result = await next_topics(child.id, db_session, limit=10)

    assert len(result) > 0
    ids = [t.id for t in result]
    # phonics_phase1 is in year_groups=[1] for age=6 (year 1)
    assert "phonics_phase1" in ids


async def test_next_topics_limit(db_session):
    """Result length is always <= limit."""
    child = await create_child(db_session, id="child-kt03-05", name="Petra", age=6)

    result = await next_topics(child.id, db_session, limit=3)

    assert len(result) <= 3


async def test_next_topics_returns_empty_for_unknown_child(db_session):
    """Unknown child_id returns empty list without raising."""
    result = await next_topics("nonexistent-child-id", db_session, limit=10)

    assert result == []


# ---------------------------------------------------------------------------
# KT-05: mastery_context_for_prompt() — shape and filtering tests
# ---------------------------------------------------------------------------

async def test_mastery_context_for_prompt_shape(db_session):
    """Result is list[dict] with 'name' and 'bucket' keys."""
    child = await create_child(db_session, id="child-mc-01", name="Quinn", age=6)

    result = await mastery_context_for_prompt(child.id, db_session, limit=5)

    assert isinstance(result, list)
    for item in result:
        assert isinstance(item, dict)
        assert "name" in item
        assert "bucket" in item
        assert isinstance(item["name"], str)
        assert isinstance(item["bucket"], str)


async def test_mastery_context_for_prompt_bucket_values(db_session):
    """All bucket values are one of: fragile, in_progress, not_started."""
    child = await create_child(db_session, id="child-mc-02", name="Rosa", age=6)

    result = await mastery_context_for_prompt(child.id, db_session, limit=5)

    valid_buckets = {"fragile", "in_progress", "not_started"}
    for item in result:
        assert item["bucket"] in valid_buckets, f"Unexpected bucket: {item['bucket']!r}"


async def test_mastery_context_no_solid(db_session):
    """'solid' bucket never appears in the returned list."""
    from datetime import datetime, timezone, timedelta

    child = await create_child(db_session, id="child-mc-03", name="Sam", age=6)
    now = datetime.now(timezone.utc)

    # Seed a solid KC — it should be filtered out
    ms = await create_or_get_mastery_state(child.id, "phonics_phase1", db_session)
    ms.p_mastery = 0.97
    ms.next_review = now + timedelta(days=7)
    await db_session.commit()

    result = await mastery_context_for_prompt(child.id, db_session, limit=5)

    for item in result:
        assert item["bucket"] != "solid", f"Solid KC leaked into mastery_context: {item}"


async def test_mastery_context_returns_empty_for_unknown_child(db_session):
    """Unknown child_id returns [] without raising."""
    result = await mastery_context_for_prompt("nonexistent-id", db_session, limit=5)

    assert result == []
