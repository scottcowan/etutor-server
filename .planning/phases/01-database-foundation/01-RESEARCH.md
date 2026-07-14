# Phase 1: Database Foundation - Research

**Researched:** 2026-07-14
**Domain:** SQLAlchemy 2.x async ORM, Alembic migrations, FastAPI dependency injection, pytest async fixtures
**Confidence:** HIGH

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

- **D-01:** Introduce a new `db/` layer that owns ORM models and CRUD. Services thin-wrap `db/` rather than being rewritten in-place.
- **D-02:** `db/session.py` exports `AsyncEngine`, `AsyncSessionLocal`, and a `get_db()` FastAPI dependency. `api/main.py` initialises the engine in its lifespan handler.
- **D-03:** Services receive the DB session via FastAPI `Depends(get_db)`. API route handlers get the session and pass it down to service functions. Evals use a `db_session` pytest fixture to inject sessions directly — no HTTP layer.
- **D-04:** `interests` and `neurodivergence` stored as JSON columns (single TEXT/JSON column per list). No association tables in Phase 1.
- **D-05:** Each `Turn` is its own row in `interaction_events`. Not a JSON blob on a session row.
- **D-06:** Dev seed profiles are idempotent upserts (`INSERT OR IGNORE` / `ON CONFLICT DO NOTHING`) run on server startup inside `lifespan`, only when `settings.env != 'production'`.
- **D-07:** Seed data lives in `db/seeds.py` as `async seed_dev_data(session)`.
- **D-08:** Seed profiles use generic identifiers (KidA / KidB). No real names in code or artifacts.
- **D-09:** Each eval run gets a fresh in-memory SQLite (`sqlite:///:memory:`). `tests/conftest.py` creates engine, applies Alembic migrations, inserts fixture child profile, provides `db_session` fixture.
- **D-10:** Evals call service functions directly with `db_session` as an explicit argument. No `app.dependency_overrides`.

### Claude's Discretion

- Exact column names, table names, SQLAlchemy model class names — standard FastAPI/SQLAlchemy conventions apply.
- Whether `db/models.py` and `db/crud.py` are single files or split — planner decides based on number of models.
- Alembic `env.py` configuration details (target_metadata, run_migrations_online/offline) — standard boilerplate.

### Deferred Ideas (OUT OF SCOPE)

None — discussion stayed within phase scope.
</user_constraints>

---

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DB-01 | SQLite database with SQLAlchemy ORM and Alembic migrations replaces in-memory stores | SQLAlchemy 2.0 async + Alembic initialized from scratch; `db/` package pattern confirmed standard |
| DB-02 | ChildProfile persisted (name, age, reading_level, interests, neurodivergence, device_id) | ORM model mirrors existing dataclass; JSON column for list fields confirmed SQLite-compatible |
| DB-03 | Session records persisted (session_id, child_id, started_at, ended_at, turn count) | `sessions` table design documented; turn count is a derived field — store individual events (D-05) |
| DB-04 | Interaction events persisted (kc_id, correct, response_ms, hint_used, timestamp) | `interaction_events` table; each Turn = own row; maps to existing `Turn` dataclass |
| DB-05 | Concept mastery state persisted per child×KC (BKT params + FSRS params) | `mastery_state` table with composite PK (child_id, kc_id); schema in place for Phase 2 to populate |
</phase_requirements>

---

## Summary

Phase 1 replaces two in-memory dicts (`_profiles` and `_sessions`) with a SQLAlchemy 2.0 async ORM layer backed by an Alembic-managed SQLite database. The project already has SQLAlchemy, Alembic, and aiosqlite listed as dependencies in `requirements.txt`, but none are installed in the venv — so installation is the first task. No Alembic migrations directory exists yet; the entire `db/` package and migrations infrastructure must be built from scratch.

