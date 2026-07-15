# Phase 2: Knowledge Tracing Backend - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-07-15
**Phase:** 2-Knowledge Tracing Backend
**Areas discussed:** BKT Implementation Approach, FSRS Library vs. Custom, next_topics() Design, KT-05 Prompt Injection

---

## BKT Implementation Approach

| Option | Description | Selected |
|--------|-------------|----------|
| Closed-form in-house | ~20 lines of BKT math in services/knowledge_tracing.py, no dependency | ✓ |
| pyBKT library | Full BKT library with EM fitting — overkill for online updates | |
| simpleKT / FoLiBiKT | Deep-learning KT models (PyTorch) — not practical without GPU | |

**User's choice:** Closed-form in-house

---

| Option | Description | Selected |
|--------|-------------|----------|
| Per-turn inline in chat route | Update BKT immediately after each log_turn | |
| Post-session batch | Collect all turns, update BKT when session ends | ✓ |
| Background task on each turn | FastAPI BackgroundTasks — async, harder to test | |

**User's choice:** Post-session batch

---

| Option | Description | Selected |
|--------|-------------|----------|
| POST /sessions/{id}/end endpoint | Explicit session-close trigger; device sync calls it | ✓ |
| Idle timeout via scheduled task | Needs APScheduler/arq — new dependency, Phase 3+ | |
| Defer to Phase 3 | Scaffold math only, no trigger in Phase 2 | |

**User's choice:** POST /sessions/{id}/end endpoint

---

## FSRS Library vs. Custom

| Option | Description | Selected |
|--------|-------------|----------|
| fsrs-python library | Reference FSRS-5 implementation, ~200 lines, no heavy deps | ✓ |
| Minimal custom subset | Write only next_review formula ourselves | |

**User's choice:** fsrs-python library

---

| Option | Description | Selected |
|--------|-------------|----------|
| Default parameters for all | Use fsrs-python defaults, personalise later | |
| Default + early personalisation infrastructure | Build storage, attempt fit after every session end | ✓ |

**User's choice:** Attempt per-child parameter fitting after every session end, even with sparse data. Fit improves as interactions accumulate.

---

| Option | Description | Selected |
|--------|-------------|----------|
| New child_fsrs_params table | child_id PK + JSON weight vector, one row per child | ✓ |
| JSON column on ChildProfileModel | Fewer tables but conflates profile with ML state | |

**User's choice:** New child_fsrs_params table

---

## next_topics() Design

| Option | Description | Selected |
|--------|-------------|----------|
| New DB-aware next_topics in services/knowledge_tracing.py | Pure curriculum.py stays untouched | ✓ |
| Replace curriculum.py's next_topics | Makes pure function depend on DB state | |
| Wrapper in api/chat.py | Puts ranking logic in API layer | |

**User's choice:** New DB-aware next_topics in services/knowledge_tracing.py

---

| Option | Description | Selected |
|--------|-------------|----------|
| FSRS next_review first, mastery bucket as tiebreaker | Most overdue first; fragile > in_progress > not_started within tier | ✓ |
| Mastery bucket first, FSRS second | Can hammer same KC every session | |
| Interest-weighted with FSRS/BKT as filters | May starve important KCs | |

**User's choice:** FSRS next_review first, mastery bucket as tiebreaker

---

## KT-05 Prompt Injection

| Option | Description | Selected |
|--------|-------------|----------|
| New mastery_context param in build_system_prompt | Optional kwarg, None = unchanged (evals safe) | ✓ |
| Separate prompt builder in knowledge_tracing.py | Extra indirection | |
| Inject into user message | Wrong layer — system prompt is canonical | |

**User's choice:** New mastery_context section in build_system_prompt

---

| Option | Description | Selected |
|--------|-------------|----------|
| Top 5 KCs from next_topics() only | Tight, actionable; passes limit=5 to next_topics | ✓ |
| Full mastery map summary | Breadth without direction | |
| Per-topic bucket for all non-not_started KCs | Hundreds of lines, blows context window | |

**User's choice:** Top N due/fragile KCs only (limit=5)

---

## Claude's Discretion

- BKT default prior values (already set in MasteryStateModel)
- Exact FSRS-5 initialisation API (follow fsrs-python docs)
- Whether per-child FSRS fitting uses fsrs-python optimizer or custom gradient step

## Deferred Ideas

None — discussion stayed within phase scope.
