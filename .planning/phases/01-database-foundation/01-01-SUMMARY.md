---
phase: 01-database-foundation
plan: "01"
subsystem: database
tags: [sqlalchemy, alembic, aiosqlite, pytest-asyncio, sqlite, orm]

# Dependency graph
requires: []
provides:
  - SQLAlchemy 2.0 async ORM models (ChildProfileModel, SessionModel, InteractionEventModel, MasteryStateModel)
  - Async session factory (engine, AsyncSessionLocal, get_db FastAPI dependency)
  - Idempotent dev seed function seed_dev_data() for KidA/KidB profiles
  - pytest-asyncio db_session fixture backed by in-memory SQLite
  - pytest.ini with asyncio_mode=auto and pythonpath=. for import resolution
affects:
  - 01-02-PLAN (CRUD tests use db_session fixture)
  - 01-03-PLAN (crud.py extends models defined here)
  - 01-05-PLAN (service migration threads sessions from get_db)
  - 01-06-PLAN (chat route adds Depends(get_db))

# Tech tracking
tech-stack:
  added:
    - sqlalchemy 2.0.51 (async ORM, DeclarativeBase, mapped_column)
    - alembic 1.18.5 (migrations tool — init deferred to plan 04)
    - aiosqlite 0.22.1 (SQLite async driver for sqlite+aiosqlite:// URLs)
    - pytest-asyncio 1.4.0 (asyncio_mode=auto for async test fixtures)
  patterns:
    - SQLAlchemy 2.0 DeclarativeBase with Mapped[] typed annotations
    - async_sessionmaker with expire_on_commit=False for FastAPI async pattern
    - INSERT OR IGNORE via sqlite_insert().prefix_with("OR IGNORE") for idempotent seeds
    - pytest_asyncio.fixture with in-memory SQLite + Base.metadata.create_all per test

key-files:
  created:
    - db/__init__.py
    - db/models.py
    - db/session.py
    - db/seeds.py
    - tests/conftest.py
    - tests/db/__init__.py
    - pytest.ini
  modified: []

key-decisions:
  - "Used Base.metadata.create_all (not Alembic programmatic invocation) for test fixture per D-12 — identical schema for Phase 1 single initial migration"
  - "Added importmode=importlib to pytest.ini — required for conftest.py to import db.* from worktree root before pythonpath is applied"
  - "Column names in ChildProfileModel match ChildProfile dataclass exactly (id, name, age, device_id, interests, reading_level, current_topic, current_books, session_count, neurodivergence) for duck-type compatibility with services/tutor.py attribute access"
  - "MasteryStateModel uses composite PK (child_id, kc_id) with Float BKT + FSRS scaffold columns all nullable — Phase 2 populates"
  - "InteractionEventModel includes nullable scaffold columns kc_id, correct, response_ms, hint_used for DB-04 Phase 2 BKT readiness"

patterns-established:
  - "SQLAlchemy 2.0: use Mapped[T] + mapped_column() not Column(); use async_sessionmaker not sessionmaker"
  - "get_db as async generator yielding AsyncSession for FastAPI Depends injection"
  - "Seed profiles as KidA/KidB (D-08) — never real names in code"
  - "Test fixtures use in-memory SQLite via sqlite+aiosqlite:///:memory: for full isolation"

requirements-completed: [DB-01]

# Metrics
duration: 5min
completed: 2026-07-14
---

# Phase 01 Plan 01: DB Package Bootstrap Summary

**SQLAlchemy 2.0 async ORM layer with 4 models (child_profiles, sessions, interaction_events, mastery_state), async session factory, idempotent KidA/KidB seeds, and pytest-asyncio in-memory fixture infrastructure**

## Performance

- **Duration:** ~5 min
- **Started:** 2026-07-14T23:00:15Z
- **Completed:** 2026-07-14T23:05:01Z
- **Tasks:** 3
- **Files modified:** 7 created, 0 modified

## Accomplishments

- Four SQLAlchemy 2.0 ORM models defined with correct column names matching downstream duck-typed callers in services/tutor.py
- Async session factory (engine, AsyncSessionLocal, get_db) wired to config/settings.py database_url — no DB I/O at import time
- Idempotent seed function using SQLite INSERT OR IGNORE for KidA/KidB generic profiles (D-08 compliant)
- pytest-asyncio infrastructure with asyncio_mode=auto and isolated in-memory db_session fixture per test
- pytest.ini updated with importmode=importlib and pythonpath=. to fix module resolution in git worktree context

## Task Commits

Each task was committed atomically:

1. **Task 1: Install dependencies and create pytest.ini + data/.gitkeep** - `8b1425c` (chore)
2. **Task 2: Create db/ package — models and session factory** - `2705061` (feat)
3. **Task 3: Create db/seeds.py and tests/conftest.py + tests/db/__init__.py** - `2d05d33` (feat)

## Files Created/Modified

- `pytest.ini` - asyncio_mode=auto, pythonpath=., importmode=importlib for pytest-asyncio and import resolution
- `db/__init__.py` - Package marker
- `db/models.py` - ChildProfileModel, SessionModel, InteractionEventModel, MasteryStateModel (SQLAlchemy 2.0 DeclarativeBase)
- `db/session.py` - AsyncEngine, AsyncSessionLocal, get_db dependency generator
- `db/seeds.py` - Idempotent async seed_dev_data(session) with KidA/KidB INSERT OR IGNORE
- `tests/conftest.py` - db_session pytest-asyncio fixture (in-memory SQLite, Base.metadata.create_all)
- `tests/db/__init__.py` - Package marker for DB unit tests
- `data/.gitkeep` - Already tracked in main repo; confirmed present in worktree

## Decisions Made

- Used `Base.metadata.create_all` instead of programmatic Alembic invocation for the test fixture (D-12). Produces identical schema for Phase 1 single initial migration; simpler and faster.
- Added `importmode = importlib` to pytest.ini (deviation — see below). Required for conftest.py module imports to work when running pytest from the worktree directory.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Added importmode=importlib and pythonpath=. to pytest.ini**
- **Found during:** Task 3 verification (`pytest tests/db/ --collect-only`)
- **Issue:** conftest.py failed with `ModuleNotFoundError: No module named 'db.models'` — pytest's default import mode loads conftest before applying `pythonpath` from pytest.ini, so `db.*` packages couldn't be found when running from the worktree directory
- **Fix:** Added `addopts = --import-mode=importlib` and `pythonpath = .` to pytest.ini. With importlib mode, pytest discovers rootdir from pytest.ini location (worktree root) and module imports resolve correctly. Verified evals still collect (10 tests) with no errors.
- **Files modified:** pytest.ini
- **Verification:** `pytest tests/db/ --collect-only -q` reports "no tests collected" (correct — no test files yet) with exit 5 (no tests found) not exit 4 (error). Evals collect 10+ tests unchanged.
- **Committed in:** 2d05d33 (Task 3 commit)

---

**Total deviations:** 1 auto-fixed (Rule 3 - blocking)
**Impact on plan:** Essential fix for test infrastructure functionality. No scope creep. pytest.ini plan spec only required `asyncio_mode = auto`; additional keys are additive and non-breaking.

## Issues Encountered

- `data/.gitkeep` is already tracked in the main repo (committed prior to this phase). The worktree correctly inherits it. The plan's Task 1 instruction to "create data/.gitkeep" was satisfied by the existing tracked file — no action needed beyond confirmation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 02 can immediately write tests against `db/crud.py` using the `db_session` fixture
- Plan 03 can extend crud.py; all 4 ORM models are defined and importable
- Plans 05-07 have the session factory and models in place to thread sessions through service call chains
- No blockers — all acceptance criteria met

---
*Phase: 01-database-foundation*
*Completed: 2026-07-14*
