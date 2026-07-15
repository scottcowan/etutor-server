# Phase 2: Knowledge Tracing Backend - Context

**Gathered:** 2026-07-15
**Status:** Ready for planning

<domain>
## Phase Boundary

Build the knowledge tracing layer: closed-form BKT mastery updates, FSRS spaced-repetition scheduling (using fsrs-python with per-child parameter fitting), a DB-aware `next_topics()` function in a new `services/knowledge_tracing.py`, and mastery bucket injection into `services/tutor.py`'s system prompt. All in-scope work lives in new/extended service files — no changes to `services/curriculum.py`'s pure data functions.

</domain>

<decisions>
## Implementation Decisions

### BKT (Bayesian Knowledge Tracing)
- **D-01:** BKT updates are implemented as closed-form 4-equation updates in `services/knowledge_tracing.py`. No external BKT library. ~20 lines of Python, fully testable, upgradeable to simpleKT later.
- **D-02:** BKT parameters are updated **post-session in batch**, not per-turn. The trigger is a new `POST /sessions/{id}/end` endpoint. When called, it fetches all `interaction_events` for that `session_id` (where `kc_id` is not null and `correct` is not null), runs BKT updates for each KC, and writes updated `p_mastery` values back to `mastery_state`.
- **D-03:** The `/sessions/{id}/end` endpoint is the canonical session-close trigger for Phase 2. Phase 5 device sync will call this after a device session. Phase 3 may add other triggers.

### FSRS (Spaced Repetition Scheduling)
- **D-04:** Use the `fsrs-python` reference library. Do not re-implement the FSRS-5 algorithm. Add `fsrs-python` to `requirements.txt`.
- **D-05:** Default FSRS-5 global parameters are used as the starting point for all children. Per-child parameter fitting is attempted after **every session end** (when `/sessions/{id}/end` fires), using all available rated interaction history for that child. With sparse data (<50 interactions per KC) the fit will be noisy but directional — it improves as data accumulates.
- **D-06:** Per-child FSRS weights are stored in a new `child_fsrs_params` table with `child_id` as PK and a JSON column holding the fitted weight vector. One row per child, updated on each session end. Requires a new Alembic migration.

### next_topics() Design
- **D-07:** A new `async next_topics(child_id: str, session: AsyncSession, limit: int = 10) -> list[Topic]` function lives in `services/knowledge_tracing.py`. It does NOT replace `curriculum.py`'s `next_topics()` — that function stays as a pure data utility.
- **D-08:** Ranking order:
  1. **FSRS-due KCs first** — KCs whose `next_review` is today or overdue, sorted by how overdue (most overdue first).
  2. **Within the same urgency tier**, rank by mastery bucket: `fragile` before `in_progress` before `not_started`.
  3. **Deprioritise** solid KCs and KCs with future `next_review`.
  4. **Filter** by prerequisites met (call `curriculum.prerequisites_met()`) and age-gating.
- **D-09:** KCs with no mastery state row yet are treated as `not_started` with `next_review = today`. They are eligible but ranked after explicitly-due KCs.

### KT-05 Prompt Injection
- **D-10:** `build_system_prompt()` in `services/tutor.py` gains an optional `mastery_context: list[dict] | None = None` parameter. When `None`, prompt is unchanged (existing evals stay green). When provided, a new section is appended to the system prompt:
  ```
  Focus topics this session:
  - [topic name] (fragile — needs reinforcement)
  - [topic name] (due for review)
  - [topic name] (not yet started — prerequisites met)
  ```
- **D-11:** `api/chat.py` calls `next_topics(child_id, session, limit=5)` before `build_system_prompt()` and passes the result as `mastery_context`. Only the top 5 KCs from `next_topics()` are injected — keeps the prompt tight and actionable.

### Mastery Bucket Definitions
- **D-12:** Bucket thresholds (used in prompt labels and KT-05):
  - `not_started`: no mastery state row, or `p_mastery < 0.1`
  - `fragile`: `0.1 ≤ p_mastery < 0.7`
  - `in_progress`: `0.7 ≤ p_mastery < 0.95`
  - `solid`: `p_mastery ≥ 0.95`