The five existing eval tests (`test_answer_reveal`, `test_hint_ladder`, `test_socratic_quality`, `test_lesson_questions`, `test_curriculum_accuracy`) are all gated behind `ANTHROPIC_API_KEY` and import only from `services.tutor` — they do NOT import from `services.profiles` or `services.sessions`. This means the eval guard rails are straightforward: the evals will continue to pass as long as `services/tutor.py` signatures remain unchanged. The risk surface is `api/chat.py`, `api/stt.py`, `api/sessions.py`, and `api/sync.py`, which all currently call the in-memory service functions without a session argument.

The primary design challenge is threading an `AsyncSession` through the call chain. Because the current callers pass no session, every service function touched must gain a `session: AsyncSession` parameter simultaneously with the route handler being updated to inject it via `Depends(get_db)`. TDD mode is enabled — Wave 0 must include CRUD unit tests written against the in-memory fixture before implementation.

**Primary recommendation:** Build `db/` (models → session → crud → seeds) in Wave 0, write CRUD tests against the in-memory fixture, then migrate callers route-by-route in Wave 1 with session injection, removing in-memory fallbacks last.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| ORM model definitions | Database/Storage (`db/models.py`) | — | SQLAlchemy declarative base; schema source of truth |
| Async session lifecycle | Database/Storage (`db/session.py`) | API/Backend (lifespan) | Engine created once; session per-request via FastAPI Depends |
| CRUD operations | Database/Storage (`db/crud.py`) | — | Thin DB accessors; no business logic |
| Service functions (get_child_by_id, log_turn, etc.) | API/Backend (`services/`) | — | Business logic layer; receives session from caller |
| Route handlers | API/Backend (`api/`) | — | Injects `AsyncSession` via `Depends(get_db)`; passes down to services |
| DB init + seed on startup | API/Backend (`api/main.py` lifespan) | Database/Storage (`db/seeds.py`) | lifespan is FastAPI's canonical startup hook |
| Eval test fixtures | Test infrastructure (`tests/conftest.py`) | — | In-memory SQLite; Alembic migrations applied at fixture setup |
| Mastery state schema | Database/Storage (`db/models.py`) | — | Scaffold table now; BKT/FSRS population is Phase 2 |

---

## Standard Stack

### Core

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| sqlalchemy | 2.0.51 [VERIFIED: PyPI] | Async ORM, declarative models, query layer | Only version with native async; project already specifies `>=2.0.0` |
| alembic | 1.18.5 [VERIFIED: PyPI] | Database schema migration management | Official SQLAlchemy migration tool; env.py integrates with async engine |
| aiosqlite | 0.22.1 [VERIFIED: PyPI] | SQLite async driver for SQLAlchemy async | Required by `sqlite+aiosqlite` URL format; already in requirements.txt |
| pytest-asyncio | 1.4.0 [VERIFIED: PyPI] | Async pytest fixtures and test functions | Required to `await` in pytest; `asyncio_mode = "auto"` for clean fixtures |

### Supporting

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| fastapi (already installed indirectly) | >=0.115.0 | `Depends(get_db)` injection | Route handlers only — service functions take explicit session |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| SQLAlchemy 2.0 async | Tortoise ORM | Tortoise is Django-inspired; no benefit given SQLAlchemy already chosen and in requirements |
| Alembic | Manual migrations | No rollback, no auto-generation, not viable for multi-phase project |
| JSON column for lists | Association table | Association table is correct at Phase 2+ scale; D-04 explicitly defers it |

**Installation (packages not yet in venv):**
```bash
pip install sqlalchemy>=2.0.0 alembic>=1.13.0 aiosqlite>=0.20.0 pytest-asyncio
```

---

## Package Legitimacy Audit

> slopcheck was not available at research time. All packages below verified against PyPI directly and cross-checked against official project documentation.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| sqlalchemy | PyPI | 18+ yrs [ASSUMED: well-known] | Very high [ASSUMED] | github.com/sqlalchemy/sqlalchemy | unavailable | Approved — canonical Python ORM, in requirements.txt |
| alembic | PyPI | 13+ yrs [ASSUMED: well-known] | Very high [ASSUMED] | github.com/sqlalchemy/alembic | unavailable | Approved — official SQLAlchemy migration tool, in requirements.txt |
| aiosqlite | PyPI | 5+ yrs [ASSUMED] | High [ASSUMED] | github.com/omnilib/aiosqlite | unavailable | Approved — in requirements.txt; maintained by omnilib |
| pytest-asyncio | PyPI | 7+ yrs [ASSUMED] | Very high [ASSUMED] | github.com/pytest-dev/pytest-asyncio | unavailable | Approved — official pytest-dev org |

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

