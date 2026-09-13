# Phase 3: Session Intelligence - Context

**Gathered:** 2026-07-16
**Status:** Ready for planning

<domain>
## Phase Boundary

Make every chat turn aware of what this child has studied in the last 24 hours: inject a compact history block into the system prompt, enforce prerequisite ordering with a diagnostic "rubber band" pattern, extract interests from session turns, and surface a one-level-deep topic tree showing what each in-progress topic unlocks. No UI, no parent dashboard — pure backend intelligence wired into the existing prompt pipeline.

Requirements: HIST-01, HIST-02, HIST-03, CURR-01, CURR-02, CURR-03, CURR-04

</domain>

<decisions>
## Implementation Decisions

### History Summary (HIST-01)
- **D-01:** Inject a flat topic list (most recent first) as the 24-hour history block — no raw Q&A, no per-topic turn counts in v1. Format: `Recent topics: volcanoes, plate tectonics, igneous rocks`.
- **D-02:** Token cap for the history block: ~50 tokens (~5-8 topic names). Keeps system prompt well under 500 tokens total for Haiku latency target.
- **D-03:** Topics extracted from `InteractionEventModel.topic` field, deduplicated, ordered by `timestamp DESC`, limited to the past 24 hours.

### Prerequisite Enforcement (CURR-02)
- **D-04:** Rubber-band pattern — the tutor lets the child explore an unmastered-prerequisite topic but escalates the redirect over turns. The system prompt signals that this topic has unmet prerequisites and instructs escalating behavior.
- **D-05:** The prerequisite *assumption* is soft: the child may already know the prerequisite even if `p_mastery` is low. The escalation strategy is to **probe** understanding of the prerequisite, not to assume ignorance. If the child answers correctly, treat it as a mastery signal.
- **D-06:** Correct probe answer → (a) update `p_mastery` for the prerequisite KC in `mastery_state`, and (b) the tutor gives a quick refresher before proceeding to the originally requested topic. Both the mastery write and the refresher are required — the refresher cements the knowledge.
- **D-07:** Escalation cadence: Turn 1 = engage + hint ("to really get X, rock types matter"). Turn 2 = gentle probe ("let me check — what do you know about rock types?"). Turn 3+ = if still unmastered after probe, active steer: "Let's build up to this — I want to show you rock types first." This is tracked via a session-level counter per child×KC pair, not persisted to DB.

### Interest Extraction (CURR-03)
- **D-08:** Interest extraction runs at **both** session end (`POST /sessions/{id}/end`) AND on next session start — the dual trigger handles sessions that end without `/end` being called (device disconnect, browser close, etc.).
- **D-09:** Matching strategy: scan child answer text against `Topic.tags` from curriculum.py. If a tag appears in 2+ turns within a session, add the corresponding topic's name to `child_profile.interests`. Tag matching is case-insensitive substring. No NLP, no LLM call.
- **D-10:** Interest updates use existing `update_interests()` CRUD function. New interests are appended (no replacement) to avoid losing interests from prior sessions.

### Prerequisite Gap Surfacing (HIST-02)
- **D-11:** Surface a one-level-deep topic tree in the system prompt: for each topic in `next_topics()` that has unmet prerequisites, show `{prerequisite} → unlocks: {topic1}, {topic2}, ...`. This gives the tutor the learning path without deep recursion.
- **D-12:** Truncate the unlocks list at 3 topics per prerequisite to stay within the ~50-token budget for this block. Order by FSRS `next_review` urgency.
- **D-13:** Only show prerequisites that are currently `fragile` or `not_started` — skip prerequisites already `in_progress` or `solid`.

### supersedes Unlocking (CURR-04)
- **D-14:** When a child's `p_mastery` for a topic KC reaches its `bloom_target` (BKT), check if any topic has `supersedes = this_topic_id`. If so, add the superseding topic to `next_topics()` output automatically. This check runs inside `next_topics()` — no separate job needed.

### Claude's Discretion
- The exact SQL query structure for the 24-hour history lookup (whether to join `sessions` table or filter `InteractionEventModel.timestamp` directly) — leave to planner.
- Whether to create a new `services/session_intelligence.py` module or extend `services/knowledge_tracing.py` — leave to planner.
- Whether `HIST-03` (session turn log retrievable per session_id) requires a new endpoint or reuses existing `get_session_history()` — leave to planner.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Existing Service Layer
- `services/tutor.py` — `build_system_prompt()` (line ~242): the function Phase 3 extends; already accepts `mastery_context: Optional[list]`; Phase 3 adds `history_context`, `prereq_tree`, and `session_prereq_state` parameters
- `services/knowledge_tracing.py` — `next_topics()`, `mastery_context_for_prompt()`: Phase 3 wraps these with prerequisite-awareness
- `services/curriculum.py` — `Topic` dataclass: `prerequisites`, `supersedes`, `bloom_target`, `tags` fields are the data model for CURR-02, CURR-03, CURR-04

