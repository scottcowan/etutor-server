"""
Session intelligence service — Phase 3 session context functions.

HIST-01: build_24hr_history_context — deduplicated 24-hour topic list for prompt injection
HIST-02: extract_and_update_interests — tag-based interest extraction from turn answers
CURR-02: build_prereq_tree_context — fragile/not_started prereqs with unlock lists
CURR-03: get/increment/reset_prereq_turn — rubber-band escalation counter management

Security note (T-3-03-01): extract_interests_from_turns uses `tag in answer_lower`
which is a read-only string operation against a pre-built static tag index.
No DB string interpolation. No injection path.

Security note (T-3-03-02): _prereq_turn_counter is an in-process dict that grows
as child×KC pairs accumulate. For Phase 3 (SQLite dev, single child) this is not
a practical risk. Phase 6 can add TTL cleanup if the dict exceeds a threshold.
Single-worker assumption — see RESEARCH.md Pitfall 5 for multi-worker limitation.
"""

from collections import defaultdict
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import MasteryStateModel
from db.crud import get_24hr_history, update_interests
from services.curriculum import CURRICULUM, _by_id


# ---------------------------------------------------------------------------
# Local mastery bucket helper — mirrors knowledge_tracing._mastery_bucket thresholds.
# Defined here to avoid importing services.knowledge_tracing at module level
# (which would fail if the fsrs package version in the environment doesn't export
# Scheduler — a pre-existing environment constraint in Phase 3 dev).
# ---------------------------------------------------------------------------

def _mastery_bucket(p_mastery: Optional[float]) -> str:
    """
    Map a p_mastery float to a bucket label (D-12 thresholds).
    Mirrors services.knowledge_tracing._mastery_bucket exactly.

    - None or < 0.1  -> "not_started"
    - 0.1 <= p < 0.7 -> "fragile"
    - 0.7 <= p < 0.95 -> "in_progress"
    - p >= 0.95      -> "solid"
    """
    if p_mastery is None or p_mastery < 0.1:
        return "not_started"
    if p_mastery < 0.7:
        return "fragile"
    if p_mastery < 0.95:
        return "in_progress"
    return "solid"


# ---------------------------------------------------------------------------
# Module-level session-level turn counter for rubber-band escalation (D-07).
# Single-worker assumption — see RESEARCH.md Pitfall 5 for multi-worker limitation.
# _prereq_turn_counter grows as child×KC pairs accumulate; see T-3-03-02 comment above.
# ---------------------------------------------------------------------------

_prereq_turn_counter: dict[tuple, int] = defaultdict(int)


# ---------------------------------------------------------------------------
# Module-level tag-to-topic index (built once at import time, ~870 topics).
# {tag_lower: topic_name} — used by extract_interests_from_turns.
# ---------------------------------------------------------------------------

_tag_to_topic: dict[str, str] = {}
for _t in CURRICULUM:
    for _tag in _t.tags:
        _tag_to_topic[_tag.lower()] = _t.name


# ---------------------------------------------------------------------------
# CURR-03: Escalation counter helpers (sync — no DB needed)
# ---------------------------------------------------------------------------

def get_prereq_turn(child_id: str, kc_id: str) -> int:
    """
    CURR-03: Return the current escalation turn count for a child×KC pair.

    Returns 0 if the pair has never been incremented.
    """
    return _prereq_turn_counter[(child_id, kc_id)]


def increment_prereq_turn(child_id: str, kc_id: str) -> int:
    """
    CURR-03: Increment the escalation turn counter for a child×KC pair by 1.

    Returns the new count.
    """
    _prereq_turn_counter[(child_id, kc_id)] += 1
    return _prereq_turn_counter[(child_id, kc_id)]


def reset_prereq_turn(child_id: str, kc_id: str) -> None:
    """
    CURR-03: Reset (remove) the escalation counter for a child×KC pair.

    After reset, get_prereq_turn() returns 0.
    """
    if (child_id, kc_id) in _prereq_turn_counter:
        del _prereq_turn_counter[(child_id, kc_id)]


def get_session_prereq_state(child_id: str) -> dict[str, int]:
    """
    CURR-03: Return dict of {kc_id: turn_count} for all active escalation entries for this child.

    Returns an empty dict if no escalation counters are active for this child.
    """
    return {
        kc_id: count
        for (cid, kc_id), count in _prereq_turn_counter.items()
        if cid == child_id
    }


# ---------------------------------------------------------------------------
# HIST-01: 24-hour history context builder
# ---------------------------------------------------------------------------

async def build_24hr_history_context(child_id: str, db: AsyncSession) -> list:
    """
    HIST-01: Return a deduplicated list of topic names from the last 24 hours.

    Topics are returned most-recent-first (DESC timestamp from get_24hr_history).
    Deduplication preserves first occurrence — which is the most recent, since
    get_24hr_history() returns rows DESC.
    Capped at 8 unique topic names (D-02 token cap).

    Returns [] when the child has no events in the last 24 hours.

    Parameters
    ----------
    child_id : str
        The child's identifier.
    db : AsyncSession
        Database session.
    """
    events = await get_24hr_history(child_id, db)
    seen: set = set()
    result: list = []

    for event in events:
        topic = event.topic
        if not topic:
            continue
        if topic in seen:
            continue
        seen.add(topic)
        result.append(topic)
        if len(result) >= 8:
            break

    return result


# ---------------------------------------------------------------------------
# CURR-02: Prerequisite tree context builder
# ---------------------------------------------------------------------------