*slopcheck was unavailable at research time. All packages above are tagged [ASSUMED] on slopcheck column. They are all in the existing requirements.txt or under official project organizations — risk is LOW. No checkpoint:human-verify is needed given they are established ecosystem packages already declared as dependencies.*

---

## Architecture Patterns

### System Architecture Diagram

```
Request (HTTP) → api/chat.py (route handler)
                        │ Depends(get_db) → db/session.py → AsyncSession
                        │
                        ↓
              services/profiles.py → db/crud.py → AsyncSession → SQLite
              services/sessions.py → db/crud.py → AsyncSession → SQLite
                        │
                        ↓
              services/tutor.py (no DB access — builds prompts only)
                        │
                        ↓
              litellm.acompletion() → Anthropic API

Startup (lifespan):
  api/main.py lifespan → create_all / run_migrations
                       → db/seeds.py seed_dev_data() [non-production only]

Eval path:
  tests/conftest.py db_session fixture → in-memory SQLite → Alembic migrations applied
              ↓
  test calls service function(db_session, ...) directly — no HTTP
```

### Recommended Project Structure

```
db/
├── __init__.py          # exports: Base, engine, AsyncSessionLocal, get_db
├── models.py            # ORM models: ChildProfile, Session, InteractionEvent, MasteryState
├── session.py           # AsyncEngine, AsyncSessionLocal, get_db() dependency
├── crud.py              # async CRUD: get_child_by_id, get_child_by_device_id, log_turn, ...
└── seeds.py             # async seed_dev_data(session) — KidA/KidB profiles

tests/
├── conftest.py          # db_session fixture with in-memory SQLite + Alembic migrations
└── evals/               # (unchanged — import from services.tutor only)

services/
├── profiles.py          # thin wrapper: remove _profiles dict; delegate to db/crud.py
└── sessions.py          # thin wrapper: remove _sessions dict; delegate to db/crud.py

api/
└── main.py              # add @asynccontextmanager lifespan; DB init + seed calls
```

### Pattern 1: SQLAlchemy 2.0 Async Declarative Model

**What:** ORM models using `DeclarativeBase` with async `mapped_column` type annotations
**When to use:** All new tables in this phase

```python
# Source: [ASSUMED] SQLAlchemy 2.0 docs pattern
from sqlalchemy import String, Integer, JSON, DateTime
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from datetime import datetime
from typing import Optional

class Base(DeclarativeBase):
    pass

class ChildProfileModel(Base):
    __tablename__ = "child_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    device_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True)
    reading_level: Mapped[str] = mapped_column(String, default="age-appropriate")
    interests: Mapped[list] = mapped_column(JSON, default=list)
    neurodivergence: Mapped[list] = mapped_column(JSON, default=list)
    current_topic: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    current_books: Mapped[list] = mapped_column(JSON, default=list)
    session_count: Mapped[int] = mapped_column(Integer, default=0)
```

### Pattern 2: Async Session Factory and get_db Dependency

**What:** `AsyncSession` factory wired to FastAPI `Depends`
**When to use:** All route handlers that need DB access

```python
# Source: [ASSUMED] FastAPI + SQLAlchemy async pattern
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config.settings import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

### Pattern 3: FastAPI Lifespan Handler for DB Init

**What:** Replace the current no-lifespan `app = FastAPI(...)` with a lifespan context manager
**When to use:** DB engine creation and seed invocation on startup

```python
# Source: [ASSUMED] FastAPI lifespan pattern
from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.session import engine
from db.models import Base
from db.seeds import seed_dev_data
from config.settings import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables if not present (Alembic handles migrations)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed dev data (non-production only)
    settings = get_settings()
    if getattr(settings, "env", "dev") != "production":
        from db.session import AsyncSessionLocal
        async with AsyncSessionLocal() as session:
            await seed_dev_data(session)
    yield
    # Shutdown (optional cleanup)

