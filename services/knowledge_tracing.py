"""
Knowledge tracing service — BKT + FSRS (Phase 2).

KT-01: BKT closed-form updates
KT-02: FSRS scheduling fields
KT-03: next_topics() using mastery + FSRS schedule
KT-04: Post-session BKT batch update
KT-05: mastery_context_for_prompt() for prompt injection

Security note (T-2-03): session_id used in WHERE clause via SQLAlchemy ORM
parameterised select() — never string-interpolated.
Security note (T-2-05): child_id and kc_id never string-interpolated in any
update_fsrs_schedule or fit_fsrs_params select() call.
"""
from datetime import datetime, timezone
from typing import Optional

from fsrs import Card, Rating, ReviewLog, Scheduler, State
from fsrs import Optimizer

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import InteractionEventModel
from db.crud import (
    create_or_get_mastery_state,
    get_child_fsrs_params,
    update_mastery_state,
    upsert_child_fsrs_params,
)


# ---------------------------------------------------------------------------
# KT-02: FSRS constant
# ---------------------------------------------------------------------------

FSRS_MIN_REVIEWS_FOR_FIT = 10


# ---------------------------------------------------------------------------
# KT-01: BKT pure function
# ---------------------------------------------------------------------------

def update_bkt(
    p_mastery: float,
    p_learn: float,
    p_slip: float,
    p_guess: float,
    correct: bool,
) -> float:
    """
    Closed-form BKT posterior update (Corbett & Anderson 1994).

    Returns new p_mastery given one correct/incorrect observation.
    Output is clamped to [0.0, 1.0] to guard against floating-point drift.

    Parameters
    ----------
    p_mastery : float
        P(mastered | observations so far)
    p_learn : float
        P(transition to mastered in one opportunity)
    p_slip : float
        P(incorrect | mastered)
    p_guess : float
        P(correct | not mastered)
    correct : bool
        Whether the child's response was correct.
    """
    # Step 1: P(correct) for evidence weighting
    p_correct = p_mastery * (1.0 - p_slip) + (1.0 - p_mastery) * p_guess

    # Step 2: Posterior P(mastered | observation)
    if correct:
        # P(mastered | correct) = P(correct | mastered) * P(mastered) / P(correct)
        # Guard against zero denominator (degenerate parameters)
        if p_correct <= 0.0:
            p_mastered_given_obs = p_mastery
        else:
            p_mastered_given_obs = (p_mastery * (1.0 - p_slip)) / p_correct
    else:
        # P(mastered | incorrect) = P(incorrect | mastered) * P(mastered) / P(incorrect)
        p_incorrect = 1.0 - p_correct
        if p_incorrect <= 0.0:
            p_mastered_given_obs = p_mastery
        else:
            p_mastered_given_obs = (p_mastery * p_slip) / p_incorrect

    # Step 3: Forward transition — P(mastered at next opportunity)
    p_new = p_mastered_given_obs + (1.0 - p_mastered_given_obs) * p_learn

    # Clamp to valid probability range
    return max(0.0, min(1.0, p_new))


# ---------------------------------------------------------------------------
# KT-04: Batch BKT update for a session
# ---------------------------------------------------------------------------

async def update_bkt_for_session(
    session_id: str,
    db: AsyncSession,
) -> dict[str, float]:
    """
    KT-04: Batch BKT update for all interaction_events in a session.

    Fetches all events where session_id matches AND kc_id IS NOT NULL
    AND correct IS NOT NULL. Applies BKT update for each event in
    chronological order per KC. Writes updated p_mastery back to
    mastery_state via update_mastery_state().

    Security note (T-2-03): session_id is parameterised via SQLAlchemy ORM.

    Returns
    -------
    dict[str, float]
        {kc_id: new_p_mastery} for all KCs updated in the session.
        Returns {} if the session has no kc_id-tagged events.
    """
    # SELECT all events for this session with kc_id and correct set,
    # ordered by timestamp ASC to process events chronologically per KC.
    stmt = (
        select(InteractionEventModel)
        .where(InteractionEventModel.session_id == session_id)
        .where(InteractionEventModel.kc_id.is_not(None))
        .where(InteractionEventModel.correct.is_not(None))
        .order_by(InteractionEventModel.timestamp.asc())
    )
    result = await db.execute(stmt)
    events = result.scalars().all()

    if not events:
        return {}

    # Group events by kc_id — maintaining chronological order from the query
    events_by_kc: dict[str, list] = {}
    child_id: Optional[str] = None
    for event in events:
        if child_id is None:
            child_id = event.child_id
        events_by_kc.setdefault(event.kc_id, []).append(event)

    if child_id is None:
        return {}

    updates: dict[str, float] = {}

    for kc_id, kc_events in events_by_kc.items():
        # Load or create the mastery state row for this child × KC
        mastery = await create_or_get_mastery_state(child_id, kc_id, db)

        p_mastery = mastery.p_mastery
        p_learn = mastery.p_learn
        p_slip = mastery.p_slip
        p_guess = mastery.p_guess

        # Apply BKT update sequentially for each event in chronological order
        for event in kc_events:
            p_mastery = update_bkt(
                p_mastery=p_mastery,
                p_learn=p_learn,
                p_slip=p_slip,
                p_guess=p_guess,
                correct=event.correct,
            )

        # Persist the final p_mastery back to the DB
        await update_mastery_state(child_id, kc_id, db, p_mastery=p_mastery)
        updates[kc_id] = p_mastery

    return updates


