# Phase 1: Database Foundation - Pattern Map

**Mapped:** 2026-07-14
**Files analyzed:** 23 (14 new, 9 modified)
**Analogs found:** 9 / 23 (9 from real codebase; 14 new files have no codebase analog — use RESEARCH.md patterns)

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `db/__init__.py` | package-init | — | none | none |
| `db/models.py` | model | CRUD | none (greenfield) | none |
| `db/session.py` | config/utility | request-response | `config/settings.py` | partial (config pattern) |
| `db/crud.py` | service | CRUD | `services/profiles.py` | role-match (same operations, different backend) |
| `db/seeds.py` | utility | CRUD | `services/profiles.py` `seed_dev_profiles()` | role-match |
| `tests/conftest.py` | test fixture | — | none | none |
| `tests/db/__init__.py` | package-init | — | none | none |
| `tests/db/test_crud_profiles.py` | test | CRUD | `tests/evals/test_answer_reveal.py` | partial (test file structure) |
| `tests/db/test_crud_sessions.py` | test | CRUD | `tests/evals/test_answer_reveal.py` | partial |
| `tests/db/test_crud_events.py` | test | CRUD | `tests/evals/test_answer_reveal.py` | partial |
| `tests/db/test_crud_mastery.py` | test | CRUD | `tests/evals/test_answer_reveal.py` | partial |
| `tests/db/test_seeds.py` | test | CRUD | `tests/evals/test_answer_reveal.py` | partial |
| `pytest.ini` | config | — | none | none |
| `migrations/env.py` | config | — | none | none |
| `services/profiles.py` *(modify)* | service | CRUD | itself | exact (migrate in-place) |
| `services/sessions.py` *(modify)* | service | CRUD | itself | exact (migrate in-place) |
| `api/main.py` *(modify)* | entrypoint | request-response | itself | exact (add lifespan) |
| `api/chat.py` *(modify)* | controller | request-response | itself | exact (add Depends) |
| `api/stt.py` *(modify)* | controller | request-response | itself | exact (remove dead call) |
| `api/sessions.py` *(modify)* | controller | request-response | `api/chat.py` | role-match |
| `api/sync.py` *(modify)* | controller | request-response | `api/chat.py` | role-match |
| `api/child.py` *(modify)* | controller | request-response | `api/chat.py` | role-match |
| `api/parent.py` *(modify)* | controller | request-response | `api/chat.py` | role-match |

---

## Pattern Assignments

### `db/__init__.py` (package-init)

**Analog:** none — standard Python package init
**Pattern:** Empty or re-export key symbols so callers can do `from db import get_db, Base`.

```python
# Minimal — just a package marker; re-exports added once models/session exist
```

---

### `db/models.py` (model, CRUD)

**Analog:** none in codebase. Use RESEARCH.md Pattern 1 + Pattern 9 directly.

**Source dataclass to mirror** (`services/profiles.py` lines 11-40):
```python
@dataclass
class ChildProfile:
    id: str
    name: str
    age: int
    device_id: Optional[str] = None
    interests: list[str] = field(default_factory=list)
    reading_level: str = "age-appropriate"
    current_topic: Optional[str] = None
    current_books: list[str] = field(default_factory=list)
    session_count: int = 0
    neurodivergence: list[str] = field(default_factory=list)
```

**Source Turn dataclass to mirror** (`services/sessions.py` lines 9-16):
```python
@dataclass
class Turn:
    id: str
    child_id: str
    question: str
    answer: str
    timestamp: str
    topic: Optional[str] = None
```