app = FastAPI(title="eTutor Server", version="0.1.0", lifespan=lifespan)
```

### Pattern 4: Idempotent Upsert Seed (SQLite)

**What:** SQLite `INSERT OR IGNORE` for seeds that run on every startup
**When to use:** `db/seeds.py` seed_dev_data function

```python
# Source: [ASSUMED] SQLite upsert pattern
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from db.models import ChildProfileModel

async def seed_dev_data(session: AsyncSession):
    stmt = sqlite_insert(ChildProfileModel).values(
        id="child-kida",
        name="KidA",
        age=7,
        device_id="device-001",
        interests=["dinosaurs", "space", "Minecraft"],
        reading_level="grade 2",
        current_topic="prehistoric life",
        current_books=[],
    ).prefix_with("OR IGNORE")
    await session.execute(stmt)
    await session.commit()
```

### Pattern 5: pytest Async DB Fixture with In-Memory SQLite

**What:** Create a fresh engine per test, apply Alembic migrations, yield an AsyncSession
**When to use:** All CRUD tests; evals can accept this fixture for new DB-dependent tests

```python
# Source: [ASSUMED] pytest-asyncio + SQLAlchemy pattern
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from db.models import Base

@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    await engine.dispose()
```

**Note on Alembic vs. create_all for tests:** The CONTEXT.md (D-09) says "applies Alembic migrations" in the fixture. For an in-memory SQLite database, running `Base.metadata.create_all` produces the same schema as Alembic migrations and is simpler. Using actual Alembic migrations in the fixture is possible but adds complexity (need to configure a test-specific `alembic.ini` or programmatic invocation). Planner should decide: `create_all` is correct for Phase 1 (single migration, no upgrade path needed in tests); using actual Alembic adds confidence the migration scripts are correct. Both approaches are standard — recommend `create_all` for speed, with a note that Alembic programmatic invocation is the more thorough option.

### Pattern 6: Service Function Signature with Explicit Session

**What:** Service functions gain an `AsyncSession` parameter; callers inject it
**When to use:** All migrated service functions

```python
# Before (in-memory):
async def get_child_by_id(child_id: str) -> Optional[ChildProfile]:
    return _profiles.get(child_id)

# After (DB-backed):
async def get_child_by_id(child_id: str, session: AsyncSession) -> Optional[ChildProfile]:
    from db.crud import get_child_by_id as db_get_child
    return await db_get_child(child_id, session)
```

Route handler companion:
```python
# api/chat.py (after migration)
@router.post("/chat/completions")
async def chat(
    req: ChatRequest,
    x_device_id: str = Header(None),
    x_child_id: str = Header(None),
    session: AsyncSession = Depends(get_db),  # NEW
):
    child = await get_child_by_id(child_id, session)
    ...
    await log_turn(child_id, req.messages[-1].content, content, session=session)
