"""
Knowledge tracing service — BKT + FSRS (Phase 2).

KT-01: BKT closed-form updates
KT-02: FSRS scheduling fields
KT-03: next_topics() using mastery + FSRS schedule
KT-04: Post-session BKT batch update
KT-05: mastery_context_for_prompt() for prompt injection

Security note (T-2-03): session_id used in WHERE clause via SQLAlchemy ORM
parameterised select() — never string-interpolated.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import InteractionEventModel
from db.crud import create_or_get_mastery_state, update_mastery_state


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
