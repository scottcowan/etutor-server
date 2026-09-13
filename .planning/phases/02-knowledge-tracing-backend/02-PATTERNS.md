# Phase 2: Knowledge Tracing Backend - Pattern Map

**Mapped:** 2026-07-16
**Files analyzed:** 11 new/modified files
**Analogs found:** 11 / 11

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `services/knowledge_tracing.py` | service | CRUD + batch | `services/sessions.py` + `db/crud.py` | role-match |
| `db/models.py` | model | CRUD | `db/models.py` (MasteryStateModel) | exact |
| `db/crud.py` | data-access | CRUD | `db/crud.py` (create_or_get_mastery_state) | exact |
| `api/sessions.py` | route | request-response | `api/sessions.py` + `api/chat.py` | exact |
| `services/tutor.py` | service | transform | `services/tutor.py` (build_system_prompt) | exact |
| `api/chat.py` | route | request-response | `api/chat.py` (existing call site) | exact |
| `migrations/versions/{hash}_add_child_fsrs_params.py` | migration | batch | `migrations/versions/9f229414e92b_initial_schema.py` | exact |
| `tests/services/test_knowledge_tracing.py` | test | unit + integration | `tests/db/test_crud_mastery.py` | role-match |
| `tests/services/test_tutor.py` | test | unit | `tests/db/test_crud_mastery.py` | role-match |
| `tests/api/test_session_end.py` | test | integration | `tests/api/test_chat_db_wiring.py` | exact |
| `requirements.txt` | config | — | `requirements.txt` (existing) | exact |

---

## Pattern Assignments

### `services/knowledge_tracing.py` (service, CRUD + batch)

**Analogs:** `services/sessions.py` (async service wrapper pattern), `db/crud.py` (select + commit pattern)

**Imports pattern** — copy from `services/sessions.py` lines 1–18 and `db/crud.py` lines 1–26:
```python
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ChildProfileModel, InteractionEventModel, MasteryStateModel
from db.crud import create_or_get_mastery_state, update_mastery_state, get_child_by_id
from services.curriculum import Topic
```

**Async service function signature pattern** — `services/sessions.py` lines 21–29:
```python
async def log_turn(
    child_id: str,
    question: str,
    answer: str,
    session: AsyncSession,
    topic: str = None,
    session_id: str = None,
):
    return await db_log_turn(child_id, question, answer, session, topic=topic, session_id=session_id)
```
Key rules: all functions are `async`, `session: AsyncSession` is an explicit parameter (not injected), keyword-only optional params follow positional required params.

**SELECT with filter pattern** — `db/crud.py` lines 62–68 and 153–170:
```python
result = await session.execute(
    select(ChildProfileModel).where(ChildProfileModel.id == child_id)
)
return result.scalar_one_or_none()

# Multi-row select with ordering:
result = await session.execute(
    select(InteractionEventModel)
    .where(InteractionEventModel.child_id == child_id)
    .order_by(InteractionEventModel.timestamp.desc())
    .limit(limit)
)
rows = list(result.scalars().all())
```

**Upsert (get-or-create) pattern** — `db/crud.py` lines 177–190:
```python
async def create_or_get_mastery_state(
    child_id: str,
    kc_id: str,
    session: AsyncSession,
) -> MasteryStateModel:
    existing = await session.get(MasteryStateModel, (child_id, kc_id))
    if existing:
        return existing
    model = MasteryStateModel(child_id=child_id, kc_id=kc_id)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model
```
Apply same pattern for `upsert_child_fsrs_params`: `await session.get(ChildFSRSParamsModel, child_id)`, update if found, `session.add(...)` if new, `await session.commit()`.

**Field-update pattern** — `db/crud.py` lines 193–211:
```python
async def update_mastery_state(
    child_id: str,
    kc_id: str,
    session: AsyncSession,
    **fields,
) -> None:
    model = await session.get(MasteryStateModel, (child_id, kc_id))
    if model is None:
        raise ValueError(f"MasteryState not found for ({child_id}, {kc_id})")
    for k, v in fields.items():
        setattr(model, k, v)
    model.updated_at = datetime.now(timezone.utc)
    await session.commit()
```
The `update_bkt_for_session()` function calls `create_or_get_mastery_state()` then `update_mastery_state()` for each KC — no direct `setattr` in the service layer.

