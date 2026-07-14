---
phase: 01-database-foundation
plan: "05"
subsystem: services
tags: [refactor, thin-wrapper, db-integration, services]
dependency_graph:
  requires: [01-03, 01-04]
  provides: [services-profiles-db-backed, services-sessions-db-backed]
  affects: [api/chat.py, api/child.py, api/sessions.py, api/parent.py]
tech_stack:
  added: []
  patterns: [thin-service-wrapper, explicit-async-session]
key_files:
  created: []
  modified:
    - services/profiles.py
    - services/sessions.py
    - api/stt.py
decisions:
  - "Service functions accept explicit AsyncSession parameter — API routes will inject via Depends(get_db) in Plans 06-07"
  - "ChildProfile dataclass removed; ORM model field names match exactly so tutor.py duck-typing continues to work"
  - "Neurodivergence documentation preserved in module docstring of profiles.py"
metrics:
  duration: "< 5 minutes"
  completed: "2026-07-15"
  tasks_completed: 2
  tasks_total: 2
  files_changed: 3
---

# Phase 01 Plan 05: Services thin-wrapper migration Summary

Services/profiles.py and services/sessions.py migrated from in-memory dicts to thin wrappers over db/crud.py; all functions now accept an explicit AsyncSession; dead import removed from api/stt.py.

## Tasks Completed

| Task | Name | Commit | Files |
|------|------|--------|-------|
| 1 | Migrate services/profiles.py to thin wrapper | 781dbee | services/profiles.py |
| 2 | Migrate services/sessions.py; remove stt.py dead import | 5835898 | services/sessions.py, api/stt.py |

## What Changed

**services/profiles.py** — Complete replacement:
- Removed: `_profiles` dict, `_device_map` dict, `ChildProfile` dataclass, `seed_dev_profiles()` function and module-level call
- Added: four thin wrapper functions delegating to `db/crud.py` (`get_child_by_id`, `get_child_by_device_id`, `list_children`, `update_interests`), all accepting explicit `AsyncSession`
- Importing this module now has zero DB I/O and no side effects

**services/sessions.py** — Complete replacement:
- Removed: `_sessions` dict, `Turn` dataclass
- Added: four thin wrapper functions delegating to `db/crud.py` (`log_turn`, `get_session_history`, `create_session`, `get_session`), all accepting explicit `AsyncSession`

**api/stt.py** — Single line removed:
- `from services.profiles import get_child_by_device_id` (dead import — unused in `transcribe()` function body)

## Verification

```
python3 -c "import services.profiles; import services.sessions; print('All service imports OK')"
# All service imports OK

pytest tests/db/ -x -q
# 23 passed in 0.18s
```

## Deviations from Plan

None — plan executed exactly as written.

## Known Stubs

None — this plan is a pure refactor with no UI-facing data flows.

## Threat Flags

None — no new network endpoints, auth paths, or trust boundaries introduced.

## Self-Check: PASSED

- services/profiles.py exists and contains `from db.crud import`
- services/sessions.py exists and contains `from db.crud import`
- api/stt.py dead import removed (grep returns 0)
- Commits 781dbee and 5835898 present in git log
- 23/23 db tests pass
