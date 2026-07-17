# Phase 3: Session Intelligence — Research

**Researched:** 2026-07-17
**Domain:** FastAPI async service extension, SQLAlchemy timestamp filtering, curriculum graph traversal, in-memory session state
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**History Summary (HIST-01)**
- **D-01:** Inject a flat topic list (most recent first) as the 24-hour history block. Format: `Recent topics: volcanoes, plate tectonics, igneous rocks`.
- **D-02:** Token cap for the history block: ~50 tokens (~5-8 topic names). Keeps system prompt well under 500 tokens total for Haiku latency target.
- **D-03:** Topics extracted from `InteractionEventModel.topic` field, deduplicated, ordered by `timestamp DESC`, limited to the past 24 hours.

**Prerequisite Enforcement (CURR-02)**
- **D-04:** Rubber-band pattern — system prompt signals unmet prerequisites and instructs escalating redirect behavior.
- **D-05:** The prerequisite assumption is soft: probe understanding before assuming ignorance.
- **D-06:** Correct probe answer → update `p_mastery` for the prerequisite KC AND give a quick refresher. Both required.
- **D-07:** Escalation cadence: Turn 1 = engage + hint. Turn 2 = gentle probe. Turn 3+ = active steer. Tracked via session-level counter per child×KC pair, not persisted to DB.

**Interest Extraction (CURR-03)**
- **D-08:** Interest extraction runs at BOTH session end (`POST /sessions/{id}/end`) AND on next session start (dual trigger).
- **D-09:** Matching: scan child answer text against `Topic.tags`. Tag appears in 2+ turns → add topic name to interests. Case-insensitive substring. No NLP.
- **D-10:** Use existing `update_interests()` CRUD. New interests appended (no replacement).

**Prerequisite Gap Surfacing (HIST-02)**
- **D-11:** One-level-deep topic tree in system prompt: `{prerequisite} → unlocks: {topic1}, {topic2}, ...`
- **D-12:** Truncate unlocks at 3 per prerequisite. Order by FSRS `next_review` urgency.
- **D-13:** Only show prerequisites that are `fragile` or `not_started` — skip `in_progress` or `solid`.

**supersedes Unlocking (CURR-04)**
- **D-14:** When `p_mastery` reaches `bloom_target` for a topic KC, check for topics with `supersedes = this_topic_id` and add them to `next_topics()` output. Runs inside `next_topics()`.

### Claude's Discretion

- The exact SQL query structure for the 24-hour history lookup (whether to join `sessions` table or filter `InteractionEventModel.timestamp` directly).
- Whether to create a new `services/session_intelligence.py` module or extend `services/knowledge_tracing.py`.
- Whether HIST-03 (session turn log retrievable per session_id) requires a new endpoint or reuses existing `get_session_history()`.

### Deferred Ideas (OUT OF SCOPE)

- Vector-embedding interest graph (v2).
- Deep prerequisite tree rendering (2+ levels).
- Per-turn interest extraction.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HIST-01 | Last 24hr session summary injected into every system prompt | D-01–D-03; `get_session_history()` needs timestamp filter added; `build_system_prompt()` gets `history_context` param |
| HIST-02 | Prerequisite skill gaps surfaced in prompt context | D-11–D-13; `next_topics()` already has mastery buckets; prereq gap block uses `Topic.prerequisites` + `_mastery_bucket()` |
| HIST-03 | Session turn log stored and retrievable per session_id | Needs new `GET /sessions/{session_id}/turns` endpoint — current `GET /sessions/{child_id}` filters by child, not session |
| CURR-01 | Tutor session selects focus topics using next_topics() + child interests | `next_topics()` already wires interests; `api/chat.py` already calls `mastery_context_for_prompt()`; D-14 adds supersedes unlock |
| CURR-02 | Topic prerequisites enforced via rubber-band escalation | D-04–D-07; new session-level counter dict; new `prereq_tree` + `session_prereq_state` params on `build_system_prompt()` |
| CURR-03 | Interest tags updated from session history | D-08–D-10; interest extractor function scans `InteractionEventModel.answer` against `Topic.tags`; called at session end and session start |
| CURR-04 | supersedes topics unlock when prerequisite mastered to bloom_target | D-14; `curriculum.next_topics()` extended; 14 topics have `supersedes` in CURRICULUM (870 total) |
</phase_requirements>

---

## Summary

Phase 3 adds four independent intelligence layers on top of Phase 2's BKT/FSRS scaffolding. Each layer is a relatively small addition to an existing function or service, with no new DB tables required. The highest-complexity item is session-level prerequisite state (D-07) — a per-child×KC turn counter that must live in memory for the escalation cadence without DB writes. The lowest-complexity item is the supersedes unlock (D-14) — a six-line extension to `curriculum.next_topics()`.

The Phase 2 code review (CR-01, CR-02) identified two pre-existing bugs: the streaming generator uses a closed DB session, and GET /sessions/{child_id} has no authorization check. Phase 3 must not make these worse. Specifically: the interest extraction code added to `end_session()` must use the `db: AsyncSession` already in scope in that function — it does not touch the streaming path (CR-01). The new GET /sessions/{session_id}/turns endpoint (HIST-03) must mirror the same IDOR exposure as the existing endpoint and should receive the same ownership-check treatment when auth is added later.