**ORM model pattern** (from RESEARCH.md Pattern 1 — no codebase analog exists):
```python
from sqlalchemy import String, Integer, JSON, DateTime, Float, ForeignKey
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

**Critical:** Column names MUST match the `ChildProfile` dataclass field names exactly. `services/tutor.py` uses `child.neurodivergence`, `child.interests`, `child.current_topic`, `child.current_books`, `child.name`, `child.age`, `child.reading_level` via attribute access (lines 210-228 of `services/tutor.py`). A name mismatch causes `AttributeError` at prompt-build time.

**Session model** (DB-03 — no existing in-memory analog; must be created):
```python
class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID4
    child_id: Mapped[str] = mapped_column(String, ForeignKey("child_profiles.id"), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    # turn_count is derived — do not store; compute from interaction_events JOIN
```

**InteractionEvent model** (DB-04, maps to Turn dataclass):
```python
class InteractionEventModel(Base):
    __tablename__ = "interaction_events"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # UUID4
    child_id: Mapped[str] = mapped_column(String, ForeignKey("child_profiles.id"), nullable=False, index=True)
    session_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("sessions.id"), nullable=True)
    question: Mapped[str] = mapped_column(String, nullable=False)
    answer: Mapped[str] = mapped_column(String, nullable=False)
    topic: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

**MasteryState model** (DB-05 scaffold — from RESEARCH.md Pattern 9):
```python
class MasteryStateModel(Base):
    __tablename__ = "mastery_state"

    child_id: Mapped[str] = mapped_column(String, ForeignKey("child_profiles.id"), primary_key=True)
    kc_id: Mapped[str] = mapped_column(String, primary_key=True)
    p_mastery: Mapped[float] = mapped_column(Float, default=0.1)
    p_learn: Mapped[float] = mapped_column(Float, default=0.2)
    p_slip: Mapped[float] = mapped_column(Float, default=0.1)
    p_guess: Mapped[float] = mapped_column(Float, default=0.2)
    stability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difficulty_d: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    card_state: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    next_review: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
```

---

### `db/session.py` (config/utility, request-response)

**Analog:** `config/settings.py` (lines 1-31) — shows the project's pattern for module-level singletons with `lru_cache` and lazy init.

**Settings pattern to reference** (`config/settings.py` lines 1-31):
```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./data/etutor.db"
    ...

@lru_cache
def get_settings() -> Settings:
    return Settings()
```

**Session factory pattern** (from RESEARCH.md Pattern 2 — no codebase analog):
```python
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from config.settings import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
```

Note: `get_settings()` is already `lru_cache`-wrapped in `config/settings.py` — call it at module level here safely.

---

### `db/crud.py` (service, CRUD)

**Analog:** `services/profiles.py` (whole file) — same operations, same return types, same function names. Direct port with session parameter added.

**Function signatures to mirror** (`services/profiles.py` lines 74-93):
```python
async def get_child_by_device_id(device_id: str) -> Optional[ChildProfile]:
async def get_child_by_id(child_id: str) -> Optional[ChildProfile]:
async def list_children() -> list[ChildProfile]:
async def update_interests(child_id: str, new_interests: list[str]):
```

**After migration — all gain `session: AsyncSession` parameter:**
```python
async def get_child_by_id(child_id: str, session: AsyncSession):
    result = await session.execute(
        select(ChildProfileModel).where(ChildProfileModel.id == child_id)
    )
    return result.scalar_one_or_none()
```

**Turn/event functions to mirror** (`services/sessions.py` lines 19-40):
```python
async def log_turn(child_id: str, question: str, answer: str, topic: str = None):
async def get_session_history(child_id: str, limit: int = 50) -> list[Turn]:
async def get_all_sessions() -> dict[str, list[Turn]]:
```

**Return type note:** `get_session_history` currently returns `list[Turn]` (dataclass). After migration it returns `list[InteractionEventModel]`. Callers in `api/sessions.py` use `vars(t)` (line 10) — SQLAlchemy model objects do not support `vars()`. The planner must update `api/sessions.py` to serialise ORM objects explicitly (e.g. `t.__dict__` with `_sa_instance_state` stripped, or a Pydantic schema).

---

### `db/seeds.py` (utility, CRUD)