```

### Anti-Patterns to Avoid

- **Calling `seed_dev_profiles()` at import time:** The existing `services/profiles.py` runs `seed_dev_profiles()` at module level. This causes DB I/O at import time once migrated. Remove the module-level call as part of migration.
- **Sync SQLAlchemy in an async service:** The codebase is fully async. Using `Session` instead of `AsyncSession` will block the event loop. Always use `AsyncSession` and `async with`.
- **`create_all` in production:** `Base.metadata.create_all` is fine for dev startup safety net, but Alembic migrations must be the schema change mechanism. Do not rely on `create_all` for schema evolution.
- **Storing JSON lists without default_factory in mapped_column:** JSON columns with mutable defaults need `default=list` (or a callable), not `default=[]`. The latter shares one list across all rows in SQLAlchemy's unit of work.
- **Mixing `Session` and `AsyncSession`:** SQLAlchemy 2.0 has both. The async driver (`aiosqlite`) requires `AsyncSession`. Using the sync `Session` will raise at runtime.

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Schema migrations | Custom ALTER TABLE scripts | Alembic `alembic revision --autogenerate` | Handles column additions, renames, index changes; rollback support |
| Upsert / insert-or-ignore | Manual SELECT then INSERT | SQLite `INSERT OR IGNORE` / SQLAlchemy `insert().prefix_with("OR IGNORE")` | Race conditions, readability |
| Async SQLite connection pooling | Custom connection manager | SQLAlchemy `create_async_engine` with `aiosqlite` | Pool management, thread safety, reconnect logic |
| JSON list serialisation | `json.dumps`/`json.loads` in model methods | SQLAlchemy `JSON` column type | Automatic serialisation/deserialisation; compatible with future PostgreSQL migration |
| Test DB isolation | Manual teardown, shared state | `async_sessionmaker` per-test with in-memory SQLite | Each test gets clean state; no cleanup needed |

**Key insight:** SQLAlchemy's async layer handles all connection lifecycle concerns; Alembic handles all schema evolution. Neither should be replicated with custom code.

---

## Common Pitfalls

### Pitfall 1: `seed_dev_profiles()` Still Running at Import
**What goes wrong:** After adding `db/` layer, if `services/profiles.py` still calls `seed_dev_profiles()` at module level, importing the module triggers in-memory dict population (harmless) but could later cause ordering issues once the function is DB-backed.
**Why it happens:** It's a module-level side effect — easy to miss.
**How to avoid:** Remove the `seed_dev_profiles()` call at module level in `services/profiles.py` during migration. Seeding moves to the lifespan handler.
**Warning signs:** Tests that import `services.profiles` see unexpected state or trigger DB connections.

### Pitfall 2: `api/stt.py` Calls `get_child_by_device_id` Without Session
**What goes wrong:** `api/stt.py` currently imports and calls `get_child_by_device_id(device_id)` — confirmed by code inspection. After migration, this call needs a session.
**Why it happens:** STT does a device lookup but the caller wasn't designed with session injection in mind.
**How to avoid:** Add `session: AsyncSession = Depends(get_db)` to the `transcribe` route and pass it to `get_child_by_device_id`. Alternatively, STT does not strictly need the child profile — consider removing the dead-code path (it stores the result nowhere in `stt.py`).
**Warning signs:** `get_child_by_device_id` is called with 1 arg after migration.

### Pitfall 3: Sessions Table vs. Interaction Events Design Gap
**What goes wrong:** DB-03 requires a `sessions` table (session_id, child_id, started_at, ended_at, turn_count). The existing in-memory model has no `Session` entity — only `Turn` objects grouped by `child_id`. There is currently no session_id concept in `services/sessions.py`. A new session must be created when chat begins and closed when it ends.
**Why it happens:** The in-memory model implicitly aggregates turns per child, not per session. Phase 1 must make sessions explicit.
**How to avoid:** Create a `Session` ORM model. Chat route creates a session on first turn or at request time. `interaction_events` rows reference `session_id`. Plan must include: "create session record when chat starts."
**Warning signs:** DB-03 spec says `session_id, child_id, started_at, ended_at, turn_count` — none of these exist in current code.

### Pitfall 4: `current_topic` and `neurodivergence_block` Template Substitution
**What goes wrong:** `services/tutor.py` accesses `child.neurodivergence` via `getattr(child, "neurodivergence", [])`. After migration, the ORM model must expose the same attribute names as the dataclass (or `build_system_prompt` must be updated to use the ORM model's attribute names).
**Why it happens:** The ORM model is a different class to the `ChildProfile` dataclass. SQLAlchemy model attributes look the same but are instrumented.
**How to avoid:** Name ORM model columns to match dataclass fields exactly. `tutor.py` uses duck typing via `getattr` and attribute access — the ORM model will satisfy this as long as column names match.
**Warning signs:** `AttributeError` on `child.interests`, `child.neurodivergence`, or `child.current_books` in prompt building after migration.

### Pitfall 5: Alembic `env.py` Not Wired for Async
**What goes wrong:** `alembic init` generates a synchronous `env.py`. Running `alembic upgrade head` with an async engine URL (`sqlite+aiosqlite://...`) will fail unless `env.py` uses `run_async_upgrade`.
**Why it happens:** Alembic default template is synchronous; async requires a different invocation pattern.
**How to avoid:** After `alembic init`, replace the online migration block in `env.py` with the async pattern using `asyncio.run(run_async_migrations())`. See Pattern 7 below.
**Warning signs:** `TypeError: coroutine 'connect' was never awaited` or similar when running `alembic upgrade head`.