async def build_prereq_tree_context(
    child_id: str,
    db: AsyncSession,
    limit: int = 5,
) -> list:
    """
    CURR-02: Return fragile/not_started prerequisites with their unlock lists.

    For each candidate topic from next_topics(), gathers prerequisites and
    filters out those with 'in_progress' or 'solid' mastery (D-13).
    Unlocks list per prereq is capped at 3 (D-12).

    Returns a list of dicts: [{"prereq_name": str, "prereq_kc_id": str, "unlocks": list[str]}].
    Returns [] if no candidates or no qualifying prerequisites found.

    Parameters
    ----------
    child_id : str
        The child's identifier.
    db : AsyncSession
        Database session.
    limit : int
        Maximum number of candidate topics to request from next_topics(). Default 5.
    """
    # Get candidate topics (FSRS-aware ranking).
    # Uses module-level `next_topics` reference so tests can patch it without
    # triggering the fsrs import chain.
    import services.session_intelligence as _self
    candidates = await _self.next_topics(child_id, db, limit=limit)
    if not candidates:
        return []

    # Gather all unique prerequisite IDs across all candidates
    all_prereq_ids = list({
        pid
        for topic in candidates
        for pid in (topic.prerequisites if hasattr(topic, "prerequisites") else [])
    })

    if not all_prereq_ids:
        return []

    # Batch-load MasteryStateModel rows for those prereq IDs (PATTERNS.md batch mastery load)
    stmt = (
        select(MasteryStateModel)
        .where(MasteryStateModel.child_id == child_id)
        .where(MasteryStateModel.kc_id.in_(all_prereq_ids))
    )
    result = await db.execute(stmt)
    mastery_rows = list(result.scalars().all())
    prereq_mastery: dict[str, MasteryStateModel] = {r.kc_id: r for r in mastery_rows}

    # Build prereq → unlocks mapping (keyed by prereq_id, NOT prereq_name)
    prereq_to_unlocks: dict[str, list] = {}

    for topic in candidates:
        prereqs = topic.prerequisites if hasattr(topic, "prerequisites") else []
        for prereq_id in prereqs:
            row = prereq_mastery.get(prereq_id)
            p = row.p_mastery if row is not None else None
            bucket = _mastery_bucket(p)
            # D-13: skip if in_progress or solid
            if bucket in ("in_progress", "solid"):
                continue
            if prereq_id not in prereq_to_unlocks:
                prereq_to_unlocks[prereq_id] = []
            prereq_to_unlocks[prereq_id].append(topic.name)

    if not prereq_to_unlocks:
        return []

    # Build output list with D-12 unlocks cap at 3
    output: list = []
    for pid, unlocks in prereq_to_unlocks.items():
        topic_obj = _by_id.get(pid)
        if topic_obj is None:
            continue
        output.append({
            "prereq_name": topic_obj.name,
            "prereq_kc_id": pid,
            "unlocks": unlocks[:3],
        })

    return output


# ---------------------------------------------------------------------------
# Internal proxy for next_topics — isolates the fsrs-dependent import.
# Tests mock `services.session_intelligence.next_topics` which patches this proxy.
# ---------------------------------------------------------------------------

async def _next_topics_proxy(child_id: str, db: AsyncSession, limit: int = 10) -> list:
    """
    Thin proxy around services.knowledge_tracing.next_topics.

    Isolated here so that tests can mock `services.session_intelligence.next_topics`
    without needing to import services.knowledge_tracing (which has an fsrs env
    dependency — v3.1.0 missing Scheduler).
    """
    from services.knowledge_tracing import next_topics as _kt_next_topics  # noqa: PLC0415
    return await _kt_next_topics(child_id, db, limit=limit)


# Expose as `next_topics` at module level so tests can mock `services.session_intelligence.next_topics`
next_topics = _next_topics_proxy


# ---------------------------------------------------------------------------
# HIST-02: Interest extraction helpers
# ---------------------------------------------------------------------------

def extract_interests_from_turns(turns: list) -> list:
    """
    HIST-02: Pure function — extract topic interests from a list of turn objects.

    Each turn must have an `.answer` attribute (str or None).
    Returns topic names where any tag appears in 2+ turn answers (D-09).
    Tag matching is case-insensitive substring search — no NLP (T-3-03-01).

    Parameters
    ----------
    turns : list
        List of objects with an `.answer` attribute.
    """
    tag_hits: dict[str, int] = defaultdict(int)

    for turn in turns:
        raw_answer = getattr(turn, "answer", None)
        answer_lower = raw_answer.lower() if raw_answer else ""
        for tag in _tag_to_topic:
            if tag in answer_lower:
                tag_hits[tag] += 1

    # Collect topic names where any tag hit >= 2
    matched_topics: set = set()
    for tag, count in tag_hits.items():
        if count >= 2:
            topic_name = _tag_to_topic[tag]
            matched_topics.add(topic_name)

    return list(matched_topics)


async def extract_and_update_interests(
    session_id: str,
    child_id: str,
    db: AsyncSession,
) -> None:
    """
    HIST-02: Extract interests from session turns and persist to child profile.

    Fetches all turns for session_id, extracts topic interests using
    extract_interests_from_turns(), then merges with existing interests
    via update_interests() (D-10: set union, idempotent).

    Returns early if the session has no turns or no interests are extracted.

    Parameters
    ----------
    session_id : str
        The tutoring session identifier.
    child_id : str
        The child's identifier.
    db : AsyncSession
        Database session.
    """
    from db.crud import get_turns_by_session_id

    turns = await get_turns_by_session_id(session_id, db)
    if not turns:
        return

    new_interests = extract_interests_from_turns(turns)
    if not new_interests:
        return

    await update_interests(child_id, new_interests, db)