**DateTime convention** — `db/models.py` lines 47, 65, 91:
```python
# Always timezone-aware UTC:
default=lambda: datetime.now(timezone.utc)
# Never datetime.utcnow() — returns naive datetime
```

---

### `db/models.py` — add `ChildFSRSParamsModel` (model, CRUD)

**Analog:** `db/models.py` — `ChildProfileModel` (lines 23–36) and `MasteryStateModel` (lines 73–91)

**Imports block** — `db/models.py` lines 15–16 (already present, no change needed):
```python
from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
```

**Single-PK model with FK pattern** — `db/models.py` lines 39–48 (`SessionModel`):
```python
class SessionModel(Base):
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), nullable=False, index=True
    )
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    ended_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
```

**JSON column pattern** — `db/models.py` lines 32–33 (`ChildProfileModel`):
```python
interests: Mapped[list] = mapped_column(JSON, default=list)
```
Use `Mapped[list]` with `JSON` column type (not `String`) — project already uses JSON columns for Python list/dict values. For `ChildFSRSParamsModel.weights`, use `Mapped[list]` with `JSON` so SQLAlchemy handles serialisation automatically.

**New model to add** (from RESEARCH.md — use JSON column variant):
```python
class ChildFSRSParamsModel(Base):
    """Per-child FSRS-5 fitted weight vector (D-06)."""
    __tablename__ = "child_fsrs_params"

    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), primary_key=True
    )
    weights: Mapped[list] = mapped_column(JSON, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
```
Also add `ChildFSRSParamsModel` to the import in `db/crud.py` line 25.

---

### `db/crud.py` — add FSRS params CRUD (data-access, CRUD)

**Analog:** `db/crud.py` — `create_or_get_mastery_state` (lines 177–190) and `update_mastery_state` (lines 193–211)

**Two functions to add — `get_child_fsrs_params` and `upsert_child_fsrs_params`:**

`get_child_fsrs_params` follows the `get_child_by_id` pattern (lines 61–68):
```python
async def get_child_by_id(
    child_id: str, session: AsyncSession
) -> Optional[ChildProfileModel]:
    result = await session.execute(
        select(ChildProfileModel).where(ChildProfileModel.id == child_id)
    )
    return result.scalar_one_or_none()
```

`upsert_child_fsrs_params` follows the `create_or_get_mastery_state` get-or-create + conditional-update pattern (lines 177–190):
```python
existing = await session.get(MasteryStateModel, (child_id, kc_id))
if existing:
    return existing
model = MasteryStateModel(child_id=child_id, kc_id=kc_id)
session.add(model)
await session.commit()
await session.refresh(model)
return model
```
For upsert (not get-or-create), use the same `session.get()` lookup but update fields if found rather than returning early:
```python
existing = await session.get(ChildFSRSParamsModel, child_id)
if existing:
    existing.weights = weights
    existing.updated_at = datetime.now(timezone.utc)
else:
    session.add(ChildFSRSParamsModel(
        child_id=child_id,
        weights=weights,
        updated_at=datetime.now(timezone.utc),
    ))
await session.commit()
```

---

### `api/sessions.py` — add `POST /sessions/{id}/end` (route, request-response)

**Analog:** `api/sessions.py` lines 1–31 (existing GET route) + `api/chat.py` lines 1–83 (error handling and Depends pattern)

**Imports and router pattern** — `api/sessions.py` lines 1–7:
```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from services.sessions import get_session_history

router = APIRouter()
```
New route adds `HTTPException` import (follow `api/chat.py` line 1).

**Route with path parameter + Depends(get_db) pattern** — `api/chat.py` lines 37–43:
```python
@router.post("/chat/completions")
async def chat(
    req: ChatRequest,
    x_device_id: str = Header(None),
    x_child_id: str = Header(None),
    session: AsyncSession = Depends(get_db),
):
```
For the session-end route, path param goes first: `session_id: str, db: AsyncSession = Depends(get_db)`.

