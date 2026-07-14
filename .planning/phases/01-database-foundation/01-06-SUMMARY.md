---
phase: 01-database-foundation
plan: 06
subsystem: api
tags: [fastapi, lifespan, dependency-injection, sqlalchemy, wiring]
dependency_graph:
  requires: [01-05]
  provides: [api/main.py lifespan, api/chat.py session injection]
  affects: [api/dashboard.py, api/sessions.py, api/parent.py, api/child.py, services/recommender.py]
tech_stack:
  added: []
  patterns: [asynccontextmanager lifespan, Depends(get_db), FastAPI dependency_overrides in tests]
key_files:
  created:
    - tests/api/test_chat_db_wiring.py
    - tests/api/conftest.py
  modified:
    - api/main.py
    - api/chat.py
    - api/dashboard.py
    - api/sessions.py
    - api/parent.py
    - api/child.py
    - services/recommender.py
decisions:
  - "create_session called before log_turn in non-streaming path; ended_at left NULL (Phase 3 scope)"
  - "Removed tests/api/__init__.py to prevent 'api' namespace collision under pytest --import-mode=importlib"
metrics:
  duration: ~25min
  completed: "2026-07-14T23:28:57Z"
  tasks_completed: 2
  files_changed: 8
---

# Phase 01 Plan 06: DB Wiring — api/main.py Lifespan + api/chat.py Session Injection Summary

Server is now DB-backed: lifespan handler creates tables and seeds dev profiles on startup; chat route injects AsyncSession via FastAPI Depends and writes a sessions row + interaction_events row on every non-streaming turn.

## Tasks Completed

| # | Name | Commit | Files |
|---|------|--------|-------|
| 1 | Add lifespan handler to api/main.py | d902377 | api/main.py + 5 bug-fixed files |
| 2 | Add Depends(get_db) to api/chat.py + tests | 1bb1c2a | api/chat.py, tests/api/ |

## Verification Results

- `python -c "import api.main; import api.chat; print('OK')"` — PASS
- `pytest tests/db/ -x -q` — 23/23 passed
- `pytest tests/api/test_chat_db_wiring.py -x -q` — 3/3 passed
- `grep -c "lifespan" api/main.py` — 2 (definition + FastAPI kwarg)
- `grep -c "Depends(get_db)" api/chat.py` — 1
- `grep -c "create_session" api/chat.py` — 2 (import + call)
- `grep "log_turn" api/chat.py` — session is 4th positional arg, session_id= kwarg

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] services/recommender.py imported ChildProfile from services.profiles**
- **Found during:** Task 1 import verification
- **Issue:** Plan 05 removed `ChildProfile` dataclass from `services/profiles.py` (now uses ORM model), but `services/recommender.py` still imported it
- **Fix:** Changed import to `from db.models import ChildProfileModel as ChildProfile`
- **Files modified:** services/recommender.py
- **Commit:** d902377

**2. [Rule 1 - Bug] api/dashboard.py imported get_all_sessions which was removed in Plan 05**
- **Found during:** Task 1 import verification
- **Issue:** `get_all_sessions` no longer exists in services/sessions.py after Plan 05 migration; dashboard was also calling service functions without session parameter
- **Fix:** Updated api/dashboard.py to use `list_children(session)` with `Depends(get_db)`; removed sessions dict from response (empty placeholder)
- **Files modified:** api/dashboard.py
- **Commit:** d902377

**3. [Rule 1 - Bug] api/sessions.py calling get_session_history without session parameter**
- **Found during:** Task 1 import verification
- **Issue:** Plan 05 migrated `get_session_history` to require an AsyncSession; api/sessions.py still called with old signature
- **Fix:** Added `Depends(get_db)` to route handler; pass session to get_session_history
- **Files modified:** api/sessions.py
- **Commit:** d902377

**4. [Rule 1 - Bug] api/parent.py imported get_all_sessions and called list_children without session**
- **Found during:** Task 1 import verification
- **Issue:** Same Plan 05 migration breakage; parent dashboard used old session-less service calls
- **Fix:** Wired `Depends(get_db)` into parent_dashboard; removed get_all_sessions usage
- **Files modified:** api/parent.py
- **Commit:** d902377

**5. [Rule 1 - Bug] api/child.py called service functions without session parameter**
- **Found during:** Task 1 import verification
- **Issue:** Both list_children and get_child_by_id calls lacked session arg
- **Fix:** Added `Depends(get_db)` to child_home and child_chat handlers
- **Files modified:** api/child.py
- **Commit:** d902377

**6. [Rule 3 - Blocking] tests/api/__init__.py caused 'api' namespace collision**
- **Found during:** Task 2 test execution
- **Issue:** With `--import-mode=importlib`, having `tests/api/__init__.py` made Python resolve `from api.main import app` as `tests/api/main.py` instead of the top-level `api/main.py`
- **Fix:** Did not create `__init__.py` in tests/api/ (removed it after creation)
- **Files modified:** tests/api/ (no __init__.py)
- **Commit:** 1bb1c2a

## Known Stubs

None — all routes that were stubs before (dashboard sessions dict, sync endpoint) return the same placeholder data they had pre-plan; no new stubs introduced.

## Threat Flags

None — no new network endpoints or auth paths added beyond what the plan specifies.

## Self-Check: PASSED

- [x] api/main.py exists and contains lifespan
- [x] api/chat.py exists and contains Depends(get_db)
- [x] tests/api/test_chat_db_wiring.py exists
- [x] Commits d902377 and 1bb1c2a exist in git log
- [x] 23 db tests pass, 3 api wiring tests pass
