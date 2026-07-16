---
phase: 02-knowledge-tracing-backend
plan: 05
subsystem: api
tags: [session-end, bkt, fsrs, tdd, rest-api]
requires:
  - 02-03
provides:
  - POST /v1/sessions/{session_id}/end endpoint
affects:
  - api/sessions.py
tech_stack:
  added: []
  patterns:
    - FastAPI POST route with 404/409 guards
    - dependency_overrides in-memory SQLite integration test pattern
key_files:
  created:
    - tests/api/test_session_end.py
  modified:
    - api/sessions.py
decisions:
  - Used `db` for the new route's session parameter to avoid shadowing existing `session` variable in GET route
  - Did not create tests/api/__init__.py — --import-mode=importlib breaks with package __init__ in test dirs
metrics:
  duration_minutes: 17
  completed: "2026-07-16T11:45:00Z"
  tasks_completed: 2
  files_created: 1
  files_modified: 1
---

# Phase 02 Plan 05: POST /sessions/{id}/end Endpoint Summary

**One-liner:** POST /v1/sessions/{id}/end closes a session, triggers BKT batch update and FSRS re-fit, returns session_id/ended_at/kcs_updated.

## What Was Built

Extended `api/sessions.py` with a new `POST /sessions/{session_id}/end` route that:
- Validates the session exists (404 if not)
- Guards against double-close (409 if `ended_at` already set)
- Sets `sessions.ended_at = now(UTC)` and commits
- Calls `update_bkt_for_session(session_id, db)` for batch BKT update
- Calls `fit_fsrs_params(child_id, db)` for per-child FSRS re-fitting
- Returns `{session_id, ended_at, kcs_updated}` where `kcs_updated = len(bkt_updates)`

Added `tests/api/test_session_end.py` with 4 integration tests using the `dependency_overrides` in-memory SQLite pattern from `test_chat_db_wiring.py`.

## TDD Gate Compliance

- RED commit: `4efffd9` — `test(02-05): add failing session end endpoint tests — RED`
- GREEN commit: `6b5cff2` — `feat(02-05): implement POST /sessions/{id}/end — GREEN`
- REFACTOR: not required (implementation was clean on first pass)

## Tasks Completed

| Task | Phase | Commit | Files |
|------|-------|--------|-------|
| RED: failing tests | 02-05 | 4efffd9 | tests/api/test_session_end.py |
| GREEN: implementation | 02-05 | 6b5cff2 | api/sessions.py |

## Verification

- `pytest tests/api/test_session_end.py -x -v` — 4/4 PASSED
- `pytest tests/ --ignore=tests/evals` — 45/45 PASSED (no regressions)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Removed tests/api/__init__.py that broke test collection**
- **Found during:** RED phase test run
- **Issue:** Creating `tests/api/__init__.py` caused `ModuleNotFoundError: No module named 'api.main'` under `--import-mode=importlib`. With importlib mode, `__init__.py` makes the directory a package and interferes with the pythonpath resolution. The existing `test_chat_db_wiring.py` works without it.
- **Fix:** Did not commit the `__init__.py` file. The plan called for creating it but it breaks the existing test infrastructure.
- **Files modified:** none (file was not committed)

## Known Stubs

None — the endpoint is fully wired to `update_bkt_for_session()` and `fit_fsrs_params()`.

## Threat Flags

No new security-relevant surface introduced beyond what was planned. The T-2-10/T-2-11/T-2-12 mitigations from the threat model are all implemented:
- T-2-10: `session_id` passed to `get_session()` which uses parameterised ORM select
- T-2-12: 409 guard prevents BKT/FSRS from running on already-ended sessions

## Self-Check: PASSED

- `/Users/scowan/Projects/scottcowan/etutor-server/.claude/worktrees/agent-a3e2be1a35b9455f2/api/sessions.py` — FOUND (modified)
- `/Users/scowan/Projects/scottcowan/etutor-server/.claude/worktrees/agent-a3e2be1a35b9455f2/tests/api/test_session_end.py` — FOUND (created)
- Commit `4efffd9` — RED gate commit exists
- Commit `6b5cff2` — GREEN gate commit exists