**Analog:** `services/profiles.py` lines 42-71 — the existing `seed_dev_profiles()` function is the direct predecessor. Copy structure but use SQLAlchemy upsert instead of dict assignment.

**Existing seed to replace** (`services/profiles.py` lines 42-71):
```python
def seed_dev_profiles():
    profiles = [
        ChildProfile(
            id="child-001",
            name="Alex",       # REAL NAME — must be replaced with KidA per D-08
            age=7,
            device_id="device-001",
            interests=["dinosaurs", "space", "Minecraft"],
            reading_level="grade 2",
            current_topic="prehistoric life",
            current_books=["My Big Dinosaur Book"],
        ),
        ChildProfile(
            id="child-002",
            name="Sam",        # REAL NAME — must be replaced with KidB per D-08
            ...
        ),
    ]
```

**New upsert pattern** (from RESEARCH.md Pattern 4):
```python
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

async def seed_dev_data(session: AsyncSession):
    stmt = sqlite_insert(ChildProfileModel).values(
        id="child-kida",
        name="KidA",           # generic per D-08
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

**Critical:** The module-level `seed_dev_profiles()` call at `services/profiles.py` line 71 MUST be removed when migrating that file. Importing `services.profiles` must not trigger DB I/O.

---

### `tests/conftest.py` (test fixture)

**Analog:** `tests/evals/test_answer_reveal.py` — shows existing pytest structure (imports, parametrize, skipif). Does not have async fixtures yet.

**Existing test structure** (`tests/evals/test_answer_reveal.py` lines 183-199):
```python
import pytest

@pytest.mark.parametrize("case", CASES, ids=[...])
@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set — skipping live eval"
)
def test_does_not_reveal_answer(case):
    revealed, response = asyncio.get_event_loop().run_until_complete(
        run_case(case, MODEL)
    )
    assert not revealed, ...
```

Note: Evals use `asyncio.get_event_loop().run_until_complete()` — sync test wrappers. The new DB fixtures use `pytest-asyncio` with `asyncio_mode = "auto"`, which is a different pattern. Do not copy the eval async style for DB tests.

**New fixture pattern** (from RESEARCH.md Pattern 5):
```python
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

---

### `tests/db/test_crud_profiles.py`, `test_crud_sessions.py`, `test_crud_events.py`, `test_crud_mastery.py`, `test_seeds.py` (test, CRUD)

**Analog:** `tests/evals/test_answer_reveal.py` — shows module docstring, import block, pytest parametrize convention.

**Module docstring convention** (`tests/evals/test_answer_reveal.py` lines 1-16):
```python
"""
Eval 1: Answer-Reveal Rate Audit
=================================
[description]

Run:
    pytest tests/... -v
"""
```

**Test body pattern** (use async test functions with `db_session` fixture from conftest):
```python
import pytest
from db.crud import get_child_by_id, create_child

async def test_get_child_by_id_returns_none_for_unknown(db_session):
    result = await get_child_by_id("nonexistent", db_session)
    assert result is None

async def test_create_and_retrieve_child(db_session):
    await create_child(db_session, id="test-001", name="KidA", age=7, ...)
    child = await get_child_by_id("test-001", db_session)
    assert child.name == "KidA"
```

---

### `pytest.ini` (config)

**Analog:** none existing. New file.

**Required content** (from RESEARCH.md Validation Architecture):
```ini
[pytest]
asyncio_mode = auto
```

Note: RESEARCH.md flags assumption A2 — verify `asyncio_mode = auto` is the correct key for pytest-asyncio 1.x before finalising. The key was `asyncio_mode` in 0.21+; 1.x should retain it.

---

### `migrations/env.py` (config, Alembic)

**Analog:** none existing. Greenfield.

**Async env.py pattern** (from RESEARCH.md Pattern 7 / Code Examples):
```python
import asyncio
from logging.config import fileConfig
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from db.models import Base

target_metadata = Base.metadata

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
```