### Pitfall 6: Missing `data/` Directory
**What goes wrong:** `sqlite+aiosqlite:///./data/etutor.db` fails silently or raises `OperationalError: unable to open database file` if `data/` does not exist.
**Why it happens:** SQLite does not create parent directories automatically.
**How to avoid:** Add `Path("data").mkdir(exist_ok=True)` to the lifespan startup block before engine creation. The `.gitignore` already has `data/etutor.db` and `data/*.db` — the directory itself should not be gitignored (add `data/.gitkeep`).
**Warning signs:** `OperationalError` on server start in a fresh clone.

---

## Code Examples

### Pattern 7: Alembic `env.py` Async Migration Block

```python
# Source: [ASSUMED] SQLAlchemy async Alembic pattern
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from db.models import Base
target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()

def run_migrations_online():
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    # offline mode (generate SQL scripts) — sync path
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
```

### Pattern 8: CRUD get_child_by_id

```python
# Source: [ASSUMED] SQLAlchemy 2.0 async select pattern
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import ChildProfileModel

async def get_child_by_id(child_id: str, session: AsyncSession):
    result = await session.execute(
        select(ChildProfileModel).where(ChildProfileModel.id == child_id)
    )
    return result.scalar_one_or_none()
```

### Pattern 9: DB-05 Mastery State Schema (scaffold for Phase 2)