### Database Layer
- `db/crud.py` — `get_session_history()` (line ~161): returns `InteractionEventModel` list; `update_interests()` (line ~87): used by D-10; `log_turn()` (line ~125): Phase 3 does NOT change its signature
- `db/models.py` — `InteractionEventModel` fields: `topic`, `answer`, `timestamp`, `kc_id`, `correct`; `ChildProfileModel.interests` (JSON column)

### API
- `api/chat.py` — `chat()` endpoint (line ~39): where Phase 3's prompt enrichment is wired in; currently calls `mastery_context_for_prompt()` before `build_system_prompt()`
- `api/sessions.py` — `end_session()`: where D-08 interest extraction (fast path) goes

### Requirements
- `.planning/REQUIREMENTS.md` §HIST-01, HIST-02, HIST-03, CURR-01–04 — exact acceptance criteria

### Code Review Findings (Phase 2)
- `.planning/phases/02-knowledge-tracing-backend/02-REVIEW.md` — CR-01 (streaming generator/closed DB session) and CR-02 (IDOR on session endpoints) are known pre-existing bugs; Phase 3 must not make them worse and ideally avoids triggering them in new code

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `build_system_prompt(child, mastery_context)` in `services/tutor.py` — already parameterised; Phase 3 adds more optional params following the same pattern
- `next_topics(child_id, db, limit)` in `services/knowledge_tracing.py` — returns ranked `Topic` list; Phase 3 extends this to factor in `supersedes` unlock logic
- `update_interests(child_id, interests, session)` in `db/crud.py` — takes a list of interest strings; Phase 3 calls this at session end and session start
- `get_session_history(child_id, session, limit)` in `db/crud.py` — filters by `child_id`, returns ASC-ordered events; Phase 3 needs to filter by timestamp (last 24hr) in addition to limit

### Established Patterns
- `Optional[list]` parameter style (Python 3.9 compatible) for new `build_system_prompt` params — agent fixed `list | None` syntax in Phase 2
- SQLAlchemy `select().where().order_by().limit()` pattern throughout `db/crud.py` — use this for the 24hr history query
- `tests/services/conftest.py` provides `db_session` async fixture without `__init__.py` — Phase 3 tests follow this pattern
- `tests/api/` integration tests use `httpx.AsyncClient` with `app` from `api/main.py` — Phase 3 API tests follow this

### Integration Points
- `api/chat.py:chat()` — the primary wiring point; Phase 3 calls new intelligence functions before `build_system_prompt()`
- `api/sessions.py:end_session()` — interest extraction fast path (D-08)
- Session start (new session creation in `create_session()`) — interest extraction catch-up path (D-08)
- `services/knowledge_tracing.py:next_topics()` — Phase 3 adds `supersedes` unlock check here (D-14)

</code_context>

<specifics>
## Specific Ideas

- **Rubber-band metaphor** (D-04–D-07): "allow them to stray but the steer should start soft and then pull them back eventually" — the escalation is about discovering whether the child knows the prerequisite, not assuming they don't. The probe is the key mechanism.
- **Probe → mastery write + refresher** (D-06): when a child correctly answers a prerequisite probe, write the mastery update AND give a brief refresher — both are required. The refresher cements the knowledge and validates the unlock.
- **Dual-trigger interest extraction** (D-08): session end AND session start. The session-start path catches sessions that ended without `/end` (device disconnect). This is the key design choice.
- **Curriculum tag matching** (D-09): `Topic.tags` already exists in `curriculum.py` with rich tag lists per topic (e.g., 'volcano', 'eruption', 'lava', 'magma'). Use these tags for v1 matching — no NLP needed.

</specifics>

<deferred>
## Deferred Ideas

- **Vector-embedding interest graph** — REQUIREMENTS.md already lists this as v2. Keyword/tag matching is v1.
- **Deep prerequisite tree rendering** (2+ levels) — one level is sufficient for v1 token budget; deeper trees can be added in Phase 6 polish.
- **Per-turn interest extraction** — ruled out due to latency impact on every chat turn.

</deferred>

---

*Phase: 3-Session Intelligence*
*Context gathered: 2026-07-16*