**Critical:** Standard `alembic init` generates a sync `env.py`. It MUST be replaced with the async block above before running `alembic upgrade head` — otherwise aiosqlite driver raises `TypeError: coroutine 'connect' was never awaited`.

---

### `services/profiles.py` *(modify)* (service, CRUD)

**Analog:** itself — migrate in-place.

**Current import block** (lines 1-4):
```python
from dataclasses import dataclass, field
from typing import Optional
import json
```

**After migration, imports become:**
```python
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.crud import (
    get_child_by_id as db_get_child_by_id,
    get_child_by_device_id as db_get_child_by_device_id,
    list_children as db_list_children,
    update_interests as db_update_interests,
)
```

**Current in-memory dict to remove** (lines 6-7):
```python
_profiles: dict[str, "ChildProfile"] = {}
_device_map: dict[str, str] = {}
```

**Current module-level side effect to remove** (line 71):
```python
seed_dev_profiles()   # DELETE THIS — replace with lifespan-based seeding
```

**Current function signatures** (lines 74-93):
```python
async def get_child_by_device_id(device_id: str) -> Optional[ChildProfile]:
async def get_child_by_id(child_id: str) -> Optional[ChildProfile]:
async def list_children() -> list[ChildProfile]:
async def update_interests(child_id: str, new_interests: list[str]):
```

**After migration — add `session` parameter to all:**
```python
async def get_child_by_id(child_id: str, session: AsyncSession):
    return await db_get_child_by_id(child_id, session)
```

**ChildProfile dataclass:** Keep the dataclass definition in `services/profiles.py` for the duration of Phase 1, OR remove it and have callers use the ORM model directly. Planner decision: keeping it for Phase 1 avoids changing the type annotations in `services/tutor.py`, but returning ORM objects from `db/crud.py` instead of dataclass instances is simpler. Since `services/tutor.py` uses only attribute access (duck typing), returning ORM model instances satisfies all callers without keeping the dataclass.

---

### `services/sessions.py` *(modify)* (service, CRUD)

**Analog:** itself — migrate in-place.

**Current import block** (lines 1-5):
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid
```

**Current in-memory dict to remove** (line 6):
```python
_sessions: dict[str, list] = {}
```

**Current function signatures** (lines 19-40):
```python
async def log_turn(child_id: str, question: str, answer: str, topic: str = None):
async def get_session_history(child_id: str, limit: int = 50) -> list[Turn]:
async def get_all_sessions() -> dict[str, list[Turn]]:
```

**After migration:**
```python
async def log_turn(child_id: str, question: str, answer: str, session: AsyncSession, topic: str = None):
    return await db_log_turn(child_id, question, answer, session, topic)

async def get_session_history(child_id: str, session: AsyncSession, limit: int = 50):
    return await db_get_session_history(child_id, session, limit)
```

Note: `api/chat.py` calls `log_turn` with keyword arg style (line 60): `await log_turn(child_id, req.messages[-1].content, content)`. Adding `session` as a required positional argument AFTER `answer` (before `topic`) will break this call site — use keyword-only or keep `session` as last non-default arg. Recommend: `log_turn(child_id, question, answer, session, topic=None)`.

---

### `api/main.py` *(modify)* (entrypoint)

**Analog:** itself — add lifespan to existing file.

**Current state** (lines 1-36):
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from api import stt, chat, sync, sessions, dashboard
from api.child import router as child_router
from api.parent import router as parent_router

app = FastAPI(title="eTutor Server", version="0.1.0")
# ... middleware, routers, static mount, health endpoint
```