The current system prompt is ~939 tokens on a typical child profile. Adding all Phase 3 blocks (history ~20 tokens, prereq tree ~43 tokens) brings the total to approximately 1,002 tokens — comfortably under the 1,500-token target.

**Primary recommendation:** Create a new `services/session_intelligence.py` module for the three new service functions (history context builder, prerequisite tree builder, interest extractor). This keeps `services/knowledge_tracing.py` focused on BKT/FSRS and avoids making that already-large file the catch-all for session intelligence logic.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 24hr history injection (HIST-01) | API / Backend service | DB (read-only) | History is fetched per-request; injected before LLM call in `api/chat.py` |
| Prerequisite gap surfacing (HIST-02) | API / Backend service | DB + in-memory curriculum | Prereq tree built from mastery state + curriculum graph; injected into prompt |
| Session turn log retrieval (HIST-03) | API / Backend | DB (read-only) | New GET endpoint; scoped to session_id |
| Curriculum topic selection (CURR-01) | Backend service | DB + curriculum | `next_topics()` already owns this; CURR-04 unlock check added here |
| Prerequisite escalation (CURR-02) | In-memory session state | Backend prompt builder | Turn counter lives in memory per session; prompt builder renders the signal |
| Interest extraction (CURR-03) | Backend service | DB (write) | Text scan + DB write; triggered at session end and session start |
| supersedes unlock (CURR-04) | Backend service (curriculum) | DB (mastery read) | Pure curriculum logic extension; `next_topics()` checks mastery vs. bloom_target |

---

## Standard Stack

Phase 3 introduces no new external packages. All required capabilities are already in the installed stack.

### Core (already installed)
| Library | Version | Purpose | Used By Phase 3 |
|---------|---------|---------|-----------------|
| SQLAlchemy | >=2.0.0 | Async ORM for 24hr timestamp query | `get_24hr_history()` new CRUD function |
| FastAPI | >=0.100.0 | Route handlers | New HIST-03 endpoint |
| Python stdlib `datetime` | 3.9+ | UTC-aware timedelta for 24hr window | `now - timedelta(hours=24)` |
| Python stdlib `collections` | 3.9+ | `defaultdict` for session-level turn counter | D-07 escalation cadence |

### No New Packages Required

The interest extractor (D-09) is a case-insensitive substring scan — no NLP library needed. The session-level counter (D-07) is a plain Python dict. No migration is needed — Phase 3 adds no new DB columns.

**Installation:** No `pip install` needed for Phase 3.

---

## Package Legitimacy Audit

Phase 3 installs no new external packages. This section is not applicable.

---

## Architecture Patterns

### System Architecture Diagram

```
Child device
    │
    ▼
POST /chat/completions (api/chat.py)
    │
    ├─► get_child_by_id()                  [DB read]
    ├─► mastery_context_for_prompt()        [DB read — Phase 2, unchanged]
    ├─► build_24hr_history_context()        [DB read — NEW Phase 3]
    │       └─► get_24hr_history() in crud.py
    ├─► build_prereq_tree_context()         [DB read + curriculum — NEW Phase 3]
    │       └─► MasteryStateModel lookup
    │       └─► Topic.prerequisites traversal
    ├─► get_session_prereq_state()          [in-memory dict — NEW Phase 3]
    └─► build_system_prompt(child,
            mastery_context,
            history_context,        ◄── NEW
            prereq_tree,            ◄── NEW
            session_prereq_state)   ◄── NEW
            └─► LLM (litellm)

POST /sessions/{id}/end (api/sessions.py)
    │
    ├─► [existing] ended_at, BKT update, FSRS fit
    └─► extract_and_update_interests()     [DB read+write — NEW Phase 3]
            └─► get_session_history() scoped to session_id
            └─► scan answers against Topic.tags
            └─► update_interests()

POST /chat/completions (session START path)
    │
    └─► [NEW] extract_and_update_interests() for previous session
            └─► find most recent ended session with no interest scan
            └─► run same interest extractor as end_session()

GET /sessions/{session_id}/turns (api/sessions.py)   [NEW HIST-03]
    └─► get_turns_by_session_id() in crud.py
```

### Recommended Project Structure

Phase 3 adds one new service file and extends four existing files:

```
services/
├── session_intelligence.py   # NEW — history context, prereq tree, interest extractor
├── tutor.py                  # EXTEND — history_context, prereq_tree, session_prereq_state params
├── knowledge_tracing.py      # EXTEND — next_topics() adds supersedes unlock check (D-14)
api/
├── chat.py                   # EXTEND — call new session_intelligence functions before build_system_prompt
├── sessions.py               # EXTEND — call interest extractor in end_session(); add HIST-03 endpoint
db/
├── crud.py                   # EXTEND — get_24hr_history() and get_turns_by_session_id()
```

