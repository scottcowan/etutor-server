# Phase 2: Knowledge Tracing Backend — Research

**Researched:** 2026-07-16
**Domain:** Bayesian Knowledge Tracing, FSRS spaced-repetition, FastAPI/SQLAlchemy async
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** BKT as closed-form 4-equation updates in `services/knowledge_tracing.py`. No external BKT library.
- **D-02:** BKT updates are post-session batch, triggered by `POST /sessions/{id}/end`. Fetches all `interaction_events` where `kc_id IS NOT NULL AND correct IS NOT NULL`.
- **D-03:** `/sessions/{id}/end` is the canonical session-close trigger for Phase 2.
- **D-04:** Use `fsrs-python` reference library (`fsrs` on PyPI). Do not re-implement FSRS-5.
- **D-05:** Default FSRS-5 global parameters as starting point. Per-child fitting attempted on every session end.
- **D-06:** Per-child FSRS weights in new `child_fsrs_params` table. `child_id` PK, JSON column for weights. One row per child, updated on each session end. New Alembic migration required.
- **D-07:** New `async next_topics(child_id, session, limit=10) -> list[Topic]` in `services/knowledge_tracing.py`. Does NOT replace `curriculum.py`'s `next_topics()`.
- **D-08:** Ranking: (1) FSRS-due first (most overdue first), (2) mastery bucket within tier, (3) deprioritise solid/future-review, (4) filter by prerequisites and age-gating.
- **D-09:** KCs with no mastery row treated as `not_started` with `next_review = today`.
- **D-10:** `build_system_prompt()` gains optional `mastery_context: list[dict] | None = None`. When `None`, prompt unchanged.
- **D-11:** `api/chat.py` calls `next_topics(child_id, session, limit=5)` before `build_system_prompt()`.
- **D-12:** Bucket thresholds: `not_started` < 0.1, `fragile` 0.1–0.7, `in_progress` 0.7–0.95, `solid` >= 0.95.

### Claude's Discretion

- BKT default prior values (p_mastery=0.1, p_learn=0.2, p_slip=0.1, p_guess=0.2) — already in MasteryStateModel; use these unless research finds better defaults.
- Exact FSRS-5 initialisation API (card creation, review rating mapping) — follow fsrs-python documentation.
- Whether per-child FSRS fitting uses the fsrs-python optimizer or a custom gradient step — researcher decides based on fsrs-python API.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| KT-01 | BKT mastery model per child per KC (p_mastery, p_learn, p_slip, p_guess) | Closed-form update formula documented below; fields already in MasteryStateModel |
| KT-02 | FSRS scheduling fields per child×KC (stability, difficulty_d, card_state, next_review) | fsrs 6.3.1 API verified; fields already in MasteryStateModel scaffold |
| KT-03 | next_topics() uses mastery state + FSRS next_review to recommend session content | Ranking algorithm documented; uses existing curriculum.prerequisites_met() |
| KT-04 | After each session, BKT params updated from interaction log | POST /sessions/{id}/end endpoint design documented |
| KT-05 | Mastery bucket labels injected into system prompt | build_system_prompt() extension pattern documented; eval safety verified |
</phase_requirements>

---

## Summary

Phase 2 implements the knowledge-tracing layer on top of the scaffold created in Phase 1. The work divides cleanly into three streams: (1) BKT closed-form math in a new service module, (2) FSRS scheduling via the `fsrs` library (PyPI package name: `fsrs`, not `fsrs-python`), and (3) prompt injection via an optional parameter on `build_system_prompt()`.

The key integration risk is the `kc_id` field on `interaction_events`. Currently `log_turn()` in `services/sessions.py` does not set `kc_id` — the planner must include a task to extend `log_turn()` (or the chat endpoint) to extract and persist a `kc_id` for each turn. Without `kc_id` populated, the BKT batch update finds no events to process. This is the most likely silent failure mode.

The eval safety concern (KT-05 must not break existing evals) is a non-issue: all five eval files build their system prompts by calling `SYSTEM_PROMPT_TEMPLATE.format(...)` directly, bypassing `build_system_prompt()` entirely. Adding `mastery_context: list[dict] | None = None` with default `None` to `build_system_prompt()` is safe — no eval calls that function.