**404 / 409 HTTPException pattern** — `api/chat.py` lines 51–55:
```python
if not child_id:
    raise HTTPException(status_code=400, detail="No child identity — ...")

child = await get_child_by_id(child_id, session)
if not child:
    raise HTTPException(status_code=404, detail="Child not found")
```
Apply same pattern: 404 if `session_row is None`, 409 if `session_row.ended_at is not None`.

**Response shape pattern** — `api/sessions.py` lines 17–31:
```python
return {
    "child_id": child_id,
    "turns": [
        {
            "id": t.id,
            ...
        }
        for t in turns
    ],
}
```
Return a plain dict (not a Pydantic response model) matching project convention.

---

### `services/tutor.py` — add `mastery_context` param (service, transform)

**Analog:** `services/tutor.py` — `build_system_prompt()` lines 209–238

**Current function signature** — `services/tutor.py` line 209:
```python
async def build_system_prompt(child) -> str:
```

**Extension pattern** — add optional parameter with `None` default (backward-compatible):
```python
async def build_system_prompt(
    child,
    mastery_context: list[dict] | None = None,
) -> str:
```
When `mastery_context` is `None` or empty, prompt is unchanged — existing evals stay green.

**Template string formatting pattern** — `services/tutor.py` lines 188–206 and 226–237:
```python
SYSTEM_PROMPT_TEMPLATE = """
{age_instructions}
...
""".strip()

return SYSTEM_PROMPT_TEMPLATE.format(
    age_instructions=AGE_INSTRUCTIONS[age_key],
    name=child.name,
    ...
)
```
Append mastery context block after the `.format(...)` result — do not embed it in `SYSTEM_PROMPT_TEMPLATE` (would break evals that use the template directly).

**String concatenation pattern for optional block** — `services/tutor.py` lines 223–225:
```python
nd_block = neurodivergence_instructions(nd_flags)
nd_section = f"\n{nd_block}\n" if nd_block else ""
```
Apply same pattern: `mastery_section = _format_mastery_context(mastery_context) if mastery_context else ""` then append to the return value.

---

### `api/chat.py` — call `next_topics` before `build_system_prompt` (route, request-response)

**Analog:** `api/chat.py` lines 56–57 (current call site)

**Current call** — `api/chat.py` line 56:
```python
system_prompt = await build_system_prompt(child)
```

**Extended call pattern** — insert before line 56, after `child` is resolved (line 53):
```python
from services.knowledge_tracing import mastery_context_for_prompt  # add to imports block

# Before build_system_prompt call:
mastery_ctx = await mastery_context_for_prompt(child_id, session, limit=5)
system_prompt = await build_system_prompt(child, mastery_context=mastery_ctx or None)
```
`mastery_ctx or None` collapses an empty list to `None`, preserving the no-op path in `build_system_prompt`.

**Import block pattern** — `api/chat.py` lines 1–13 (add new import alongside existing service imports):
```python
from services.tutor import build_system_prompt, route_model
from services.profiles import get_child_by_device_id, get_child_by_id
from services.sessions import log_turn
# Add:
from services.knowledge_tracing import mastery_context_for_prompt
```

---

### `migrations/versions/{hash}_add_child_fsrs_params.py` (migration, batch)

**Analog:** `migrations/versions/9f229414e92b_initial_schema.py` — full file

**File header pattern** — lines 1–19:
```python
"""add child_fsrs_params

Revision ID: {autogenerated}
Revises: 9f229414e92b
Create Date: {autogenerated}

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '{autogenerated}'
down_revision: Union[str, Sequence[str], None] = '9f229414e92b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
```
`down_revision` must point to the initial schema revision `9f229414e92b`.

**`op.create_table` pattern** — lines 22–37:
```python
def upgrade() -> None:
    op.create_table('child_profiles',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('interests', sa.JSON(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
```
Use `sa.JSON()` (not `sa.String()`) for `weights` column, matching the model definition.

**`op.drop_table` downgrade pattern** — lines 82–92:
```python
def downgrade() -> None:
    op.drop_table('child_fsrs_params')
```

**env.py** — `migrations/env.py` line 10 already has `from db.models import Base` — adding `ChildFSRSParamsModel` to `db/models.py` is sufficient for autogenerate to detect the new table. No changes to `env.py` required.