# ---------------------------------------------------------------------------
# KT-02: FSRS scheduling
# ---------------------------------------------------------------------------

async def update_fsrs_schedule(
    child_id: str,
    kc_id: str,
    correct: bool,
    db: AsyncSession,
    review_datetime: Optional[datetime] = None,
) -> None:
    """
    KT-02: Update FSRS scheduling fields on a mastery_state row after a rated review.

    Writes stability, difficulty_d, card_state, and next_review to the mastery_state
    row identified by (child_id, kc_id). Creates the row if it does not exist.

    Security note (T-2-05): child_id and kc_id are never string-interpolated —
    all DB access goes through ORM parameterised calls.

    Parameters
    ----------
    child_id : str
        The child's identifier.
    kc_id : str
        The knowledge component identifier.
    correct : bool
        True → Rating.Good; False → Rating.Again.
    db : AsyncSession
        Database session.
    review_datetime : datetime, optional
        The datetime of the review. Defaults to datetime.now(timezone.utc).
    """
    # Load per-child FSRS weights; fall back to defaults on cold start
    params_row = await get_child_fsrs_params(child_id, db)
    if params_row is None:
        scheduler = Scheduler()
    else:
        scheduler = Scheduler(parameters=tuple(params_row.weights))

    # Load or create the mastery state row
    mastery = await create_or_get_mastery_state(child_id, kc_id, db)

    # Reconstruct Card from stored fields
    if mastery.stability is None:
        card = Card()
    else:
        card = Card()
        card.stability = mastery.stability
        card.difficulty = mastery.difficulty_d  # stored as difficulty_d, maps to card.difficulty
        if mastery.next_review is not None:
            nr = mastery.next_review
            if nr.tzinfo is None:
                nr = nr.replace(tzinfo=timezone.utc)
            card.due = nr
        if mastery.card_state:
            card.state = State[mastery.card_state]

    # Map correct → FSRS Rating (two-level mapping per RESEARCH.md)
    rating = Rating.Good if correct else Rating.Again

    # Perform the review
    now = review_datetime if review_datetime is not None else datetime.now(timezone.utc)
    card, _ = scheduler.review_card(card, rating, review_datetime=now)

    # Write FSRS fields back to mastery_state
    await update_mastery_state(
        child_id,
        kc_id,
        db,
        stability=card.stability,
        difficulty_d=card.difficulty,  # FSRS Card uses .difficulty; store as difficulty_d
        card_state=card.state.name,
        next_review=card.due,
    )


async def fit_fsrs_params(
    child_id: str,
    db: AsyncSession,
) -> None:
    """
    KT-02: Fit per-child FSRS-5 weights from all available rated interaction history.

    Cold-start guard: returns without writing if fewer than FSRS_MIN_REVIEWS_FOR_FIT
    rated events exist for the child.

    Security note (T-2-05): child_id is parameterised via SQLAlchemy ORM — never
    string-interpolated.

    Parameters
    ----------
    child_id : str
        The child's identifier.
    db : AsyncSession
        Database session.
    """
    # Fetch all rated events for this child, ordered chronologically
    stmt = (
        select(InteractionEventModel)
        .where(InteractionEventModel.child_id == child_id)
        .where(InteractionEventModel.correct.is_not(None))
        .order_by(InteractionEventModel.timestamp.asc())
    )
    result = await db.execute(stmt)
    events = list(result.scalars().all())

    # Cold-start guard
    if len(events) < FSRS_MIN_REVIEWS_FOR_FIT:
        return

    # Build ReviewLog list from interaction events
    review_logs: list[ReviewLog] = []
    for event in events:
        rating = Rating.Good if event.correct else Rating.Again
        ts = event.timestamp
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        review_logs.append(
            ReviewLog(
                card_id=1,  # all events treated as a single virtual card for optimization
                rating=rating,
                review_datetime=ts,
                review_duration=None,
            )
        )

    # Fit optimal parameters
    optimizer = Optimizer(review_logs)
    optimal = optimizer.compute_optimal_parameters()

    # Persist fitted weights
    await upsert_child_fsrs_params(child_id, list(optimal), db)
