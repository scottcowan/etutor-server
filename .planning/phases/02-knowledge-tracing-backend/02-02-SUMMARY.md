---
phase: 02-knowledge-tracing-backend
plan: "02"
subsystem: knowledge-tracing
tags: [bkt, bayesian-knowledge-tracing, pytest, tdd, sqlalchemy, async]

requires:
  - phase: 02-01
    provides: "MasteryStateModel, create_or_get_mastery_state, update_mastery_state CRUD, log_turn with kc_id/correct fields"

provides:
  - "update_bkt() pure function: 4-equation closed-form BKT (Corbett & Anderson 1994)"
  - "update_bkt_for_session() async service: batch BKT update from interaction_events"
  - "TDD test suite: 9 tests covering pure function + integration scenarios"

affects:
  - "02-03 (FSRS scheduling — builds on same knowledge_tracing.py module)"
  - "02-05 (POST /sessions/{id}/end — calls update_bkt_for_session)"

tech-stack:
  added: []
  patterns:
    - "BKT 4-equation closed form in update_bkt() pure function"
    - "Async batch service pattern: SELECT → group → iterate → write via existing CRUD"
    - "tests/services/ dir uses conftest.py sys.path fix (no __init__.py) to avoid package name collision with top-level services/ under pytest importlib mode"

key-files:
  created:
    - "services/knowledge_tracing.py"
    - "tests/services/test_knowledge_tracing.py"
    - "tests/services/conftest.py"
  modified: []

key-decisions:
  - "Removed tests/services/__init__.py: pytest importlib mode registers tests/services as the 'services' package, shadowing top-level services/. Fixed by using conftest.py sys.path injection (matches tests/api/ pattern) instead."
  - "BKT near-zero incorrect threshold set to < 0.3 (not < 0.2): with p_learn=0.2, even p_mastery→0 after incorrect observation yields ~0.201 due to forward transition step. The correct BKT behaviour is that p_learn acts as a floor."
  - "Parameterised SELECT via SQLAlchemy ORM satisfies T-2-03 (no string interpolation of session_id)."

patterns-established:
  - "services/knowledge_tracing.py: module docstring listing KT-01 through KT-05 requirements for future implementors"
  - "BKT pure function signature: (p_mastery, p_learn, p_slip, p_guess, correct) -> float"
  - "Batch service returns dict[str, float] keyed by kc_id; returns {} on empty (no exception)"

requirements-completed: [KT-01]

duration: 15min
completed: 2026-07-16
---

# Phase 02 Plan 02: BKT Mastery Model Summary

**Closed-form 4-equation BKT (Corbett & Anderson 1994) implemented as a pure function + async batch service, with 9 TDD tests passing GREEN and 35/35 full suite passing**

## Performance

- **Duration:** ~15 min
- **Started:** 2026-07-16T10:18:00Z
- **Completed:** 2026-07-16T10:33:31Z
- **Tasks:** 2 (RED + GREEN TDD phases)
- **Files modified:** 3 created, 0 modified

## Accomplishments

- `update_bkt()` pure function: standard 4-equation BKT with zero-denominator guard and [0,1] clamp
- `update_bkt_for_session()` async service: parameterised SELECT of kc_id-tagged events, chronological BKT update per KC, writes back via existing CRUD
- 9 tests covering unit math, clamp invariant, session integration, DB persistence, and empty-session no-op
- Discovered and fixed pytest importlib mode package-name collision for tests/services/ subdirectory

## Task Commits

1. **RED: failing BKT tests** - `2d28c6a` (test)
2. **GREEN: BKT implementation** - `5e7fdc6` (feat)

## Files Created/Modified

- `services/knowledge_tracing.py` — update_bkt() pure function + update_bkt_for_session() async service
- `tests/services/test_knowledge_tracing.py` — 9 TDD tests (5 unit, 4 integration)
- `tests/services/conftest.py` — sys.path fix for pytest importlib mode

## Decisions Made

- Removed `tests/services/__init__.py` after discovering that pytest importlib mode was registering `tests/services` as the top-level `services` package, causing `ModuleNotFoundError` when tests tried to import `services.knowledge_tracing`. Used the same `conftest.py` sys.path injection pattern already established in `tests/api/conftest.py`.
- BKT near-zero incorrect test threshold corrected to `< 0.3`: the BKT forward transition step always adds `(1 - posterior) * p_learn`, so even with posterior ≈ 0 the minimum output is ≈ `p_learn = 0.2`. The original `< 0.2` assertion was mathematically wrong for these parameters.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed incorrect BKT test assertion for near-zero mastery + incorrect observation**
- **Found during:** GREEN phase (running tests after implementation)
- **Issue:** `test_bkt_near_zero_incorrect_stays_low` asserted `result < 0.2` but the BKT forward transition step adds `p_learn ≈ 0.2` to the posterior, so the minimum output is ~0.201 — mathematically correct behaviour, wrong test assertion
- **Fix:** Changed threshold to `< 0.3` with explanatory comment; updated docstring to explain p_learn floor
- **Files modified:** `tests/services/test_knowledge_tracing.py`
- **Verification:** All 9 tests pass
- **Committed in:** `5e7fdc6` (GREEN commit)

**2. [Rule 3 - Blocking] Removed tests/services/__init__.py to fix pytest importlib package collision**
- **Found during:** GREEN phase (running tests)
- **Issue:** `tests/services/__init__.py` caused pytest importlib mode to register `tests/services` as the `services` package in `sys.modules`, shadowing top-level `services/`. Result: `ModuleNotFoundError: No module named 'services.knowledge_tracing'`
- **Fix:** Removed `__init__.py`; added `tests/services/conftest.py` with same sys.path insertion pattern as `tests/api/conftest.py`
- **Files modified:** `tests/services/__init__.py` (deleted), `tests/services/conftest.py` (created)
- **Verification:** All 9 new tests pass; 35/35 full suite passes
- **Committed in:** `5e7fdc6` (GREEN commit)

---

**Total deviations:** 2 auto-fixed (1 bug in test assertion, 1 blocking import error)
**Impact on plan:** Both fixes required for correct test execution. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `services/knowledge_tracing.py` module is ready for Plan 02-03 to add `update_fsrs_schedule()` and other functions
- BKT batch update is callable from the session-end endpoint (Plan 02-05)
- `kc_id` and `correct` fields are already populated by `log_turn()` (from Plan 02-01); BKT will process real data when correctness grading is wired in Phase 3/6

---

## Self-Check: PASSED

- `services/knowledge_tracing.py` exists: FOUND
- `tests/services/test_knowledge_tracing.py` exists: FOUND
- `tests/services/conftest.py` exists: FOUND
- RED commit `2d28c6a`: FOUND
- GREEN commit `5e7fdc6`: FOUND
- All 35 tests pass: VERIFIED

---
*Phase: 02-knowledge-tracing-backend*
*Completed: 2026-07-16*