### Claude's Discretion
- BKT default prior values (p_mastery=0.1, p_learn=0.2, p_slip=0.1, p_guess=0.2) — already set in MasteryStateModel; use these unless research finds better defaults.
- Exact FSRS-5 initialisation API (card creation, review rating mapping) — follow fsrs-python documentation.
- Whether per-child FSRS fitting uses the fsrs-python optimizer or a custom gradient step — researcher decides based on fsrs-python API.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Requirements
- `.planning/REQUIREMENTS.md` §KT-01 through KT-05 — the 5 KT requirements this phase must satisfy
- `.planning/ROADMAP.md` §Phase 2 — goal statement, success criteria, key decisions/risks

### Existing code to extend
- `db/models.py` — `MasteryStateModel` already has BKT + FSRS fields (Phase 1 scaffold); `child_fsrs_params` table is NEW (requires Alembic migration)
- `db/crud.py` — `create_or_get_mastery_state`, `update_mastery_state` already exist; new CRUD needed for FSRS params
- `services/tutor.py` — `build_system_prompt()` gains optional `mastery_context` param; read it before touching
- `services/curriculum.py` — `next_topics()`, `prerequisites_met()`, `get_topics_for_child()` are reusable pure functions; do NOT modify
- `api/chat.py` — call `next_topics()` before `build_system_prompt()` and pass mastery_context; already injects session

### Evals (must stay green — KT-05 must not break them)
- `tests/evals/test_answer_reveal.py`
- `tests/evals/test_hint_ladder.py`
- `tests/evals/test_socratic_quality.py`
- `tests/evals/test_lesson_questions.py`
- `tests/evals/test_curriculum_accuracy.py`

### External library
- `fsrs-python` — not yet in `requirements.txt`; researcher should verify current PyPI version and API

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `MasteryStateModel` in `db/models.py`: BKT fields (p_mastery, p_learn, p_slip, p_guess) + FSRS fields (stability, difficulty_d, card_state, next_review) already defined — Phase 2 populates them
- `create_or_get_mastery_state(child_id, kc_id, session)` in `db/crud.py`: creates row with BKT defaults on first access — use this as the upsert entrypoint
- `update_mastery_state(child_id, kc_id, session, **fields)` in `db/crud.py`: generic field updater — use for BKT and FSRS writes
- `curriculum.prerequisites_met(topic_id, mastered_ids)` in `services/curriculum.py`: pure function, accepts list of mastered topic IDs — call with IDs where `p_mastery >= 0.95`
- `curriculum.get_topics_for_child(child, mastered_ids, ...)` in `services/curriculum.py`: returns age/interest filtered candidate topics — use as input to `next_topics()` ranking
- `Depends(get_db)` pattern: established in Phase 1 — all new routes and service calls follow same session injection pattern

### Established Patterns
- All new service functions are `async` and accept `session: AsyncSession` as explicit argument
- New routes follow `api/{name}.py` pattern with `router = APIRouter()` and `Depends(get_db)`
- TDD mode is on — write failing tests first for BKT math, FSRS scheduling, and `next_topics()` ranking

### Integration Points
- `api/chat.py` line ~50: `build_system_prompt(child)` call — gains `mastery_context=` kwarg here
- `api/sessions.py`: `GET /sessions/{child_id}` already exists — new `POST /sessions/{id}/end` route goes in same file or new `api/knowledge_tracing.py`
- `db/models.py`: needs one new model (`ChildFSRSParamsModel`) and one new Alembic migration

</code_context>

<specifics>
## Specific Ideas

- The `/sessions/{id}/end` endpoint is the single trigger for both BKT batch update AND per-child FSRS re-fitting. Both happen in the same request handler.
- Mastery context injected into prompts should use plain language bucket labels, not numeric p_mastery values — the LLM understands "fragile" better than "p_mastery=0.43".

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 2-Knowledge Tracing Backend*
*Context gathered: 2026-07-15*
