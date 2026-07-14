---
phase: 01-database-foundation
plan: "04"
subsystem: database
tags: [alembic, migrations, async, sqlite, aiosqlite, sqlalchemy]

# Dependency graph
requires:
  - 01-01  # db/models.py Base.metadata source
provides:
  - alembic.ini configured for sqlite+aiosqlite:///./data/etutor.db
  - migrations/env.py with async pattern (run_async_migrations, async_engine_from_config)
  - migrations/versions/9f229414e92b_initial_schema.py — creates all 4 tables
affects:
  - 01-02-PLAN (tests can now use programmatic Alembic for fixture confidence)
  - 01-05-PLAN (lifespan handler can call alembic upgrade head at startup)

# Tech tracking
tech-stack:
  added:
    - alembic 1.18.5 (migrations directory init, async env.py pattern)
    - greenlet 3.5.3 (implicit SQLAlchemy async dep — was missing from venv, auto-fixed)
  patterns:
    - Alembic async env.py using async_engine_from_config and asyncio.run(run_async_migrations())
    - offline mode: synchronous context.configure(url=...) path preserved for SQL script generation
    - autogenerate with target_metadata = Base.metadata from db.models

key-files:
  created:
    - alembic.ini
    - migrations/env.py
    - migrations/script.py.mako
    - migrations/README
    - migrations/versions/9f229414e92b_initial_schema.py
  modified: []

key-decisions:
  - "alembic.ini sqlalchemy.url = sqlite+aiosqlite:///./data/etutor.db — matches settings.database_url default exactly"
  - "migrations/env.py imports Base from db.models directly (not db package) — db/__init__.py is a package marker only"
  - "greenlet installed as auto-fix (Rule 3 — blocking): SQLAlchemy async requires greenlet but it was absent from the venv"
  - "migrations/script.py.mako left unchanged — async mode does not require template modification"
  - "data/etutor.db left in upgraded (head) state for development use after upgrade/downgrade/upgrade cycle"

# Metrics
duration: 10min
completed: 2026-07-15
---

# Phase 01 Plan 04: Alembic Init and Initial Migration Summary

**Alembic async migrations initialised — env.py uses async_engine_from_config pattern; initial migration creates all 4 tables on SQLite with upgrade/downgrade verified**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-07-14T23:00:00Z
- **Completed:** 2026-07-14T23:10:16Z
- **Tasks:** 2
- **Files created:** 5

## Accomplishments

- `alembic init migrations` run from worktree root — creates alembic.ini, migrations/env.py, migrations/script.py.mako, migrations/versions/
- alembic.ini `sqlalchemy.url` set to `sqlite+aiosqlite:///./data/etutor.db` (matches `config/settings.py` `Settings.database_url` default)
- migrations/env.py replaced entirely with async pattern: `async_engine_from_config`, `asyncio.run(run_async_migrations())`, `target_metadata = Base.metadata` from `db.models`
- `alembic revision --autogenerate -m "initial schema"` generated `9f229414e92b_initial_schema.py` with all 4 tables and FK constraints
- `alembic upgrade head` exits 0 — creates `data/etutor.db` with all 4 tables (SQLite)
- `alembic current` reports `9f229414e92b (head)`
- `alembic downgrade base` exits 0 — drops all tables cleanly
- `alembic upgrade head` (second run) exits 0 — migration path is idempotent

## Task Commits

Each task was committed atomically:

1. **Task 1: alembic init and async env.py replacement** — `4c6ce0d` (chore)
2. **Task 2: Generate initial migration and verify upgrade/downgrade** — `cb47e03` (feat)

## Files Created/Modified

- `alembic.ini` — Alembic configuration; `sqlalchemy.url = sqlite+aiosqlite:///./data/etutor.db`
- `migrations/env.py` — Async env using `async_engine_from_config`; imports `Base` from `db.models`
- `migrations/script.py.mako` — Unchanged default template for migration file generation
- `migrations/README` — Alembic README (auto-generated, unchanged)
- `migrations/versions/9f229414e92b_initial_schema.py` — Initial migration: `create_table` for child_profiles, sessions, interaction_events, mastery_state + FK constraints + indexes

## Decisions Made

- Used `from db.models import Base` not `from db import Base` — `db/__init__.py` is a package marker only (confirmed by Plan 01 SUMMARY)
- `data/etutor.db` left in `head` state after final `alembic upgrade head` — ready for development
- `migrations/script.py.mako` unchanged — async mode requires no template modification; template is for Python script generation, not migration execution

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Installed missing greenlet package**
- **Found during:** Task 2 — `alembic revision --autogenerate` failed with `ValueError: the greenlet library is required to use this function. No module named 'greenlet'`
- **Issue:** SQLAlchemy async requires `greenlet` at runtime but it was not installed in the venv (not listed explicitly in requirements.txt despite being an implicit SQLAlchemy async dependency)
- **Fix:** `pip install greenlet` — installed version 3.5.3
- **Files modified:** None (venv only)
- **Note:** Should add `greenlet` to requirements.txt or ensure `sqlalchemy[asyncio]` is specified as the extra that pulls it in

---

**Total deviations:** 1 auto-fixed (Rule 3 — blocking)
**Impact on plan:** greenlet install unblocked autogenerate; no scope creep; plan executed exactly as written otherwise.

## Issues Encountered

- `greenlet` was absent from the venv. SQLAlchemy's async layer requires it at runtime. The package is an implicit transitive dependency of `sqlalchemy[asyncio]` — if the venv was built with bare `sqlalchemy` (not the `asyncio` extra), greenlet is omitted. Future consideration: pin `sqlalchemy[asyncio]` in requirements.txt.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- Plan 02 (CRUD tests) can use `Base.metadata.create_all` for its test fixture (same schema as Alembic, simpler for in-memory SQLite)
- Plan 05 (service migration) — `alembic upgrade head` is ready to be called from `api/main.py` lifespan
- Phase 1 success criterion 2 (SQLite portion): SATISFIED — `alembic upgrade head` runs cleanly on fresh SQLite
- PostgreSQL verification deferred to Phase 6 (production hardening) as specified

## Known Stubs

None — this plan creates infrastructure only (alembic.ini, env.py, migration file). No UI, no data flow stubs.

## Threat Flags

None found beyond what was documented in the plan's threat_model (T-1-09, T-1-10, T-1-SC reviewed).

## Self-Check: PASSED

- `alembic.ini` exists at worktree root: FOUND
- `migrations/env.py` contains `run_async_migrations`: FOUND (2 occurrences — definition and call)
- `migrations/versions/9f229414e92b_initial_schema.py` exists: FOUND
- Task 1 commit `4c6ce0d`: FOUND
- Task 2 commit `cb47e03`: FOUND
- `alembic current` reports `(head)` after final upgrade: CONFIRMED

---
*Phase: 01-database-foundation*
*Completed: 2026-07-15*