### Pattern 1: 24-Hour Timestamp Filter (HIST-01)

**What:** Add `since` parameter to `get_session_history()` or add a dedicated `get_24hr_history()` function. The planner should add `get_24hr_history()` as a new function (doesn't break existing callers of `get_session_history()`).

**When to use:** Called by `build_24hr_history_context()` in `services/session_intelligence.py` before each `chat()` request.

**Example:**
```python
# Source: [VERIFIED codebase] — follows db/crud.py select/where/order_by pattern exactly
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from db.models import InteractionEventModel

async def get_24hr_history(
    child_id: str,
    session: AsyncSession,
    limit: int = 50,
) -> list[InteractionEventModel]:
    """Return interaction events for child_id in the past 24 hours, DESC order."""
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    result = await session.execute(
        select(InteractionEventModel)
        .where(InteractionEventModel.child_id == child_id)
        .where(InteractionEventModel.timestamp >= since)
        .order_by(InteractionEventModel.timestamp.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
```

**Key detail:** `InteractionEventModel.timestamp` is `DateTime(timezone=True)` — the stored value is UTC-aware. `datetime.now(timezone.utc) - timedelta(hours=24)` produces a UTC-aware datetime that SQLAlchemy can compare correctly against it. Do NOT use `datetime.utcnow()` (naive — risks wrong comparison on SQLite).

### Pattern 2: history_context Block in build_system_prompt (HIST-01)

**What:** Add `history_context: Optional[list] = None` parameter to `build_system_prompt()` following the same `mastery_context` extension pattern from Phase 2.

**When to use:** Called with a list of topic name strings (deduplicated, most-recent-first, max 8 items).

**Example:**
```python
# Source: [VERIFIED codebase] — follows services/tutor.py mastery_section pattern exactly
HISTORY_CONTEXT_TEMPLATE = "\nRecent topics: {topic_list}\n"

def _format_history_context(history_context: list) -> str:
    if not history_context:
        return ""
    return HISTORY_CONTEXT_TEMPLATE.format(topic_list=", ".join(history_context))

# In build_system_prompt():
async def build_system_prompt(
    child,
    mastery_context: Optional[list] = None,
    history_context: Optional[list] = None,
    prereq_tree: Optional[list] = None,
    session_prereq_state: Optional[dict] = None,
) -> str:
    # ... existing code ...
    mastery_section = _format_mastery_context(mastery_context) if mastery_context else ""
    history_section = _format_history_context(history_context) if history_context else ""
    prereq_section = _format_prereq_tree(prereq_tree) if prereq_tree else ""
    return base_prompt + mastery_section + history_section + prereq_section
```

**Backward-compat:** All three new params have `None` defaults. Existing evals that call `build_system_prompt(child)` or `build_system_prompt(child, mastery_context=[...])` are unaffected.

### Pattern 3: Session-Level Prerequisite Turn Counter (D-07)

**What:** A module-level dict in `services/session_intelligence.py` keyed by `(child_id, kc_id)` → turn count. This is the right trade-off for Phase 3: no DB overhead, naturally ephemeral (process restart clears it), and sufficient for the escalation cadence.

**When to use:** Incremented on each chat turn when the current topic has an unmastered prerequisite. Read by `build_system_prompt()` to select the correct escalation signal.

**Example:**
```python
# Source: [ASSUMED] — standard Python pattern; no library needed
from collections import defaultdict
from typing import Optional

# Module-level — lives for the process lifetime; intentionally not persisted (D-07)
_prereq_turn_counter: dict[tuple[str, str], int] = defaultdict(int)

def get_prereq_turn(child_id: str, kc_id: str) -> int:
    """Return current escalation turn count for this child×KC pair."""
    return _prereq_turn_counter[(child_id, kc_id)]

def increment_prereq_turn(child_id: str, kc_id: str) -> int:
    """Increment and return the new turn count."""
    _prereq_turn_counter[(child_id, kc_id)] += 1
    return _prereq_turn_counter[(child_id, kc_id)]

def reset_prereq_turn(child_id: str, kc_id: str) -> None:
    """Reset counter when prerequisite mastery is confirmed (D-06)."""
    _prereq_turn_counter.pop((child_id, kc_id), None)
```

**Concurrency note:** This is a single-process dict. FastAPI's async event loop is single-threaded — no locking needed for aiosqlite/SQLite deployments. For multi-worker Gunicorn deployments (future), this would need Redis or a DB-backed counter. Document this as a known limitation in the code comment.

### Pattern 4: Interest Extraction (D-08, D-09)

**What:** Scan `InteractionEventModel.answer` strings from a session against all `Topic.tags` strings. If a tag appears in ≥2 turn answers, add the topic name to child interests.

**When to use:** At session end AND at session start (D-08 dual trigger).

**Performance analysis:** 870 topics × avg 8.3 tags = ~7,221 tag strings. For each session with N turns: N × 7,221 substring checks. At 20 turns, that's 144,420 string operations. Python's `in` operator on short strings is O(len(text) × len(tag)) but highly optimized in CPython. For a 20-turn session this runs in well under 1ms — linear scan is acceptable. [VERIFIED: codebase — topic count confirmed at 870 from curriculum.py]

**Example:**
```python
# Source: [VERIFIED codebase] — Topic.tags confirmed as list[str] in curriculum.py
from services.curriculum import CURRICULUM

def extract_interests_from_turns(
    turns: list,  # list[InteractionEventModel]
) -> list[str]:
    """
    D-09: Return topic names where a tag appears in 2+ turn answers.
    Case-insensitive substring match. No NLP.
    """
    # Build tag → topic_name index once
    tag_to_topic: dict[str, str] = {}
    for topic in CURRICULUM:
        for tag in topic.tags:
            tag_to_topic[tag.lower()] = topic.name

    # Count tag appearances across turn answers
    tag_hits: dict[str, int] = defaultdict(int)
    for turn in turns:
        answer_lower = (turn.answer or "").lower()
        for tag in tag_to_topic:
            if tag in answer_lower:
                tag_hits[tag] += 1

    # Collect topic names where any tag hit >= 2
    matched_topics: set[str] = set()
    for tag, count in tag_hits.items():
        if count >= 2:
            matched_topics.add(tag_to_topic[tag])

    return list(matched_topics)
```

**Optimization note:** The tag-to-topic index (`tag_to_topic`) is built from the module-level `CURRICULUM` list. Building it per-call is cheap (870 × 8.3 = ~7k iterations), but it can be module-level cached if profiling shows it matters.

### Pattern 5: supersedes Unlock in next_topics() (D-14)

**What:** After the existing candidate filtering in `services/knowledge_tracing.next_topics()`, add a check: for each KC in `mastered_ids` where `p_mastery >= bloom_target_for_that_kc`, look up topics with `supersedes = kc_id` and inject them as candidates.

**Critical detail about bloom_target vs p_mastery:** `bloom_target` is a Bloom level integer (1–6). `p_mastery` is a BKT probability (0.0–1.0). The CONTEXT.md decision D-14 says "when p_mastery reaches bloom_target" but these are incommensurable scales. The correct interpretation: use the existing `solid` threshold (`p_mastery >= 0.95`) as the unlock trigger — "mastered to bloom_target" means the child has solidly mastered the topic per BKT, regardless of which Bloom level the topic targets. The `bloom_target` on the superseded topic is a pedagogical guide for the tutor (what depth to aim for), not a numerical threshold to compare against `p_mastery`. [ASSUMED — this interpretation is consistent with the existing `solid` bucket definition and the D-14 language, but the planner should confirm with user if the intended trigger is `p_mastery >= 0.95` vs some other threshold.]

**Example:**
```python
# Source: [VERIFIED codebase] — follows curriculum.py pattern; _by_id dict already exists
from services.curriculum import CURRICULUM, _by_id

# Build reverse supersedes index at module level (one-time cost)
_superseded_by: dict[str, list[str]] = {}
for _t in CURRICULUM:
    if _t.supersedes:
        _superseded_by.setdefault(_t.supersedes, []).append(_t.id)

# In services/knowledge_tracing.next_topics():
# After: mastered_ids = [r.kc_id for r in mastery_rows if r.p_mastery >= 0.95]
# Add:
for kc_id in mastered_ids:
    for superseding_id in _superseded_by.get(kc_id, []):
        superseding_topic = _by_id.get(superseding_id)
        if superseding_topic and superseding_id not in mastered_ids:
            # Add to candidates if not already there
            if superseding_topic not in candidates:
                candidates.append(superseding_topic)
```

### Pattern 6: Prerequisite Tree for Prompt (HIST-02)

**What:** Build a list of dicts, one per fragile/not_started prerequisite, showing which next_topics it would unlock. Format: `{"prereq_name": "Rock Types", "unlocks": ["Volcanoes", "Plate Tectonics"]}`.

**When to use:** Called in `api/chat.py` before `build_system_prompt()`. Limited to `fragile` and `not_started` prerequisites (D-13). Unlocks list capped at 3 per prereq (D-12).

**Example:**
```python
# Source: [VERIFIED codebase] — uses existing mastery_by_kc pattern and Topic.prerequisites
async def build_prereq_tree_context(
    child_id: str,
    db: AsyncSession,
    limit: int = 5,
) -> list[dict]:
    """
    HIST-02: One-level prereq tree. Returns [{prereq_name, unlocks: [topic_name, ...]}]
    Only fragile/not_started prerequisites shown (D-13). Unlocks capped at 3 (D-12).
    """
    # Get current next_topics candidates
    topics = await next_topics(child_id, db, limit=limit)
    if not topics:
        return []

    # Load mastery state for all prereqs referenced
    all_prereq_ids = set()
    for topic in topics:
        all_prereq_ids.update(topic.prerequisites)

    if not all_prereq_ids:
        return []

    stmt = (
        select(MasteryStateModel)
        .where(MasteryStateModel.child_id == child_id)
        .where(MasteryStateModel.kc_id.in_(list(all_prereq_ids)))
    )
    result = await db.execute(stmt)
    prereq_mastery = {r.kc_id: r for r in result.scalars().all()}

    # Group: which topics does each fragile/not_started prereq unlock?
    prereq_to_unlocks: dict[str, list[str]] = defaultdict(list)
    for topic in topics:
        for prereq_id in topic.prerequisites:
            row = prereq_mastery.get(prereq_id)
            bucket = _mastery_bucket(row.p_mastery if row else None)
            if bucket in ("fragile", "not_started"):
                prereq_topic = _by_id.get(prereq_id)
                if prereq_topic:
                    prereq_to_unlocks[prereq_topic.name].append(topic.name)

    # Build output: cap unlocks at 3, order by FSRS next_review urgency (D-12)
    tree = []
    for prereq_name, unlocks in prereq_to_unlocks.items():
        tree.append({
            "prereq_name": prereq_name,
            "unlocks": unlocks[:3],
        })

    return tree
```

### Pattern 7: HIST-03 — GET /sessions/{session_id}/turns

**What:** New route that returns turns filtered by `session_id` (not child_id). Requires a new CRUD function `get_turns_by_session_id()` in `db/crud.py`.

**Why a new endpoint:** Current `GET /sessions/{child_id}` filters by `child_id`. `HIST-03` requires retrieval by `session_id`. The `InteractionEventModel` has a `session_id` FK column — a new `WHERE session_id = ?` query is straightforward.

**Example:**
```python
# Source: [VERIFIED codebase] — follows get_session_history() pattern exactly
async def get_turns_by_session_id(
    session_id: str,
    db: AsyncSession,
) -> list[InteractionEventModel]:
    result = await db.execute(
        select(InteractionEventModel)
        .where(InteractionEventModel.session_id == session_id)
        .order_by(InteractionEventModel.timestamp.asc())
    )
    return list(result.scalars().all())
```

**Route:**
```python
@router.get("/sessions/{session_id}/turns")
async def get_session_turns(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    turns = await get_turns_by_session_id(session_id, db)
    return {
        "session_id": session_id,
        "turns": [
            {
                "id": t.id,
                "child_id": t.child_id,
                "question": t.question,
                "answer": t.answer,
                "topic": t.topic,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            }
            for t in turns
        ],
    }
```

**IDOR note (CR-02 awareness):** This endpoint has the same IDOR exposure as the existing `GET /sessions/{child_id}`. Do not add additional authorization beyond what already exists — match the existing pattern so they are fixed together in the auth phase. Do NOT introduce an inconsistent auth check here that would make the existing endpoint appear more secure than it is.

### Anti-Patterns to Avoid

- **Blocking `build_system_prompt()` with DB calls:** All DB work (history, prereq tree) must happen BEFORE calling `build_system_prompt()` in `api/chat.py`. `build_system_prompt()` must remain a sync-compatible formatter — it receives pre-fetched data, never calls DB itself.
- **Mutating `curriculum.next_topics()` signature:** The `curriculum.next_topics(age, mastered_ids, interests)` function in `curriculum.py` is a pure function. The supersedes logic goes into `services/knowledge_tracing.next_topics()` which wraps it, not into `curriculum.py` directly. This preserves the pure/testable curriculum module.
- **Interest extraction on every chat turn:** D-08 explicitly rules this out. Only at session end and session start. Never inside the streaming path.
- **Using `datetime.utcnow()` for the 24hr cutoff:** Returns a naive datetime that will produce wrong results when compared to the UTC-aware `InteractionEventModel.timestamp` column. Always use `datetime.now(timezone.utc)`.
- **Passing topic IDs to build_system_prompt():** All prompt params use human-readable names and bucket labels, not internal IDs. The LLM receives "Rock Types (fragile)", not "rocks_soils (fragile)".

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Tag index from curriculum | Custom search/index | Module-level dict built from `CURRICULUM` list at import time | Already 870 topics; linear dict build is trivial at startup |
| Mastery bucket lookup | New function | `_mastery_bucket()` in `services/knowledge_tracing.py` | Already implemented with correct thresholds |
| Prerequisite check | Custom graph walk | `curriculum.prerequisites_met(topic_id, mastered_ids)` | Already implemented and tested |
| Topic lookup by ID | Database query | `curriculum._by_id[topic_id]` (module-level dict) | Already O(1) dict lookup; no DB round-trip needed |
| Interest merge | Set union logic | `db.crud.update_interests()` | Already handles set union to prevent duplication |

**Key insight:** The curriculum module already provides all graph operations needed (prerequisite check, topic lookup, interest scoring). Phase 3 only needs to connect these to the DB mastery state and the prompt builder.

---

## Common Pitfalls

### Pitfall 1: 24hr History Cuts Across Session Boundaries
**What goes wrong:** The 24hr history query returns events from multiple sessions. If you try to group by session, you complicate the query and the D-01 format (flat topic list) doesn't need it.
**Why it happens:** Temptation to join the `sessions` table to get session-level grouping.
**How to avoid:** Query `InteractionEventModel` directly with `timestamp >= (now - 24h)`. Extract `.topic` field, deduplicate with a seen-set while iterating DESC, take first 8 unique non-null topics. No join needed.
**Warning signs:** Any SQL JOIN against `sessions` in the history query — that's overengineering for D-01.

### Pitfall 2: session_prereq_state Passed Into build_system_prompt() Incorrectly
**What goes wrong:** The `session_prereq_state` param is a dict mapping `kc_id → turn_count`. `build_system_prompt()` needs to render the escalation signal (hint/probe/steer) but the `kc_id` of the current topic comes from `req` in `api/chat.py`, not from the child profile.
**Why it happens:** The chat request doesn't necessarily specify `kc_id` — it specifies natural-language content. The prereq escalation applies to the topic being discussed in the current turn.
**How to avoid:** In `api/chat.py`, extract the current topic's prerequisites from the matched `Topic` object (if the `topic` field in the chat request maps to a curriculum topic). If no curriculum match, skip the escalation block. Document this as a "best-effort" signal in the prompt — the tutor will still work without it.
**Warning signs:** `build_system_prompt()` performing curriculum lookups itself — it should receive pre-computed data only.

### Pitfall 3: Dual-Trigger Interest Extraction Double-Counts
**What goes wrong:** Session end triggers interest extraction. Session start triggers extraction for the previous session. If both triggers fire for the same session (e.g., device sends `/end` AND a new session starts), the same interest is added twice — but `update_interests()` uses set union so duplicates are silently ignored. This is actually fine by design.
**Why it happens:** Understanding of D-08 dual trigger is incomplete.
**How to avoid:** The session-start path should find the most-recent session for the child that: (a) has `ended_at IS NOT NULL` and (b) has NOT had interest extraction run yet. Add an `interests_extracted_at` flag OR simply always run extraction on session start — `update_interests()` is idempotent (set union). The simpler approach (always run at start) is correct.
**Warning signs:** Any attempt to track "has this session been interest-extracted?" in a separate DB column — that's over-engineering; idempotency handles it.

### Pitfall 4: bloom_target / p_mastery Scale Mismatch for CURR-04
**What goes wrong:** D-14 says "p_mastery reaches bloom_target" but `bloom_target` is 1–6 and `p_mastery` is 0.0–1.0. Literally comparing `p_mastery >= bloom_target` will never trigger (bloom_target values are all ≥ 2; p_mastery is always ≤ 1.0).
**Why it happens:** D-14 language is ambiguous.
**How to avoid:** Use `p_mastery >= 0.95` (the existing `solid` threshold) as the unlock trigger for supersedes. This is the natural interpretation: "fully mastered the simpler model." See Assumptions Log A1.
**Warning signs:** Any literal `p_mastery >= topic.bloom_target` comparison — this will silently never fire.

### Pitfall 5: Module-Level Dict for _prereq_turn_counter in Multi-Worker Deployments
**What goes wrong:** If FastAPI is run with multiple workers (Gunicorn + uvicorn workers), each worker has its own memory space. The `_prereq_turn_counter` dict is per-worker. A child whose requests are load-balanced across workers will see inconsistent escalation behavior.
**Why it happens:** Module-level state is per-process in Python.
**How to avoid:** For Phase 3 (SQLite dev), this is not an issue — single worker is the standard. Document the limitation in a comment. Phase 6 (performance/polish) can upgrade to Redis-backed counters if multi-worker is needed.
**Warning signs:** Any deployment config specifying `--workers > 1` without a Redis counter migration.

### Pitfall 6: Prereq Tree Block Renders Prerequisite IDs, Not Names
**What goes wrong:** The prompt block renders `rocks_soils → unlocks: volcanoes_ks2` instead of `Rock Types, Soils, and Weathering → unlocks: Volcanoes`.
**Why it happens:** Using `topic.id` instead of `topic.name` when building the tree dict.
**How to avoid:** Always look up `Topic.name` via `_by_id[kc_id].name`. The prompt builder receives human-readable names throughout.

---

## Runtime State Inventory

Phase 3 adds no new DB tables, no new environment variables, and no new external service registrations. Skip: no rename/refactor scope.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.9+ | `Optional[list]` typing, `timedelta` | ✓ | 3.x (project standard) | — |
| SQLAlchemy >= 2.0 | Async timestamp filter query | ✓ | installed Phase 1 | — |
| FastAPI | New HIST-03 route | ✓ | installed Phase 1 | — |
| SQLite (dev) / aiosqlite | DB queries | ✓ | installed Phase 1 | — |

No missing dependencies for Phase 3.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | pytest.ini (asyncio_mode = auto) |
| Quick run command | `pytest tests/ -x -q` |
| Full suite command | `pytest tests/ -v` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| HIST-01 | 24hr history injected into system prompt | unit | `pytest tests/services/test_session_intelligence.py::test_history_context_format -x` | ❌ Wave 0 |
| HIST-01 | `get_24hr_history()` filters to last 24h only | unit+integration | `pytest tests/db/test_crud_session_intelligence.py::test_get_24hr_history -x` | ❌ Wave 0 |
| HIST-02 | Prereq tree renders fragile/not_started only | unit | `pytest tests/services/test_session_intelligence.py::test_prereq_tree_filters -x` | ❌ Wave 0 |
| HIST-02 | build_system_prompt includes prereq_tree block | unit | `pytest tests/services/test_tutor.py::test_system_prompt_with_prereq_tree -x` | ❌ Wave 0 |
| HIST-03 | GET /sessions/{session_id}/turns returns correct turns | integration | `pytest tests/api/test_session_turns.py::test_get_session_turns -x` | ❌ Wave 0 |
| CURR-01 | next_topics includes supersedes unlocks when mastered | unit | `pytest tests/services/test_session_intelligence.py::test_supersedes_unlock -x` | ❌ Wave 0 |
| CURR-02 | session_prereq_state escalation cadence | unit | `pytest tests/services/test_session_intelligence.py::test_escalation_cadence -x` | ❌ Wave 0 |
| CURR-03 | extract_interests finds tags in 2+ turns | unit | `pytest tests/services/test_session_intelligence.py::test_interest_extraction -x` | ❌ Wave 0 |
| CURR-03 | interest extraction runs at session end | integration | `pytest tests/api/test_session_end.py::test_end_session_extracts_interests -x` | ❌ Wave 0 |
| CURR-04 | supersedes topic appears in next_topics after solid mastery | unit | `pytest tests/services/test_knowledge_tracing.py::test_supersedes_unlock -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/ -x -q` (full suite, fast)
- **Per wave merge:** `pytest tests/ -v`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/services/test_session_intelligence.py` — covers HIST-01, HIST-02, CURR-02, CURR-03 unit tests
- [ ] `tests/db/test_crud_session_intelligence.py` — covers `get_24hr_history()` and `get_turns_by_session_id()` DB tests
- [ ] `tests/api/test_session_turns.py` — covers HIST-03 integration test
- [ ] `tests/api/test_session_end.py` already exists — CURR-03 integration test adds to it

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Not in scope Phase 3 |
| V3 Session Management | yes | Session ID used in HIST-03 endpoint — same IDOR exposure as CR-02; do not worsen |
| V4 Access Control | yes | HIST-03 `GET /sessions/{session_id}/turns` exposes child turn data — match existing pattern, fix together with CR-02 in auth phase |
| V5 Input Validation | yes | Tag matching uses `in` operator on answer text — no injection risk (no DB string interpolation); SQLAlchemy ORM throughout |
| V6 Cryptography | no | No new crypto operations |

### Known Threat Patterns for This Phase

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| IDOR on `/sessions/{session_id}/turns` | Information Disclosure | Same pattern as CR-02 — do not add inconsistent auth; fix both endpoints together in auth phase |
| Substring tag matching on user-supplied answer text | Tampering | `tag in answer_lower` is read-only; no DB write based on raw text; safe |
| Module-level `_prereq_turn_counter` dict growth | Denial of Service | Dict grows unboundedly if children never clear counters; add max-size guard or TTL cleanup if dict exceeds threshold |

### CR-01 / CR-02 Non-Regression

**CR-01 (streaming generator / closed session):** Phase 3 adds calls to `extract_and_update_interests()` inside `end_session()`, which uses `db: AsyncSession = Depends(get_db)` scoped to the `end_session()` request handler. This is NOT the streaming path. No new DB calls are added inside `generate()`. CR-01 is not worsened.

**CR-02 (IDOR):** The new HIST-03 endpoint follows the same pattern as the existing `GET /sessions/{child_id}` — no authorization check. Both endpoints should receive auth together. Do not selectively gate HIST-03 while leaving the existing endpoint ungated.

---

## Code Examples — Verified Patterns

### Wiring all three new context builders in api/chat.py

```python
# Source: [VERIFIED codebase] — follows existing mastery_ctx pattern in api/chat.py lines 57-58
from services.session_intelligence import (
    build_24hr_history_context,
    build_prereq_tree_context,
    get_session_prereq_state,
)

# In chat() after child is resolved:
mastery_ctx = await mastery_context_for_prompt(child_id, session, limit=5)
history_ctx = await build_24hr_history_context(child_id, session)
prereq_tree = await build_prereq_tree_context(child_id, session, limit=5)
prereq_state = get_session_prereq_state(child_id)

system_prompt = await build_system_prompt(
    child,
    mastery_context=mastery_ctx or None,
    history_context=history_ctx or None,
    prereq_tree=prereq_tree or None,
    session_prereq_state=prereq_state or None,
)
```

### Wiring interest extraction in end_session()

```python
# Source: [VERIFIED codebase] — follows existing end_session() structure in api/sessions.py
from services.session_intelligence import extract_and_update_interests

# At the end of end_session(), after BKT and FSRS:
await extract_and_update_interests(session_id, session_row.child_id, db)

return {
    "session_id": session_id,
    "ended_at": session_row.ended_at.isoformat(),
    "kcs_updated": len(bkt_updates),
}
```

### Session-start catch-up trigger in api/chat.py

```python
# Source: [ASSUMED] — D-08 dual trigger; exact wiring is planner's discretion
# After child is resolved, before building system prompt:
# Find most recent ended session and run interest extraction on it
from db.crud import get_most_recent_ended_session  # new CRUD function needed
from services.session_intelligence import extract_and_update_interests

prev_session = await get_most_recent_ended_session(child_id, session)
if prev_session and prev_session.id:
    await extract_and_update_interests(prev_session.id, child_id, session)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Inject only mastery buckets | Inject history + prereqs + mastery | Phase 3 | More context-aware tutoring per HIST-01, HIST-02 |
| Interest tags set manually by parent | Auto-extracted from session turns | Phase 3 | Curriculum selection becomes self-tuning |
| Hard prerequisite blocks | Rubber-band escalation (soft enforce) | Phase 3 | Respects child curiosity while building foundations |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `p_mastery >= 0.95` (solid threshold) is the correct trigger for CURR-04 supersedes unlock, interpreting D-14 "reaches bloom_target" as "solidly mastered" | Pattern 5, Pitfall 4 | If the user meant a different threshold (e.g., a mapped Bloom→p_mastery scale), the unlock fires too early or never |
| A2 | The session-start catch-up trigger for D-08 should run on the most-recent ended session (not all un-extracted sessions) | Pattern sections | If many sessions accumulated without `/end` calls, the start trigger only catches one — older sessions' interests are never extracted |
| A3 | `services/session_intelligence.py` is the right module home (not extending `services/knowledge_tracing.py`) | Architecture Patterns | Not a risk; planner's discretion per CONTEXT.md |
| A4 | `_prereq_turn_counter` as a module-level dict is sufficient for Phase 3 (single-worker assumption) | Pattern 3 | Multi-worker deployments will have inconsistent escalation cadence; acceptable for Phase 3 dev target |

---

## Open Questions

1. **A1: Precise supersedes unlock trigger**
   - What we know: D-14 says "p_mastery reaches bloom_target"; `bloom_target` is 1–6, `p_mastery` is 0.0–1.0
   - What's unclear: Is the trigger `p_mastery >= 0.95` (existing solid) or a Bloom→p_mastery mapping?
   - Recommendation: Default to `p_mastery >= 0.95` and document the assumption. Clarify with user at plan review if needed.

2. **A2: Session-start catch-up scope**
   - What we know: D-08 says "on next session start" to catch sessions that ended without `/end`
   - What's unclear: Does "next session start" mean catch-up for ALL previous un-extracted sessions or just the most recent one?
   - Recommendation: Implement for the most-recent ended session only. If the device was offline for weeks, catching up 30 sessions on start would be slow. One session catch-up is the correct scope.

3. **HIST-03 endpoint path conflict**
   - Current path: `GET /sessions/{child_id}` (child_id in path)
   - New path: `GET /sessions/{session_id}/turns` (session_id in path)
   - These are non-overlapping (the `/turns` suffix disambiguates). No conflict.

---

## Sources

### Primary (HIGH confidence)
- `services/tutor.py` (verified in this session) — `build_system_prompt()` signature, `SYSTEM_PROMPT_TEMPLATE`, `_format_mastery_context()` pattern
- `db/crud.py` (verified in this session) — `get_session_history()`, `update_interests()`, `create_session()` signatures
- `services/curriculum.py` (verified in this session) — `Topic` dataclass fields, `CURRICULUM` list size (870), `_by_id` dict, `next_topics()` pure function, `prerequisites_met()`, `supersedes` field usage (14 topics)
- `services/knowledge_tracing.py` (verified in this session) — `next_topics()` async wrapper, `mastery_context_for_prompt()`, `_mastery_bucket()`, `BUCKET_ORDER`
- `api/chat.py` (verified in this session) — current wiring, `mastery_ctx` pattern
- `api/sessions.py` (verified in this session) — `end_session()` full implementation
- `db/models.py` (verified in this session) — `InteractionEventModel` fields including `timestamp`, `topic`, `answer`, `session_id`
- `tests/conftest.py`, `tests/services/conftest.py` (verified in this session) — `db_session` fixture, `sys.path` pattern
- `tests/services/test_tutor.py` (verified in this session) — `_make_child()` pattern, backward-compat test style
- `.planning/phases/02-knowledge-tracing-backend/02-PATTERNS.md` (verified in this session) — all shared async/SQLAlchemy patterns

### Secondary (MEDIUM confidence)
- `.planning/phases/02-knowledge-tracing-backend/02-REVIEW.md` — CR-01, CR-02 pre-existing bugs; non-regression requirements

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new packages; all capabilities confirmed in existing codebase
- Architecture: HIGH — all integration points verified by reading source files
- Pitfalls: HIGH — drawn directly from code analysis (CR-01/CR-02) and scale measurements (870 topics, token counts)
- Assumptions: MEDIUM — A1 (bloom_target interpretation) is the one ambiguity that needs user confirmation

**Research date:** 2026-07-17
**Valid until:** 2026-08-17 (stable stack; CURRICULUM changes are the main staleness risk)