```python
# Source: [ASSUMED] SQLAlchemy 2.0 declarative
class MasteryStateModel(Base):
    __tablename__ = "mastery_state"

    child_id: Mapped[str] = mapped_column(String, ForeignKey("child_profiles.id"), primary_key=True)
    kc_id: Mapped[str] = mapped_column(String, primary_key=True)
    # BKT fields
    p_mastery: Mapped[float] = mapped_column(Float, default=0.1)
    p_learn: Mapped[float] = mapped_column(Float, default=0.2)
    p_slip: Mapped[float] = mapped_column(Float, default=0.1)
    p_guess: Mapped[float] = mapped_column(Float, default=0.2)
    # FSRS fields
    stability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difficulty_d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    card_state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    next_review: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| SQLAlchemy 1.x `Session` | SQLAlchemy 2.0 `AsyncSession` + `mapped_column` typed annotations | 2023 (2.0 release) | Fully async; type-safe column declarations; no `.query()` API |
| Alembic sync `env.py` | Alembic async `env.py` with `async_engine_from_config` | 2021+ | Required for aiosqlite/asyncpg drivers |
| `pytest-asyncio` `@pytest.mark.asyncio` per test | `asyncio_mode = "auto"` in `pytest.ini` | pytest-asyncio 0.18+ | Removes decorator noise; all async tests run automatically |

**Deprecated/outdated:**
- SQLAlchemy `Session.query()`: replaced by `select()` + `session.execute()` in 2.0 style — do not use `.query()` in new code.
- Module-level `seed_dev_profiles()` in `services/profiles.py`: must be removed; side effects at import time are an anti-pattern.

---

## Open Questions

1. **`api/stt.py` dead-code path**
   - What we know: `stt.py` calls `get_child_by_device_id(device_id)` but does nothing with the result — no variable is assigned, no profile data is used.
   - What's unclear: Is this intentional scaffolding for a future feature, or a dead-code artifact?
   - Recommendation: Remove the call from `stt.py` in Phase 1 (simplest migration path) and re-add when STT needs to personalise on profile data.

2. **Session creation trigger for DB-03**
   - What we know: DB-03 requires a `sessions` table with `session_id, started_at, ended_at, turn_count`. The current code has no session creation event — turns are just appended.
   - What's unclear: Should a new `Session` row be created per HTTP `/chat/completions` call, per device connection, or when the client explicitly starts a session?
   - Recommendation: Create a `Session` row on the first `log_turn` call if no open session exists for the child (implicit session start). Set `ended_at` on an explicit `/sessions/{id}/end` call or via a timeout — Phase 1 can leave `ended_at` nullable and populate it in Phase 3.

3. **`neurodivergence_block` format string `{{` issue**
   - What we know: `SYSTEM_PROMPT_TEMPLATE` in `tutor.py` uses `{neurodivergence_block}`. The current `.format()` call passes `nd_section` which is an empty string or a block. This works today.
   - What's unclear: If the ORM model returns `None` instead of `[]` for `neurodivergence`, `getattr(child, "neurodivergence", [])` will still return `[]` — no issue. But `nd_flags or []` check should remain.
   - Recommendation: Map ORM column default to `[]` not `None` to avoid defensive coding in tutor.py.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python 3.14 | All | ✓ | 3.14 (from venv path) | — |
| pytest | Test runner | ✓ | 9.1.1 | — |
| sqlalchemy | ORM layer | ✗ (not in venv) | — (2.0.51 on PyPI) | None — must install |
| alembic | Migrations | ✗ (not in venv) | — (1.18.5 on PyPI) | None — must install |
| aiosqlite | SQLite async driver | ✗ (not in venv) | — (0.22.1 on PyPI) | None — must install |
| pytest-asyncio | Async test fixtures | ✗ (not in venv) | — (1.4.0 on PyPI) | None — must install for TDD wave |
| data/ directory | SQLite file path | ✗ (does not exist) | — | Create at startup via `Path("data").mkdir(exist_ok=True)` |

**Missing dependencies with no fallback:**
- `sqlalchemy`, `alembic`, `aiosqlite`, `pytest-asyncio` — all listed in `requirements.txt` but not installed. Wave 0 must run `pip install` before any test or model code can execute.

**Missing dependencies with fallback:**
- `data/` directory — created at startup; no blocker.

---

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | pytest 9.1.1 |
| Config file | `pytest.ini` (does not exist yet — Wave 0 gap) |
| Quick run command | `pytest tests/ -x --ignore=tests/evals -q` |
| Full suite command | `pytest tests/ -q` (evals skip without ANTHROPIC_API_KEY) |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DB-01 | SQLAlchemy engine connects; table created | unit | `pytest tests/db/test_session.py -x` | ❌ Wave 0 |
| DB-02 | ChildProfile CRUD: create, read by id, read by device_id, update interests | unit | `pytest tests/db/test_crud_profiles.py -x` | ❌ Wave 0 |
| DB-03 | Session record: create, read, turn_count increments | unit | `pytest tests/db/test_crud_sessions.py -x` | ❌ Wave 0 |
| DB-04 | InteractionEvent: log_turn creates row with all fields | unit | `pytest tests/db/test_crud_events.py -x` | ❌ Wave 0 |
| DB-05 | MasteryState: create row, read by (child_id, kc_id) | unit | `pytest tests/db/test_crud_mastery.py -x` | ❌ Wave 0 |
| D-09 | Eval fixture: db_session uses in-memory SQLite | unit | `pytest tests/test_fixtures.py -x` | ❌ Wave 0 |
| D-06 | Seeds are idempotent (run twice, same row count) | unit | `pytest tests/db/test_seeds.py -x` | ❌ Wave 0 |
| Regression | Existing evals continue to pass | eval | `pytest tests/evals/ -q` (requires API key) | ✓ existing |

### Sampling Rate

- **Per task commit:** `pytest tests/db/ -x -q`
- **Per wave merge:** `pytest tests/ -x -q` (evals skip without API key)
- **Phase gate:** All DB unit tests green + evals green (with API key) before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] `pytest.ini` — needs `asyncio_mode = auto` for pytest-asyncio
- [ ] `tests/conftest.py` — `db_session` fixture (async, in-memory SQLite, create_all)
- [ ] `tests/db/test_crud_profiles.py` — covers DB-02
- [ ] `tests/db/test_crud_sessions.py` — covers DB-03
- [ ] `tests/db/test_crud_events.py` — covers DB-04
- [ ] `tests/db/test_crud_mastery.py` — covers DB-05
- [ ] `tests/db/test_seeds.py` — covers D-06 idempotency
- [ ] `tests/db/__init__.py` — package marker

---

## Security Domain

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | No (Phase 1 is internal DB layer) | — |
| V3 Session Management | Partial (sessions table exists) | Session IDs as UUID4; no auth tokens in Phase 1 |
| V4 Access Control | No | — |
| V5 Input Validation | Yes — child_id, device_id from HTTP headers | Already validated via HTTPException 400 in chat.py; ORM parameterised queries prevent SQL injection |
| V6 Cryptography | No | — |

### Known Threat Patterns

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| SQL injection via child_id / device_id headers | Tampering | SQLAlchemy ORM parameterised queries — never string-interpolated SQL |
| Seed data containing PII | Information Disclosure | D-08 enforces generic IDs (KidA/KidB); no real names in code |
| `data/` directory world-readable | Information Disclosure | Add `data/` to `.gitignore` (already done); ensure server runs as non-root |

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | sqlalchemy 2.0.51, alembic 1.18.5, aiosqlite 0.22.1, pytest-asyncio 1.4.0 are current PyPI versions | Standard Stack | Minor — version pinning difference only; install from requirements.txt minimums is safe |
| A2 | pytest-asyncio `asyncio_mode = "auto"` is the correct config key for v1.x | Validation Architecture | Planner should verify against pytest-asyncio 1.x changelog; key name may differ |
| A3 | SQLAlchemy `JSON` column type serialises Python lists transparently in aiosqlite | Architecture Patterns | If wrong, must use `String` column + manual `json.dumps/loads`; low risk given this is well-established |
| A4 | `INSERT OR IGNORE` is supported via `.prefix_with("OR IGNORE")` on SQLAlchemy `insert()` statement for SQLite | Architecture Patterns | Alternative is `on_conflict_do_nothing()` from `sqlalchemy.dialects.sqlite` — either works |
| A5 | All 5 eval tests are gated on `ANTHROPIC_API_KEY` and will skip in CI without it | Common Pitfalls | If any eval lacks the skipif guard, it will fail without credentials |

---

## Sources

### Primary (HIGH confidence)

- Codebase inspection (`services/profiles.py`, `services/sessions.py`, `api/chat.py`, `api/stt.py`, `api/main.py`, `config/settings.py`) — direct reading of all integration points
- `requirements.txt` — confirmed sqlalchemy, alembic, aiosqlite declared but not installed
- PyPI API queries — confirmed current versions: sqlalchemy 2.0.51, alembic 1.18.5, aiosqlite 0.22.1, pytest-asyncio 1.4.0
- `tests/evals/*.py` imports — confirmed all 5 evals import only from `services.tutor`, not profiles/sessions

### Secondary (MEDIUM confidence)

- `.planning/phases/01-database-foundation/01-CONTEXT.md` — locked decisions D-01 through D-10

### Tertiary (LOW confidence — training knowledge)

- SQLAlchemy 2.0 async patterns, Alembic async env.py pattern, pytest-asyncio fixture pattern — training data; verify against official docs before implementing
- `asyncio_mode = "auto"` pytest-asyncio config key — needs verification against v1.x docs

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified via PyPI; packages already in requirements.txt
- Architecture: MEDIUM — patterns from training knowledge; official docs not fetched (ctx7 unavailable)
- Pitfalls: HIGH — derived from direct codebase inspection of integration points

**Research date:** 2026-07-14
**Valid until:** 2026-08-14 (stable ecosystem; SQLAlchemy/Alembic rarely have breaking changes within minor versions)
