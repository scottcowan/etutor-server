---
phase: 02-knowledge-tracing-backend
plan: "03"
subsystem: knowledge-tracing
tags: [fsrs, spaced-repetition, tdd, scheduling, per-child-params]
dependency_graph:
  requires: [02-02]
  provides: [02-04, 02-05, 02-06]
  affects: [services/knowledge_tracing.py]
tech_stack:
  added: [fsrs==6.3.1 (installed in venv), fsrs[optimizer] (torch+pandas+numpy)]
  patterns:
    - FSRS-5 scheduler via fsrs.Scheduler + fsrs.Card + fsrs.Rating
    - Per-child parameter fitting via fsrs.Optimizer.compute_optimal_parameters()
    - Timezone normalisation: nr.replace(tzinfo=timezone.utc) when nr.tzinfo is None
    - Two-level rating mapping: correct=True → Rating.Good, correct=False → Rating.Again
key_files:
  modified:
    - services/knowledge_tracing.py
    - tests/services/test_knowledge_tracing.py
decisions:
  - "FSRS Card attribute is card.difficulty (not card.difficulty_d) — stored in difficulty_d column"
  - "Optimizer uses card_id=1 for all events (single virtual card per child for optimization)"
  - "fsrs package installed in .venv at execution time (was listed in requirements.txt but missing from venv)"
metrics:
  duration: ~20 minutes
  completed: "2026-07-16"
  tasks: 2
  files: 2
---

# Phase 02 Plan 03: FSRS-5 Scheduling (KT-02) Summary

FSRS-5 spaced-repetition scheduling layer — `update_fsrs_schedule()` writes stability/difficulty_d/card_state/next_review per rated review, and `fit_fsrs_params()` fits per-child FSRS-5 weights from interaction history with a cold-start guard (< 10 events → no write).

## Tasks Completed

| Task | Type | Description | Commit |
|------|------|-------------|--------|
| RED | test | Add failing FSRS scheduling tests | cd7098f |
| GREEN | feat | Implement update_fsrs_schedule + fit_fsrs_params | a5b4f16 |

## What Was Built

### `services/knowledge_tracing.py` additions

- `FSRS_MIN_REVIEWS_FOR_FIT = 10` — cold-start guard constant
- `update_fsrs_schedule(child_id, kc_id, correct, db, review_datetime=None)` — loads per-child FSRS weights (or defaults), reconstructs FSRS Card from mastery_state fields, applies review, writes stability/difficulty_d/card_state/next_review
- `fit_fsrs_params(child_id, db)` — selects all rated events, returns early if < 10, builds ReviewLog list, runs Optimizer to compute 21 optimal parameters, upserts to child_fsrs_params

### `tests/services/test_knowledge_tracing.py` additions

6 new test functions covering all behavioral requirements:
- `test_update_fsrs_schedule_correct` — verifies all 4 FSRS fields written after Good review
- `test_update_fsrs_schedule_incorrect_shorter_interval` — verifies Again < Good interval
- `test_fsrs_min_reviews_constant` — verifies FSRS_MIN_REVIEWS_FOR_FIT == 10
- `test_fit_fsrs_cold_start_guard_zero_events` — 0 events → no write
- `test_fit_fsrs_cold_start_guard_nine_events` — 9 events → no write
- `test_fit_fsrs_writes_params_with_fifteen_events` — 15 events → 21-float list written

## Verification Results

```
tests/services/test_knowledge_tracing.py — 15 passed (9 BKT + 6 FSRS)
Full suite (tests/ --ignore=tests/evals) — 41 passed, 1 warning
python -c "from services.knowledge_tracing import ...; print(FSRS_MIN_REVIEWS_FOR_FIT)" → 10
```

## TDD Gate Compliance

- RED commit: `cd7098f` — test(02-03): add failing FSRS scheduling tests — RED
- GREEN commit: `a5b4f16` — feat(02-03): implement FSRS update_fsrs_schedule + fit_fsrs_params — GREEN

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] fsrs package not installed in virtual environment**
- **Found during:** RED phase setup
- **Issue:** `fsrs` and `fsrs[optimizer]` were listed in requirements.txt but not installed in .venv
- **Fix:** Ran `pip install fsrs` and `pip install "fsrs[optimizer]"` to install fsrs 6.3.1 with torch/pandas/numpy optimizer support
- **Files modified:** .venv (not tracked)
- **Commit:** N/A (pre-commit fix)

## Known Stubs

None — all functions are fully implemented.

## Threat Surface Scan

No new threat surface beyond what was declared in the plan's `<threat_model>`. All FSRS inputs are internally computed (scheduler output and optimizer results) — no user-supplied data flows into FSRS weight writes. `child_id` and `kc_id` parameters are used only via SQLAlchemy ORM parameterised calls (T-2-05 mitigated).

## Self-Check: PASSED

- services/knowledge_tracing.py: FOUND
- tests/services/test_knowledge_tracing.py: FOUND
- Commit cd7098f: FOUND (RED)
- Commit a5b4f16: FOUND (GREEN)
