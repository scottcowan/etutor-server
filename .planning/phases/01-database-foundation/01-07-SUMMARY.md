---
phase: 01-database-foundation
plan: "07"
subsystem: api
tags: [refactor, db-integration, session-injection, api-routes]
dependency_graph:
  requires: [01-05]
  provides: [api-routes-db-backed]
  affects: [api/sessions.py, api/sync.py, api/child.py, api/parent.py, api/dashboard.py]
tech_stack:
  added: []
  patterns: [Depends(get_db)-injection, explicit-orm-serialisation]
key_files:
  created: []
  modified:
    - api/sessions.py
    - api/sync.py
    - api/child.py
    - api/parent.py
    - api/dashboard.py
    - services/recommender.py
decisions:
  - "get_all_sessions removed from api/parent.py and api/dashboard.py — session replay is Phase 4 scope; sessions={} passed to templates for Phase 1"
  - "vars() ORM serialisation replaced with explicit dict construction in api/sessions.py and api/dashboard.py to prevent _sa_instance_state leakage"
  - "services/recommender.py ChildProfile import replaced with ChildProfileModel — Rule 1 fix for broken import from Plan 05 migration"
metrics:
  duration: "< 10 minutes"
  completed: "2026-07-15"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 6
---

# Phase 01 Plan 07: Route session injection — remaining 5 API files Summary

Depends(get_db) session injection wired into api/sessions.py, api/sync.py, api/child.py, api/parent.py, api/dashboard.py; vars() ORM serialisation replaced with explicit dict construction; get_all_sessions removed from API layer.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Inject session into api/sessions.py and api/sync.py | 5f89ca3 | api/sessions.py, api/sync.py, services/recommender.py |
| 2 | Inject session into api/child.py, api/parent.py, api/dashboard.py | cc37b4f | api/child.py, api/parent.py, api/dashboard.py |

## What Changed

**api/sessions.py** — Session injection + explicit serialisation:
- Added `session: AsyncSession = Depends(get_db)` parameter to `get_sessions`
- `get_session_history(child_id, limit)` -> `get_session_history(child_id, session, limit)`
- `[vars(t) for t in turns]` -> explicit dict with id, child_id, question, answer, timestamp.isoformat(), topic, session_id

**api/sync.py** — Session injection:
- Added `session: AsyncSession = Depends(get_db)` parameter to `sync_device`
- `get_child_by_device_id(device_id)` -> `get_child_by_device_id(device_id, session)`

**api/child.py** — Session injection:
- Added `session: AsyncSession = Depends(get_db)` to both `child_home` and `child_chat`
- Consolidated inline `from services.profiles import get_child_by_id` to top-level import
- Both service calls pass session

**api/parent.py** — Session injection + get_all_sessions removal:
- Added `session: AsyncSession = Depends(get_db)` to `parent_dashboard`
- Removed `get_all_sessions` import and call; `sessions = {}` passed to template (Phase 4 scope)
- `list_children(session)` call wired

**api/dashboard.py** — Session injection + vars() removal + get_all_sessions removal:
- Added `session: AsyncSession = Depends(get_db)` to `dashboard`
- Removed `get_all_sessions` import; `"sessions": {}` in response
- `[vars(c) for c in children]` -> explicit dict with all ChildProfileModel fields enumerated

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed broken ChildProfile import in services/recommender.py**
- **Found during:** Task 1 (import verification)
- **Issue:** `services/recommender.py` imported `ChildProfile` from `services/profiles` which was removed in Plan 05 migration. This caused `ImportError` when any route importing `recommender` was loaded.
- **Fix:** Replaced `from services.profiles import ChildProfile` with `from db.models import ChildProfileModel` and updated both function type annotations.
- **Files modified:** services/recommender.py
- **Commit:** 5f89ca3

## Verification

```
python -c "
import api.sessions, api.sync, api.child, api.parent, api.dashboard
print('All 5 route files import OK')
"
# All 5 route files import OK

grep -rn "vars(" api/ --include="*.py"
# (no output — 0 matches)

grep -rn "get_all_sessions" api/ --include="*.py"
# (no output — 0 matches)

pytest tests/db/ -x -q
# 23 passed in 0.18s
```

## Known Stubs

- `api/parent.py` and `api/dashboard.py` pass `sessions = {}` — intentional Phase 1 stub; session replay is Phase 4 scope, noted in code comments.

## Threat Flags

None — no new network endpoints introduced; explicit serialisation in sessions.py and dashboard.py prevents _sa_instance_state leakage (T-1-20 mitigated).

## Self-Check: PASSED

- api/sessions.py, api/sync.py, api/child.py, api/parent.py, api/dashboard.py all exist with Depends(get_db)
- services/recommender.py uses ChildProfileModel
- No vars() in api/: grep returns 0 matches
- No get_all_sessions in api/: grep returns 0 matches
- Commits 5f89ca3 and cc37b4f present in git log
- 23/23 db tests pass