**Generation command** (do not run manually — include in plan task):
```bash
alembic revision --autogenerate -m "add child_fsrs_params"
```

---

### `tests/services/test_knowledge_tracing.py` (test, unit + integration)

**Analog:** `tests/db/test_crud_mastery.py` (lines 1–77) — same `db_session` fixture, same assert style

**Test file header and imports pattern** — `tests/db/test_crud_mastery.py` lines 1–13:
```python
"""
Tests for MasteryState CRUD functions (DB-05).
...
"""
from sqlalchemy import func, select

from db.crud import create_child, create_or_get_mastery_state, update_mastery_state
from db.models import MasteryStateModel
```
New test file uses `db_session` fixture from `tests/conftest.py` — no local fixture needed for unit tests. Integration tests that need `ChildFSRSParamsModel` may add the model to imports.

**`db_session` fixture usage pattern** — every test function signature:
```python
async def test_create_mastery_state(db_session):
    await create_child(db_session, id="child-c1", name="Grace", age=9)
    ms = await create_or_get_mastery_state("child-c1", "kc-fractions", db_session)
    assert ms.p_mastery == pytest.approx(0.1)
```
All test functions are `async def`. No `@pytest.mark.asyncio` decorator — `asyncio_mode = auto` is set in `pytest.ini`.

**Float comparison pattern** — `tests/db/test_crud_mastery.py` lines 23–26:
```python
assert ms.p_mastery == pytest.approx(0.1)
assert ms.p_learn == pytest.approx(0.2)
```
Use `pytest.approx()` for all float comparisons — BKT math produces floating-point values.

**`pytest` import placement** — `tests/db/test_crud_mastery.py` line 76:
```python
import pytest  # placed at bottom after test functions — match this style
```

**Pure-function unit test pattern** (no `db_session` needed for BKT math):
```python
async def test_bkt_correct_increases_mastery():
    """BKT update with correct=True raises p_mastery."""
    from services.knowledge_tracing import update_bkt
    result = update_bkt(p_mastery=0.1, p_learn=0.2, p_slip=0.1, p_guess=0.2, correct=True)
    assert result > 0.1
    assert result <= 1.0
```

---

### `tests/services/test_tutor.py` (test, unit)

**Analog:** `tests/db/test_crud_mastery.py` — async test style; `services/tutor.py` — the function under test

**No DB fixture needed** — `build_system_prompt()` is called with a mock child object. Use a simple `MagicMock` or a `ChildProfileModel` instance constructed directly without DB (same approach as the evals use `SYSTEM_PROMPT_TEMPLATE` directly).

**Pattern for testing optional parameter backward compatibility:**
```python
async def test_system_prompt_no_mastery_context(mock_child):
    """build_system_prompt(child) without mastery_context is unchanged."""
    from services.tutor import build_system_prompt
    prompt = await build_system_prompt(mock_child)
    assert "Focus topics" not in prompt

async def test_system_prompt_with_mastery_context(mock_child):
    """build_system_prompt(child, mastery_context=[...]) appends focus block."""
    from services.tutor import build_system_prompt
    ctx = [{"name": "Fractions", "bucket": "fragile"}]
    prompt = await build_system_prompt(mock_child, mastery_context=ctx)
    assert "Focus topics this session" in prompt
    assert "fragile" in prompt
```

---

### `tests/api/test_session_end.py` (test, integration)

**Analog:** `tests/api/test_chat_db_wiring.py` — full file (lines 1–183)

**Engine + session fixture pattern** — `tests/api/test_chat_db_wiring.py` lines 31–46:
```python
@pytest_asyncio.fixture
async def mem_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture
async def mem_session(mem_engine):
    factory = async_sessionmaker(mem_engine, expire_on_commit=False)
    async with factory() as session:
        yield session
```

**dependency_overrides pattern** — `tests/api/test_chat_db_wiring.py` lines 69–90:
```python
factory = async_sessionmaker(mem_engine, expire_on_commit=False)

async def override_get_db():
    async with factory() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
    yield client

app.dependency_overrides.pop(get_db, None)
```