**After migration — add lifespan block** (from RESEARCH.md Pattern 3):
```python
from contextlib import asynccontextmanager
from pathlib import Path
from db.session import engine, AsyncSessionLocal
from db.models import Base
from db.seeds import seed_dev_data
from config.settings import get_settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure data/ directory exists for SQLite file
    Path("data").mkdir(exist_ok=True)
    # Create tables (Alembic handles evolution; create_all is startup safety net)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed dev data — non-production only (D-06)
    settings = get_settings()
    if getattr(settings, "env", "dev") != "production":
        async with AsyncSessionLocal() as session:
            await seed_dev_data(session)
    yield

app = FastAPI(title="eTutor Server", version="0.1.0", lifespan=lifespan)
```

All existing routers, middleware, and the `/health` endpoint remain unchanged.

---

### `api/chat.py` *(modify)* (controller, request-response)

**Analog:** itself — add `Depends(get_db)` to route and thread session to service calls.

**Current route signature** (lines 26-31):
```python
@router.post("/chat/completions")
async def chat(
    req: ChatRequest,
    x_device_id: str = Header(None),
    x_child_id: str = Header(None),
):
```

**After migration:**
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db

@router.post("/chat/completions")
async def chat(
    req: ChatRequest,
    x_device_id: str = Header(None),
    x_child_id: str = Header(None),
    session: AsyncSession = Depends(get_db),   # NEW
):
    child_id = x_child_id or req.child_id
    if not child_id and x_device_id:
        child = await get_child_by_device_id(x_device_id, session)   # session added
        ...
    child = await get_child_by_id(child_id, session)                 # session added
    ...
    await log_turn(child_id, req.messages[-1].content, content, session)  # session added
```

**Existing error handling to keep** (lines 38-40):
```python
if not child_id:
    raise HTTPException(status_code=400, detail="No child identity — provide X-Child-ID or X-Device-ID header")
```

---

### `api/stt.py` *(modify)* (controller, request-response)

**Analog:** itself.

**Dead-code import to remove** (line 7):
```python
from services.profiles import get_child_by_device_id   # REMOVE — result is never used
```

**Dead-code call to remove** (not present in current file — confirmed: `stt.py` imports `get_child_by_device_id` but the function `transcribe` does NOT call it). The import itself is dead. Remove the import line.

Confirmed from reading `api/stt.py`: the `get_child_by_device_id` import exists at line 7 but is unused in the `transcribe` function body. The RESEARCH.md pitfall description was slightly inaccurate — it's an unused import, not an active call. Either way: remove the import (D per RESEARCH.md recommendation).

---

### `api/sessions.py` *(modify)* (controller, request-response)

**Analog:** `api/chat.py` — same Depends(get_db) injection pattern.

**Current state** (lines 1-10):
```python
from fastapi import APIRouter
from services.sessions import get_session_history

router = APIRouter()

@router.get("/sessions/{child_id}")
async def get_sessions(child_id: str, limit: int = 50):
    turns = await get_session_history(child_id, limit)
    return {"child_id": child_id, "turns": [vars(t) for t in turns]}
```

**After migration:**
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
from services.sessions import get_session_history

@router.get("/sessions/{child_id}")
async def get_sessions(child_id: str, limit: int = 50, session: AsyncSession = Depends(get_db)):
    turns = await get_session_history(child_id, session, limit)
    # vars(t) does not work on ORM objects — serialise explicitly:
    return {"child_id": child_id, "turns": [
        {"id": t.id, "child_id": t.child_id, "question": t.question,
         "answer": t.answer, "timestamp": t.timestamp.isoformat(), "topic": t.topic}
        for t in turns
    ]}
```

---

### `api/sync.py` *(modify)* (controller, request-response)

**Analog:** `api/chat.py` — Depends(get_db) injection pattern.

**Current state** (lines 1-27): imports `get_child_by_device_id` and calls it without a session.

**After migration:** add `session: AsyncSession = Depends(get_db)` to `sync_device` and pass to `get_child_by_device_id(device_id, session)`.

---

### `api/child.py` *(modify)* (controller, request-response)

**Analog:** `api/chat.py`.

**Current state** (`api/child.py` lines 1-24): `list_children()` and `get_child_by_id()` called without session.