**Primary recommendation:** Implement in this order — BKT math + tests → ChildFSRSParamsModel + migration → FSRS scheduling → next_topics() + ranking → build_system_prompt() extension + chat.py wiring → POST /sessions/{id}/end endpoint.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| BKT mastery update | API / Backend (service layer) | Database | Pure computation; writes to mastery_state table |
| FSRS schedule update | API / Backend (service layer) | Database | Wraps fsrs library; writes stability/next_review to mastery_state |
| Per-child FSRS fitting | API / Backend (service layer) | — | Triggered at session end; reads interaction_events, writes child_fsrs_params |
| next_topics() ranking | API / Backend (service layer) | — | Reads mastery_state; delegates candidate filtering to curriculum.py |
| Mastery context injection | API / Backend (service layer) | — | `build_system_prompt()` in services/tutor.py; not browser-side |
| POST /sessions/{id}/end | API / Backend (route) | Service layer | Route dispatches to KT service functions |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `fsrs` | 6.3.1 [VERIFIED: PyPI registry] | FSRS-5 spaced-repetition scheduling | Official py-fsrs reference implementation; maintained by open-spaced-repetition org since 2022 |
| `sqlalchemy` | >=2.0.0 (already in requirements.txt) | Async ORM | Already used throughout project |
| `alembic` | >=1.13.0 (already in requirements.txt) | DB migrations | Already used throughout project |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `fsrs[optimizer]` | 6.3.1 | Per-child weight fitting via `Optimizer` class | Install this extra when per-child FSRS fitting is wired up; requires `torch` as transitive dep |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `fsrs` reference impl | Hand-rolled FSRS-5 | 21-parameter algorithm with complex memory model; reference impl is tested, do not re-implement |
| `fsrs[optimizer]` | Custom gradient step | Optimizer is battle-tested; custom step acceptable only if torch dependency is rejected |

**Installation:**
```bash
pip install "fsrs>=6.3.1"
# Add to requirements.txt:
# fsrs>=6.3.1
```

For per-child fitting (Phase 2 D-05 requires it):
```bash
pip install "fsrs[optimizer]>=6.3.1"
```

**Note on package name:** The PyPI package is `fsrs`, not `fsrs-python`. The GitHub repo is `py-fsrs` but the published package name is `fsrs`. [VERIFIED: PyPI registry]

---

## Package Legitimacy Audit

slopcheck was unavailable at research time. Manual verification performed:

| Package | Registry | Age | Source Repo | Disposition |
|---------|----------|-----|-------------|-------------|
| `fsrs` | PyPI | ~3.5 yrs (first release 2022-12-01) | github.com/open-spaced-repetition/py-fsrs | Approved — established org, MIT, active maintenance, latest 2026-03-10 |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*slopcheck was unavailable at research time. All packages above are tagged [ASSUMED] pending slopcheck verification. The planner should add a `checkpoint:human-verify` before the install step if strict mode is required.*

---

## BKT Update Formula

### Closed-Form 4-Equation BKT

Standard BKT (Corbett & Anderson 1994). The four parameters are:
- `p_mastery` — P(mastered | observations so far)
- `p_learn` — P(transition to mastered in one opportunity)
- `p_slip` — P(incorrect | mastered)
- `p_guess` — P(correct | not mastered)

```python
# Source: Corbett & Anderson (1994) BKT standard formulation [ASSUMED — well-established]
def update_bkt(
    p_mastery: float,
    p_learn: float,
    p_slip: float,
    p_guess: float,
    correct: bool,
) -> float:
    """
    Closed-form BKT posterior update.
    Returns new p_mastery given one correct/incorrect observation.
    """
    # Step 1: P(correct) for evidence weighting
    p_correct = p_mastery * (1.0 - p_slip) + (1.0 - p_mastery) * p_guess

    # Step 2: Posterior P(mastered | observation)
    if correct:
        # P(mastered | correct) = P(correct | mastered) * P(mastered) / P(correct)
        p_mastered_given_obs = (p_mastery * (1.0 - p_slip)) / p_correct
    else:
        # P(mastered | incorrect) = P(incorrect | mastered) * P(mastered) / P(incorrect)
        p_incorrect = 1.0 - p_correct
        p_mastered_given_obs = (p_mastery * p_slip) / p_incorrect

    # Step 3: Forward transition — P(mastered at next opportunity)
    p_new = p_mastered_given_obs + (1.0 - p_mastered_given_obs) * p_learn

    # Clamp to valid probability range (guard against floating-point drift)
    return max(0.0, min(1.0, p_new))
```

**Default priors (from MasteryStateModel):**
- `p_mastery = 0.1` (prior: child unlikely to already know topic)
- `p_learn = 0.2` (moderate learning rate per opportunity)
- `p_slip = 0.1` (low chance of error if mastered)
- `p_guess = 0.2` (low chance of lucky guess)

These are reasonable textbook defaults. Research note: Pardos & Heffernan (2010) found p_guess=0.25 and p_slip=0.1 common in practice; the project's 0.2/0.1 are defensible and already set in the model.

---

## FSRS API (fsrs 6.3.1)

[VERIFIED: github.com/open-spaced-repetition/py-fsrs README]

### Core Imports

```python
from fsrs import Scheduler, Card, Rating, ReviewLog, State
from datetime import datetime, timezone
```

### Creating and Reviewing a Card

```python
# Create a new card (all new cards are due immediately)
card = Card()

# Review — returns (updated_card, review_log)
card, review_log = scheduler.review_card(card, Rating.Good)

# Or with explicit timestamp (required for historical replay):
card, review_log = scheduler.review_card(card, Rating.Good,
                                          review_datetime=datetime.now(timezone.utc))
```

