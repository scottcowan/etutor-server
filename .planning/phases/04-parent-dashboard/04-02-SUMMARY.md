---
phase: 04-parent-dashboard
plan: 02
subsystem: alert-data-layer
tags: [crud, tdd, alerts, safety, sessions, parent-dashboard]
dependency_graph:
  requires:
    - 04-01 (AlertModel ORM + safety_flag migration must exist)
  provides:
    - update_child_profile (db/crud.py)
    - create_alert (db/crud.py)
    - get_alerts_for_child (db/crud.py)
    - get_all_mastery_for_child (db/crud.py)
    - run_frustration_tally (db/crud.py)
    - _SAFETY_KEYWORDS + _has_safety_flag() (db/crud.py)
    - D-10 frustration alert tally at end_session
    - D-12/D-13 safety_flag + sensitive AlertModel row at log_turn
    - D-11 new-interest alert at extract_and_update_interests
  affects:
    - db/crud.py (new CRUD functions + safety logic)
    - api/sessions.py (run_frustration_tally wired)
    - services/session_intelligence.py (new-interest alert wired)
tech_stack:
  added: []
  patterns:
    - func.count() GROUP BY kc_id for frustration tally (sqlalchemy aggregation)
    - frozenset keyword detection (_has_safety_flag — read-only, no NLP)
    - Optional field-patch pattern for update_child_profile (setattr only non-None fields)
    - timedelta(days=30) window query with DESC ordering for alert feed
key_files:
  created:
    - tests/db/test_crud_parent.py (11 TDD tests, RED + GREEN)
  modified:
    - db/crud.py (new functions + safety detection in log_turn)
    - api/sessions.py (run_frustration_tally call at end_session)
    - services/session_intelligence.py (new-interest alert at extract_and_update_interests)
decisions:
  - "run_frustration_tally extracted as a standalone function in db/crud.py (not inlined in end_session) — keeps testability clean; end_session delegates via import"
  - "_SAFETY_KEYWORDS and _has_safety_flag defined in db/crud.py alongside log_turn — single source of truth for safety detection; test checks via log_turn return value"
  - "hint_used parameter added to log_turn signature (was previously absent) — allows tests to insert events with hint_used=True directly via log_turn"
  - "new-interest alert loop computes pre-update interests set before calling update_interests, then compares after — preserves idempotency of update_interests (set union) while detecting net-new tags"
metrics:
  duration: ~25 min
  completed: 2026-07-20
  tasks_completed: 2
  files_changed: 4
---

# Phase 04 Plan 02: Alert Data Layer Summary

**One-liner:** Four parent-dashboard CRUD functions (update_child_profile, create_alert, get_alerts_for_child, get_all_mastery_for_child) + safety keyword detection, frustration tally, and new-interest alert writes wired into session lifecycle.

---

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| RED | TDD test stubs — 11 tests failing ImportError | 812affc | tests/db/test_crud_parent.py |
| GREEN | CRUD implementation + session wiring | 98d8b92 | db/crud.py, api/sessions.py, services/session_intelligence.py |

---

## Verification Results

- `pytest tests/db/test_crud_parent.py -x -q` RED: **ImportError — CONFIRMED**
- `pytest tests/db/test_crud_parent.py -x -q` GREEN: **11 passed**
- `pytest tests/db/ -x -q`: **41 passed** (no regressions in DB test suite)
- `pytest tests/ -x -q --ignore=tests/evals --ignore=tests/api --ignore=tests/services/test_knowledge_tracing.py`: **62 passed** (pre-existing failures: `fastapi` not installed in worktree env; `fsrs.Scheduler` missing in worktree env — both failures existed before this plan)

---

## TDD Gate Compliance

- RED commit (`812affc`) — `test(04-02): add failing TDD tests` exists
- GREEN commit (`98d8b92`) — `feat(04-02): implement alert CRUD` exists after RED
- Gate sequence: PASSED

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing functionality] hint_used parameter missing from log_turn**
- **Found during:** GREEN phase — tests insert events with hint_used=True via log_turn
- **Issue:** `log_turn` had no `hint_used` keyword parameter; the frustration tally test needed to insert events with `hint_used=True` through the standard CRUD function
- **Fix:** Added `hint_used: Optional[bool] = None` keyword parameter to `log_turn` signature
- **Files modified:** `db/crud.py`
- **Commit:** 98d8b92

**2. [Rule 2 - Missing functionality] run_frustration_tally extracted as separate function**
- **Found during:** GREEN phase design
- **Issue:** The plan described inlining the frustration tally in `end_session()`. Extracting it as a standalone `run_frustration_tally(session_id, child_id, db)` function allows direct TDD testing (test_frustration_alert_created_at_end_session calls it directly without needing a full HTTP request)
- **Fix:** Extracted as standalone function; `end_session()` delegates to it
- **Files modified:** `db/crud.py`, `api/sessions.py`
- **Commit:** 98d8b92

### Verification Notes

The plan's spot-check greps expected `hint_count` in `api/sessions.py` and `create_alert.*sensitive` in `api/sessions.py`. Both live in `db/crud.py` instead (the correct architectural home). All 11 tests confirm the semantics are satisfied.

---

## Known Stubs

None — all CRUD functions are fully wired with real DB operations.

---

## Threat Surface

No new endpoints added. All write paths are internal (called from end_session + log_turn + extract_and_update_interests). The `_SAFETY_KEYWORDS` frozenset is a compile-time constant (T-4-02-02 accept disposition confirmed).

---

## Self-Check

Files exist:
- `tests/db/test_crud_parent.py` — FOUND
- `db/crud.py` (modified) — FOUND
- `api/sessions.py` (modified) — FOUND
- `services/session_intelligence.py` (modified) — FOUND

Commits exist:
- 812affc — FOUND
- 98d8b92 — FOUND

## Self-Check: PASSED