**POST route assertion pattern** — `tests/api/test_chat_db_wiring.py` lines 110–135:
```python
response = await test_client.post(
    "/v1/sessions/{session_id}/end",
    headers={"X-Child-ID": "child-kida"},
)
assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

# Verify DB state:
factory = async_sessionmaker(mem_engine, expire_on_commit=False)
async with factory() as session:
    result = await session.execute(
        select(SessionModel).where(SessionModel.id == session_id)
    )
    row = result.scalar_one_or_none()
assert row.ended_at is not None
```

**sys.path fixture** — `tests/api/conftest.py` lines 1–6 (already handles path — no changes needed in this file for new test file):
```python
import sys
from pathlib import Path
root = str(Path(__file__).parent.parent.parent)
if root not in sys.path:
    sys.path.insert(0, root)
```

---

### `requirements.txt` — add `fsrs` (config)

**Analog:** `requirements.txt` lines 1–20 (version pinning style)

**Version pin pattern** — existing lines use `>=` lower-bound pins:
```
sqlalchemy>=2.0.0
alembic>=1.13.0
```

**Line to add:**
```
fsrs[optimizer]>=6.3.1
```
Place after `alembic>=1.13.0` (logically grouped with DB/data dependencies). The `[optimizer]` extra is required for `fit_fsrs_params()` (D-05 per-child fitting).

---

## Shared Patterns

### AsyncSession injection
**Source:** `api/sessions.py` line 13, `api/chat.py` line 43, `db/crud.py` all functions
**Apply to:** All new route functions (`api/sessions.py` end route), all new service functions (`services/knowledge_tracing.py`)

Route layer uses `Depends(get_db)`:
```python
session: AsyncSession = Depends(get_db)
```
Service layer receives explicit parameter (never calls `Depends` directly):
```python
async def my_service_fn(child_id: str, session: AsyncSession) -> ...:
```

### UTC-aware datetime
**Source:** `db/models.py` lines 47, 65, 91; `db/crud.py` line 210
**Apply to:** All datetime creation in `services/knowledge_tracing.py`, `db/models.py` new model, `db/crud.py` new functions
```python
from datetime import datetime, timezone
# Always:
datetime.now(timezone.utc)
# Never:
datetime.utcnow()  # returns naive datetime — breaks FSRS comparison
```

### HTTP error handling
**Source:** `api/chat.py` lines 50–55
**Apply to:** `api/sessions.py` new POST /sessions/{id}/end route
```python
from fastapi import HTTPException

if model is None:
    raise HTTPException(status_code=404, detail="Session not found")
if model.ended_at is not None:
    raise HTTPException(status_code=409, detail="Session already ended")
```

### select() parameterisation (never string-interpolated)
**Source:** `db/crud.py` lines 8–10 (security note), all CRUD select calls
**Apply to:** All new `select()` calls in `services/knowledge_tracing.py` and new `db/crud.py` functions
```python
# Correct — parameterised:
select(InteractionEventModel).where(InteractionEventModel.session_id == session_id)
# Never:
f"SELECT * FROM interaction_events WHERE session_id = '{session_id}'"
```

### Test async conventions
**Source:** `tests/conftest.py` lines 1–25, `tests/db/test_crud_mastery.py` lines 16–26
**Apply to:** All new test files
- All test functions are `async def`
- No `@pytest.mark.asyncio` decorator needed — `asyncio_mode = auto` in `pytest.ini`
- Use `pytest_asyncio.fixture` (not `pytest.fixture`) for async fixtures
- Float assertions use `pytest.approx()`

---

## No Analog Found

All files have close analogs in the existing codebase. No files require falling back to RESEARCH.md patterns exclusively, though `services/knowledge_tracing.py` introduces logic (BKT math, FSRS API calls) that is novel — the RESEARCH.md code examples should be used for those algorithm bodies, with the structural patterns (async, session injection, select, commit) copied from codebase analogs.

---

## Metadata

**Analog search scope:** `api/`, `db/`, `services/`, `migrations/`, `tests/`
**Files scanned:** 14 source files + 8 test files
**Pattern extraction date:** 2026-07-16