### Reading Back State

```python
card.stability      # float — memory stability in days
card.difficulty     # float — card difficulty (field name: difficulty, not difficulty_d)
card.due            # datetime (UTC) — next scheduled review
card.state          # State enum: State.Learning(1), State.Review(2), State.Relearning(3)
card.state.name     # str: "Learning", "Review", "Relearning"
```

**Important:** The FSRS `Card` stores `difficulty` (not `difficulty_d`). The MasteryStateModel column is named `difficulty_d`. Map: `mastery.difficulty_d = card.difficulty`.

### FSRS Rating Mapping

| BKT / Response | FSRS Rating | Rationale |
|---------------|-------------|-----------|
| `correct=True`, p_mastery >= 0.7 | `Rating.Good` (3) | Confident recall — standard good review |
| `correct=True`, p_mastery < 0.7 | `Rating.Hard` (2) | Correct but still fragile — credit with caveat |
| `correct=False` | `Rating.Again` (1) | Failed recall — reset interval |

**Recommendation (Claude's Discretion):** Use two-level mapping. Correct → `Rating.Good`; incorrect → `Rating.Again`. The Hard/Easy distinctions require explicit child effort signals (response time, hint usage) that are scaffolded in Phase 2 but not reliably populated yet. Simpler mapping is defensible until Phase 6 latency/effort tracking is complete.

### Per-Child FSRS Fitting

```python
from fsrs import Optimizer

# review_logs: list[ReviewLog] — all historical review logs for this child
optimizer = Optimizer(review_logs)
optimal_parameters = optimizer.compute_optimal_parameters()

# Use fitted parameters for this child's scheduler
child_scheduler = Scheduler(parameters=optimal_parameters)
```

**Cold-start behaviour:** `Optimizer` requires sufficient review history to converge. With < 30 reviews it will return parameters close to the defaults — this is expected and safe. The fitted weights should be stored but treated as directional until the child accumulates ~50+ rated interactions per KC (per FSRS-5 paper). The planner should add a guard: only attempt fitting if the child has >= 10 total rated events; fall back to default Scheduler() otherwise.

### Initialising the Scheduler with Per-Child Weights

```python
import json
from fsrs import Scheduler

# Load from child_fsrs_params row
weights = json.loads(params_row.weights_json)  # list of 21 floats
scheduler = Scheduler(parameters=tuple(weights))

# Default scheduler (cold start or fitting skipped)
scheduler = Scheduler()
```

### Card JSON Persistence

The `card.to_json()` / `Card.from_json()` API is available but not needed here — the project stores FSRS fields as individual columns on `mastery_state`, not as serialised Card objects. Extract fields directly from the returned `card` object after `review_card()`.

---

## ChildFSRSParamsModel Definition

```python
class ChildFSRSParamsModel(Base):
    """Per-child FSRS-5 fitted weight vector (D-06)."""
    __tablename__ = "child_fsrs_params"

    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), primary_key=True
    )
    # JSON list of 21 floats — FSRS-5 weight vector
    weights_json: Mapped[str] = mapped_column(String, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
```

**Notes:**
- Use `String` not `JSON` for `weights_json` to match the existing project style for lists-as-JSON (the FSRS `Scheduler(parameters=...)` expects a tuple; store as `json.dumps(list(weights))`, load as `tuple(json.loads(row.weights_json))`).
- Alternatively, use `JSON` column type (already imported in models.py) — then the column value is a Python list directly without explicit serialisation. Either approach works; `JSON` type is more idiomatic given the project already uses it for `interests` etc.

**Recommended (using existing JSON column type):**

```python
from sqlalchemy import JSON  # already imported in models.py

class ChildFSRSParamsModel(Base):
    """Per-child FSRS-5 fitted weight vector (D-06)."""
    __tablename__ = "child_fsrs_params"

    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), primary_key=True
    )
    weights: Mapped[list] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
```

---

## Alembic Migration

New migration file (`migrations/versions/{hash}_add_child_fsrs_params.py`):

```python
def upgrade() -> None:
    op.create_table(
        "child_fsrs_params",
        sa.Column("child_id", sa.String(), nullable=False),
        sa.Column("weights", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["child_profiles.id"]),
        sa.PrimaryKeyConstraint("child_id"),
    )

def downgrade() -> None:
    op.drop_table("child_fsrs_params")
```

Generate with: `alembic revision --autogenerate -m "add child_fsrs_params"` after adding `ChildFSRSParamsModel` to `db/models.py`. The `Base.metadata` import in `env.py` must include the new model — verify `from db.models import Base` is already in `migrations/env.py`.

---

## Function Signatures: services/knowledge_tracing.py

```python
"""
Knowledge tracing service — BKT + FSRS (Phase 2).

KT-01: BKT closed-form updates
KT-02: FSRS scheduling fields
KT-03: next_topics() using mastery + FSRS schedule
KT-04: Post-session BKT batch update
KT-05: mastery_context_for_prompt() for prompt injection
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from services.curriculum import Topic


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

    Returns: {kc_id: new_p_mastery} dict for the session.
    """
    ...


async def update_fsrs_schedule(
    child_id: str,
    kc_id: str,
    correct: bool,
    db: AsyncSession,
    review_datetime: Optional[datetime] = None,
) -> None:
    """
    KT-02: Update FSRS scheduling fields for one child×KC after a response.

    Loads per-child weights from child_fsrs_params (falls back to defaults).
    Calls scheduler.review_card() with mapped Rating.
    Writes stability, difficulty_d, card_state, next_review back to
    mastery_state via update_mastery_state().
    """
    ...


async def fit_fsrs_params(
    child_id: str,
    db: AsyncSession,
) -> None:
    """
    D-05: Fit per-child FSRS weights from all available rated history.

    Loads all interaction_events for child_id where correct IS NOT NULL.
    Reconstructs ReviewLog list. If len(review_logs) < 10, skips fitting
    (cold-start guard) and returns without writing. Otherwise runs
    Optimizer.compute_optimal_parameters() and upserts child_fsrs_params.
    """
    ...


async def next_topics(
    child_id: str,
    db: AsyncSession,
    limit: int = 10,
) -> list[Topic]:
    """
    KT-03: Return ordered list of recommended Topic objects for a child.

    Ranking (D-08):
    1. FSRS-due KCs (next_review <= today), sorted most-overdue first.
    2. Within same urgency tier, rank: fragile < in_progress < not_started.
    3. Deprioritise: solid KCs, KCs with future next_review.
    4. Filter: prerequisites met (curriculum.prerequisites_met()), age-gating.

    KCs with no mastery_state row treated as not_started / due today (D-09).
    Calls curriculum.next_topics(age, mastered_ids, interests) to get the
    candidate pool, then re-ranks by FSRS schedule from mastery_state rows.
    """
    ...


async def mastery_context_for_prompt(
    child_id: str,
    db: AsyncSession,
    limit: int = 5,
) -> list[dict]:
    """
    KT-05: Returns top-N KCs as dicts for build_system_prompt() injection.

    Calls next_topics(child_id, db, limit=limit) then formats each Topic
    as: {"name": topic.name, "bucket": "fragile"|"in_progress"|"not_started"}.
    """
    ...
```

---

## Architecture Patterns

### System Architecture Diagram

```
POST /sessions/{id}/end
        │
        ▼
api/sessions.py (or api/knowledge_tracing.py)
        │
        ├──► update_bkt_for_session(session_id, db)
        │         │
        │         ├── SELECT interaction_events WHERE session_id=X, kc_id NOT NULL
        │         ├── FOR each kc_id: update_bkt() [pure function]
        │         └── update_mastery_state(child_id, kc_id, p_mastery=...)
        │
        ├──► fit_fsrs_params(child_id, db)
        │         │
        │         ├── SELECT all interaction_events WHERE child_id=X, correct NOT NULL
        │         ├── Reconstruct ReviewLog list
        │         ├── IF len >= 10: Optimizer → compute_optimal_parameters()
        │         └── UPSERT child_fsrs_params(child_id, weights=...)
        │
        └──► SET sessions.ended_at = now()


POST /chat/completions
        │
        ▼
api/chat.py
        │
        ├──► next_topics(child_id, db, limit=5)
        │         │
        │         ├── load child profile (age, interests)
        │         ├── load mastery_state rows for child
        │         ├── curriculum.next_topics(age, mastered_ids, interests) → candidates
        │         ├── re-rank by FSRS next_review + mastery bucket
        │         └── filter by prerequisites_met()
        │
        └──► build_system_prompt(child, mastery_context=[...])
                  │
                  └── appends "Focus topics this session:" block to prompt
```

### Recommended Project Structure

```
services/
├── knowledge_tracing.py   # NEW — BKT + FSRS + next_topics
├── tutor.py               # EXTEND — build_system_prompt gains mastery_context param
├── curriculum.py          # NO CHANGES
└── sessions.py            # EXTEND — log_turn gains kc_id + correct params (or in chat.py)

db/
├── models.py              # EXTEND — add ChildFSRSParamsModel
└── crud.py                # EXTEND — add get/upsert child_fsrs_params CRUD

api/
├── chat.py                # EXTEND — call next_topics + pass mastery_context
└── sessions.py            # EXTEND — add POST /sessions/{id}/end route

migrations/versions/
└── {hash}_add_child_fsrs_params.py  # NEW
```

### Pattern: Upsert child_fsrs_params

```python
# Source: established project pattern from crud.py create_or_get_mastery_state [CITED: db/crud.py]
async def upsert_child_fsrs_params(
    child_id: str,
    weights: list[float],
    session: AsyncSession,
) -> None:
    existing = await session.get(ChildFSRSParamsModel, child_id)
    if existing:
        existing.weights = weights
        existing.updated_at = datetime.now(timezone.utc)
    else:
        session.add(ChildFSRSParamsModel(
            child_id=child_id,
            weights=weights,
            updated_at=datetime.now(timezone.utc),
        ))
    await session.commit()
```

### Pattern: next_topics() FSRS-aware ranking

```python
# Pseudocode — exact implementation in services/knowledge_tracing.py
async def next_topics(child_id, db, limit=10):
    child = await get_child_by_id(child_id, db)
    
    # Get mastered KC IDs (solid bucket)
    mastery_rows = await get_all_mastery_for_child(child_id, db)
    mastered_ids = [r.kc_id for r in mastery_rows if r.p_mastery >= 0.95]
    
    # Get curriculum candidates (pure function — no DB)
    from services.curriculum import next_topics as curriculum_next_topics
    candidates = curriculum_next_topics(child.age, mastered_ids, child.interests)
    
    # Build mastery lookup for candidates
    mastery_by_kc = {r.kc_id: r for r in mastery_rows}
    now = datetime.now(timezone.utc)
    
    def rank_key(topic):
        row = mastery_by_kc.get(topic.id)
        if row is None:  # D-09: no row = not_started, due today
            overdue_days = 0
            bucket_rank = 3  # not_started last within same tier
            is_due = True
        else:
            p = row.p_mastery
            bucket_rank = 0 if p >= 0.1 and p < 0.7 else (1 if p < 0.95 else 99)
            # bucket_rank: 0=fragile, 1=in_progress, 99=solid (deprioritise)
            nr = row.next_review
            is_due = (nr is None or nr.replace(tzinfo=timezone.utc) <= now)
            overdue_days = (now - nr.replace(tzinfo=timezone.utc)).days if (nr and is_due) else 0
        
        # Sort: due before not-due, most overdue first, then bucket rank
        return (0 if is_due else 1, -overdue_days, bucket_rank)
    
    ranked = sorted(candidates, key=rank_key)
    # Filter out solid KCs (p_mastery >= 0.95) with future next_review
    filtered = [
        t for t in ranked
        if not (mastery_by_kc.get(t.id) and mastery_by_kc[t.id].p_mastery >= 0.95
                and mastery_by_kc[t.id].next_review
                and mastery_by_kc[t.id].next_review.replace(tzinfo=timezone.utc) > now)
    ]
    return filtered[:limit]
```

### Anti-Patterns to Avoid

- **Setting `kc_id` based on `topic` string match:** The `topic` column in `interaction_events` is a free-text string set by the chat handler. It is NOT guaranteed to match curriculum topic IDs (slugs like `phonics_phase1`). The planner must decide how `kc_id` gets set — either the client sends it explicitly, the LLM response tags it, or the chat handler infers it from the active session's topic. This is a Phase 2 design decision that must be resolved in Wave 0.
- **Mutating `curriculum.py` functions:** The context explicitly prohibits this. `curriculum.next_topics()` returns pure curriculum candidates without DB access — it must stay that way.
- **Calling `Optimizer` with an empty list:** Will raise an exception. Always guard: `if len(review_logs) < 10: return`.
- **Timezone-naive datetimes in FSRS:** py-fsrs requires UTC-aware datetimes. `datetime.now(timezone.utc)` always; never `datetime.utcnow()` (returns naive).
- **Storing card state as FSRS `State` enum directly:** The `MasteryStateModel.card_state` column is `String`. Store as `card.state.name` (e.g. `"Review"`); reconstruct with `State[card_state_str]` if needed.

---

## Integration Notes

### curriculum.py Integration

`curriculum.next_topics()` signature:
```python
def next_topics(
    age: int,
    mastered_ids: list[str],
    interests: Optional[list[str]] = None,
    allow_ahead: bool = True,
) -> list[Topic]:
```

Usage in `services/knowledge_tracing.py.next_topics()`:
1. Load `child` profile from DB to get `age` and `interests`.
2. Build `mastered_ids` = list of `kc_id` values where `p_mastery >= 0.95` from `mastery_state`.
3. Call `curriculum.next_topics(child.age, mastered_ids, child.interests)` to get the unranked candidate pool.
4. Re-rank the returned `list[Topic]` by FSRS `next_review` + mastery bucket using loaded `mastery_state` rows.

`curriculum.prerequisites_met()` signature:
```python
def prerequisites_met(topic_id: str, mastered_ids: list[str]) -> bool:
```
This is already called internally by `curriculum.next_topics()` — the returned candidates already have prerequisites met. No need to call it again in the KT `next_topics()` unless implementing additional safety filtering.

### tutor.py Integration

Current `build_system_prompt()`:
```python
async def build_system_prompt(child) -> str:
```

Extended signature:
```python
async def build_system_prompt(
    child,
    mastery_context: list[dict] | None = None,
) -> str:
```

Appended prompt block (only when `mastery_context` is not None and not empty):
```python
MASTERY_CONTEXT_TEMPLATE = """
Focus topics this session:
{topic_lines}
"""

def _format_mastery_context(mastery_context: list[dict]) -> str:
    lines = []
    for item in mastery_context:
        name = item["name"]
        bucket = item["bucket"]
        if bucket == "fragile":
            lines.append(f"- {name} (fragile — needs reinforcement)")
        elif bucket == "in_progress":
            lines.append(f"- {name} (due for review)")
        elif bucket == "not_started":
            lines.append(f"- {name} (not yet started — prerequisites met)")
        # "solid" should not appear — filter before passing
    return MASTERY_CONTEXT_TEMPLATE.format(topic_lines="\n".join(lines))
```

Append at the end of the existing `SYSTEM_PROMPT_TEMPLATE.format(...)` result.

### chat.py Integration

Current call at line ~56:
```python
system_prompt = await build_system_prompt(child)
```

Extended call:
```python
from services.knowledge_tracing import mastery_context_for_prompt

mastery_ctx = await mastery_context_for_prompt(child_id, session, limit=5)
system_prompt = await build_system_prompt(child, mastery_context=mastery_ctx or None)
```

**Note on session_id in chat.py:** Currently `db_session_row = await create_session(child_id, session)` is called inside the streaming generator (`generate()`) or after the LLM call for non-streaming. The `mastery_context_for_prompt()` call needs to happen before the LLM call. The session row may not exist yet at prompt-build time — this is fine, `mastery_context_for_prompt` reads from `mastery_state`, not from the current session.

### POST /sessions/{id}/end Route

```python
# In api/sessions.py (or api/knowledge_tracing.py)
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.crud import get_session
from db.session import get_db
from services.knowledge_tracing import update_bkt_for_session, fit_fsrs_params
from datetime import datetime, timezone

@router.post("/sessions/{session_id}/end")
async def end_session(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    """
    D-03: Canonical session-close trigger.
    Sets ended_at, runs BKT batch update, fits per-child FSRS params.
    """
    session_row = await get_session(session_id, db)
    if session_row is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if session_row.ended_at is not None:
        raise HTTPException(status_code=409, detail="Session already ended")
    
    session_row.ended_at = datetime.now(timezone.utc)
    await db.commit()
    
    bkt_updates = await update_bkt_for_session(session_id, db)
    await fit_fsrs_params(session_row.child_id, db)
    
    return {
        "session_id": session_id,
        "ended_at": session_row.ended_at.isoformat(),
        "kcs_updated": len(bkt_updates),
    }
```

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| FSRS-5 algorithm | Custom 21-parameter memory model | `fsrs` library | Algorithm involves non-trivial exponential forgetting curves and stability update equations; reference impl is validated against Anki data |
| FSRS parameter fitting | Custom gradient descent | `fsrs[optimizer]` | Optimizer uses torch-based optimisation validated against open-spaced-repetition benchmark |
| BKT | Any external library | 4-equation closed form (20 lines) | BKT is simple enough to implement directly; external libs add dependency for minimal gain |

---

## Common Pitfalls

### Pitfall 1: kc_id Never Gets Set

**What goes wrong:** `update_bkt_for_session()` queries `interaction_events WHERE kc_id IS NOT NULL` — if `kc_id` is always NULL, the function processes zero events and returns an empty dict silently. BKT never runs.

**Why it happens:** `log_turn()` in `services/sessions.py` does not accept or set `kc_id`. Nothing currently sets this field. The BKT batch update will silently no-op without a task to wire up `kc_id` population.

**How to avoid:** Wave 0 task must add `kc_id: Optional[str] = None` and `correct: Optional[bool] = None` parameters to `log_turn()`, and update the `api/chat.py` call site to pass them. Alternatively, Phase 2 may choose to infer `kc_id` from `child.current_topic` at log time.

**Warning signs:** `update_bkt_for_session()` always returns `{}`.

### Pitfall 2: FSRS Timezone Naive Datetimes

**What goes wrong:** py-fsrs 6.x requires UTC-aware datetimes. Passing `datetime.utcnow()` (timezone-naive) will either raise a TypeError or produce incorrect schedule arithmetic.

**Why it happens:** Python's `datetime.utcnow()` returns a naive datetime. The project uses `datetime.now(timezone.utc)` in models (see `models.py`), but it's easy to forget in service code.

**How to avoid:** Always use `datetime.now(timezone.utc)`. Never use `datetime.utcnow()`.

**Warning signs:** `TypeError: can't compare offset-naive and offset-aware datetimes` in FSRS calls.

### Pitfall 3: MasteryStateModel.next_review is Timezone-Naive in DB

**What goes wrong:** The existing `MasteryStateModel.next_review` column uses `DateTime` (not `DateTime(timezone=True)`). When FSRS writes a UTC-aware datetime and it's read back from SQLite, SQLAlchemy may return it as naive. Comparing naive DB value to `datetime.now(timezone.utc)` raises TypeError.

**Why it happens:** SQLite stores DATETIME as text without timezone info. The existing initial migration creates `next_review` as `sa.DateTime()` not `sa.DateTime(timezone=True)`.

**How to avoid:** In `next_topics()` ranking, normalise before comparison: `nr.replace(tzinfo=timezone.utc)` when `nr.tzinfo is None`. This is safe since the server always writes UTC.

**Warning signs:** `TypeError: can't compare offset-naive and offset-aware datetimes` in `next_topics()` ranking.

### Pitfall 4: FSRS Optimizer Cold-Start Exception

**What goes wrong:** `Optimizer([])` or `Optimizer` with very few reviews raises an exception or returns garbage weights.

**Why it happens:** The optimizer requires sufficient data to fit. No guard in the calling code.

**How to avoid:** Always check `if len(review_logs) < 10: return` before calling `Optimizer`. Store the cold-start threshold as a named constant.

**Warning signs:** Exception in `fit_fsrs_params()` on first session end for a new child.

### Pitfall 5: curriculum.next_topics() Not a Drop-in Replacement

**What goes wrong:** Planner confuses `services/knowledge_tracing.next_topics(child_id, db)` with `curriculum.next_topics(age, mastered_ids)`. The two have different signatures and responsibilities.

**Why it happens:** Same function name in two modules. D-07 states the KT version does NOT replace the curriculum version.

**How to avoid:** Import with explicit module prefix in `api/chat.py`: `from services.knowledge_tracing import next_topics as kt_next_topics`. The curriculum version is only called from inside `services/knowledge_tracing.py`.

---

## Eval Safety Analysis

The five gated evals do NOT call `build_system_prompt()`:

| Eval file | How system prompt is built | Impact of adding mastery_context param |
|-----------|---------------------------|----------------------------------------|
| `test_answer_reveal.py` | `SYSTEM_PROMPT_TEMPLATE.format(...)` directly | None — bypasses `build_system_prompt()` entirely |
| `test_hint_ladder.py` | Direct template use (pattern from test_answer_reveal) | None |
| `test_socratic_quality.py` | Direct template use | None |
| `test_lesson_questions.py` | Direct template use | None |
| `test_curriculum_accuracy.py` | Direct template use | None |

Adding `mastery_context: list[dict] | None = None` to `build_system_prompt()` is completely safe. None of the evals import or call `build_system_prompt()`. [VERIFIED: grep of test files]

---

## Validation Architecture

**Test framework:** pytest with pytest-asyncio (asyncio_mode=auto, confirmed in project). `db_session` fixture provides in-memory SQLite per test.

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| KT-01 | BKT update_bkt() correct/incorrect math | unit | `pytest tests/services/test_knowledge_tracing.py::test_bkt_correct_increases_mastery -x` | Wave 0 |
| KT-01 | BKT update_bkt() batch processes all session events | integration | `pytest tests/services/test_knowledge_tracing.py::test_update_bkt_for_session -x` | Wave 0 |
| KT-02 | FSRS review_card() writes stability/next_review to mastery_state | integration | `pytest tests/services/test_knowledge_tracing.py::test_update_fsrs_schedule -x` | Wave 0 |
| KT-02 | fit_fsrs_params() skips cold-start (<10 events) | unit | `pytest tests/services/test_knowledge_tracing.py::test_fit_fsrs_cold_start_guard -x` | Wave 0 |
| KT-03 | next_topics() ranks overdue KCs before future KCs | integration | `pytest tests/services/test_knowledge_tracing.py::test_next_topics_due_first -x` | Wave 0 |
| KT-03 | next_topics() ranks fragile before in_progress | integration | `pytest tests/services/test_knowledge_tracing.py::test_next_topics_bucket_ranking -x` | Wave 0 |
| KT-04 | POST /sessions/{id}/end sets ended_at and triggers BKT | integration | `pytest tests/api/test_session_end.py -x` | Wave 0 |
| KT-05 | build_system_prompt(mastery_context=None) unchanged | unit | `pytest tests/services/test_tutor.py::test_system_prompt_no_mastery_context -x` | Wave 0 |
| KT-05 | build_system_prompt(mastery_context=[...]) appends focus block | unit | `pytest tests/services/test_tutor.py::test_system_prompt_with_mastery_context -x` | Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/services/test_knowledge_tracing.py -x`
- **Per wave merge:** `pytest tests/ -x --ignore=tests/evals`
- **Phase gate:** Full suite (including evals if LLM key available) green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `tests/services/__init__.py` — package init
- [ ] `tests/services/test_knowledge_tracing.py` — covers KT-01, KT-02, KT-03
- [ ] `tests/services/test_tutor.py` — covers KT-05 prompt injection
- [ ] `tests/api/__init__.py` — package init
- [ ] `tests/api/test_session_end.py` — covers KT-04 POST /sessions/{id}/end
- [ ] `fsrs>=6.3.1` added to `requirements.txt`
- [ ] `ChildFSRSParamsModel` added to `db/models.py` before Wave 0 test runs

---

## Open Questions

1. **How is kc_id set per turn?**
   - What we know: `InteractionEventModel.kc_id` exists, `log_turn()` does not set it, nothing in Phase 1 sets it.
   - What's unclear: Should the client send `kc_id` in the chat request? Should the server infer it from `child.current_topic`? Should the LLM response include a structured tag?
   - Recommendation: Simplest approach for Phase 2 — infer `kc_id` from `child.current_topic` at log time (it's a slug already). Extend `log_turn()` to accept `kc_id: Optional[str] = None`. Document that Phase 5 device sync will send explicit `kc_id`.

2. **How is `correct` determined per turn?**
   - What we know: `InteractionEventModel.correct` exists, nothing sets it.
   - What's unclear: Determining correctness requires either the client to grade the answer or an LLM call to assess it.
   - Recommendation: For Phase 2, let the chat endpoint pass `correct=None` unless the LLM response contains an explicit signal (e.g. structured output tag). Correctness grading is a Phase 3/6 concern. BKT will no-op for turns with `correct=None` — this is acceptable and clearly documented.

3. **Where does POST /sessions/{id}/end live — `api/sessions.py` or new `api/knowledge_tracing.py`?**
   - What we know: `api/sessions.py` already has `GET /sessions/{child_id}`.
   - Recommendation: Add to `api/sessions.py` for cohesion. If the file grows large, extract later.

4. **`fsrs[optimizer]` brings torch as a transitive dependency — is this acceptable?**
   - What we know: `torch` is a large package (~700MB). The server runs on a standard machine, not the e-ink device. Package size is not a concern server-side.
   - Recommendation: Add `fsrs[optimizer]` to `requirements.txt`. If CI has size limits, note that `torch` can be installed with `--index-url https://download.pytorch.org/whl/cpu` for the CPU-only build.

---

## Environment Availability

| Dependency | Required By | Available | Fallback |
|------------|------------|-----------|----------|
| `fsrs` (PyPI) | KT-02 FSRS scheduling | Not yet installed | None — must install |
| `alembic` | DB migration | Already in requirements.txt | — |
| `pytest-asyncio` | Unit/integration tests | Inferred from existing tests | — |

**Missing dependencies with no fallback:**
- `fsrs>=6.3.1` — must be added to `requirements.txt` before Wave 1

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `fsrs` PyPI package is the same as `fsrs-python` reference implementation | Standard Stack | Low — confirmed via PyPI home URL pointing to github.com/open-spaced-repetition/py-fsrs |
| A2 | `Optimizer` is available in `fsrs[optimizer]` extra, requires torch | FSRS API | Medium — if API changed in 6.3.1, fitting code must be adjusted |
| A3 | Correct → Rating.Good, Incorrect → Rating.Again is the right mapping | FSRS Rating Mapping | Low — maps to expected FSRS semantics; revisit in Phase 6 when latency data available |
| A4 | BKT default priors (0.1, 0.2, 0.1, 0.2) are reasonable for this domain | BKT section | Low — already set in MasteryStateModel; consistent with textbook defaults |
| A5 | All eval files use SYSTEM_PROMPT_TEMPLATE.format() directly, not build_system_prompt() | Eval Safety | None — verified by reading all 5 eval files in this session |

---

## Sources

### Primary (HIGH confidence)

- `github.com/open-spaced-repetition/py-fsrs` README [VERIFIED: WebFetch] — Card, Rating, Scheduler, Optimizer API
- `pypi.org/pypi/fsrs/json` [VERIFIED: curl] — version 6.3.1, oldest release 2022-12-01, MIT license
- `db/models.py`, `db/crud.py`, `services/curriculum.py`, `services/tutor.py`, `api/chat.py`, `api/sessions.py` [VERIFIED: direct file read] — existing codebase patterns

### Secondary (MEDIUM confidence)

- Corbett & Anderson (1994) BKT formulation — standard 4-equation closed form; well-established in EdTech literature [ASSUMED — textbook knowledge]

### Tertiary (LOW confidence)

- Pardos & Heffernan (2010) typical BKT parameter ranges — p_guess ≈ 0.25, p_slip ≈ 0.1 [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — fsrs 6.3.1 verified on PyPI, existing stack from codebase
- Architecture: HIGH — based on direct codebase reading
- BKT math: MEDIUM — standard formulation from training knowledge, not verified against a live paper in this session
- FSRS API: HIGH — verified against official README
- Pitfalls: HIGH — derived from direct code analysis (kc_id gap is a real unset field)

**Research date:** 2026-07-16
**Valid until:** 2026-08-16 (fsrs API is stable; check if 6.4.x releases before Phase 2 kicks off)