**After migration:** both route functions get `session: AsyncSession = Depends(get_db)` and pass it to service functions.

---

### `api/parent.py` *(modify)* (controller, request-response)

**Analog:** `api/chat.py`.

**Current state** (`api/parent.py` lines 1-19): `list_children()` and `get_all_sessions()` called without session.

**After migration:** `parent_dashboard` gets `session: AsyncSession = Depends(get_db)` and passes it to both service calls. `get_all_sessions` return type changes (was `dict[str, list[Turn]]`, becomes a list of `InteractionEventModel`). Template `dashboard.html` must tolerate the new shape — planner should verify template usage.

---

## Shared Patterns

### FastAPI `Depends(get_db)` injection
**Source:** RESEARCH.md Pattern 2 + `api/chat.py` as the first modified example
**Apply to:** `api/chat.py`, `api/sessions.py`, `api/sync.py`, `api/child.py`, `api/parent.py`
```python
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db

# In any route handler:
async def my_route(..., session: AsyncSession = Depends(get_db)):
    ...
```

### Settings access pattern
**Source:** `config/settings.py` lines 28-31
**Apply to:** `db/session.py`, `api/main.py` lifespan
```python
from config.settings import get_settings

settings = get_settings()   # lru_cache — safe to call at module level
```

### HTTPException error pattern
**Source:** `api/chat.py` lines 38-40
**Apply to:** Any route that needs to return 400/404
```python
from fastapi import HTTPException

raise HTTPException(status_code=400, detail="No child identity — provide X-Child-ID or X-Device-ID header")
```

### Async service function signature
**Source:** `services/profiles.py` lines 74-93, `services/sessions.py` lines 19-40
**Apply to:** All new `db/crud.py` functions and migrated service wrappers
```python
# Pattern: async + explicit session + Optional return type
async def get_child_by_id(child_id: str, session: AsyncSession) -> Optional[ChildProfileModel]:
    ...
```

### Async settings access in lifespan
**Source:** `api/main.py` existing `from config.settings import get_settings` + RESEARCH.md Pattern 3
**Apply to:** `api/main.py` lifespan block, `db/seeds.py`
```python
from config.settings import get_settings
settings = get_settings()
if getattr(settings, "env", "dev") != "production":
    ...
```

---

## No Analog Found

Files with no close match in the codebase (planner must use RESEARCH.md patterns):

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `db/models.py` | model | CRUD | No ORM models exist anywhere in the codebase |
| `db/session.py` | config/utility | request-response | No SQLAlchemy session management exists yet |
| `db/crud.py` | service | CRUD | No DB-backed CRUD exists yet (only in-memory dicts) |
| `db/seeds.py` | utility | CRUD | Only precursor is the in-memory `seed_dev_profiles()` |
| `tests/conftest.py` | test fixture | — | No pytest fixtures exist; no conftest.py in project |
| `pytest.ini` | config | — | No pytest.ini exists in project |
| `migrations/env.py` | config | — | No Alembic directory exists in project |

All 7 greenfield files should follow the explicit patterns in RESEARCH.md §Architecture Patterns and §Code Examples (Patterns 1–9), which are based on SQLAlchemy 2.0 + Alembic official documentation patterns.

---

## Metadata

**Analog search scope:** `/Users/scowan/Projects/scottcowan/etutor-server` (all `.py` files excluding `.venv/`)
**Files scanned:** 21 project Python files
**Pattern extraction date:** 2026-07-14
**Key finding:** The codebase has no existing SQLAlchemy, Alembic, or pytest-asyncio usage. All `db/` package files and migration infrastructure are greenfield. The only real codebase analogs are the service files being migrated (`services/profiles.py`, `services/sessions.py`) and the route handlers being modified (`api/chat.py` as the primary Depends injection template). RESEARCH.md patterns are the authoritative source for all new `db/` package files.
