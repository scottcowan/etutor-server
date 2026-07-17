# Phase 3: Session Intelligence - Pattern Map

**Mapped:** 2026-07-17
**Files analyzed:** 8 new/modified files
**Analogs found:** 7 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `services/session_intelligence.py` | service | request-response + CRUD | `services/knowledge_tracing.py` | role-match |
| `services/tutor.py` (extend) | service | request-response | self (extend existing) | exact |
| `services/knowledge_tracing.py` (extend) | service | CRUD | self (extend existing) | exact |
| `db/crud.py` (extend) | utility | CRUD | self (extend existing) | exact |
| `api/chat.py` (extend) | controller | request-response | self (extend existing) | exact |
| `api/sessions.py` (extend) | controller | request-response | self (extend existing) | exact |
| `tests/services/test_session_intelligence.py` | test | — | `tests/services/test_knowledge_tracing.py` | exact |
| `tests/db/test_crud_session_intelligence.py` | test | — | `tests/db/test_crud_events.py` | exact |
| `tests/api/test_session_turns.py` | test | — | `tests/api/test_session_end.py` | exact |

---

## Pattern Assignments

### `services/session_intelligence.py` (new service, request-response + CRUD)

**Analog:** `services/knowledge_tracing.py`

**Module docstring + imports pattern** (`services/knowledge_tracing.py` lines 1–32):
```python
"""
Session intelligence service — history context, prereq tree, interest extraction (Phase 3).

HIST-01: build_24hr_history_context() — flat topic list for system prompt
HIST-02: build_prereq_tree_context() — one-level prereq gap tree for system prompt
CURR-02: get_session_prereq_state() / increment_prereq_turn() — rubber-band escalation counter
CURR-03: extract_and_update_interests() — tag-scan interest extraction at session end/start
"""
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import InteractionEventModel, MasteryStateModel
from db.crud import update_interests
from services.curriculum import CURRICULUM, _by_id
from services.knowledge_tracing import next_topics, _mastery_bucket
```

**Private module-level state pattern** (no analog — standard Python, see RESEARCH.md Pattern 3):
```python
# Module-level session-level turn counter for rubber-band escalation (D-07).
# Single-worker assumption — see RESEARCH.md Pitfall 5 for multi-worker limitation.
_prereq_turn_counter: dict[tuple[str, str], int] = defaultdict(int)

def get_prereq_turn(child_id: str, kc_id: str) -> int:
    return _prereq_turn_counter[(child_id, kc_id)]

def increment_prereq_turn(child_id: str, kc_id: str) -> int:
    _prereq_turn_counter[(child_id, kc_id)] += 1
    return _prereq_turn_counter[(child_id, kc_id)]

def reset_prereq_turn(child_id: str, kc_id: str) -> None:
    _prereq_turn_counter.pop((child_id, kc_id), None)
```

**Async service function signature pattern** (`services/knowledge_tracing.py` lines 433–437):
```python
async def mastery_context_for_prompt(
    child_id: str,
    db: AsyncSession,
    limit: int = 5,
) -> list[dict]:
```
All new async service functions follow this `(child_id: str, db: AsyncSession, limit: int = N) -> list[...]` signature. Use `Optional[list]` not `list | None` (Python 3.9 compat per project convention).

**SQLAlchemy select + where + order_by pattern** (`db/crud.py` lines 161–178):
```python
result = await session.execute(
    select(InteractionEventModel)
    .where(InteractionEventModel.child_id == child_id)
    .order_by(InteractionEventModel.timestamp.desc())
    .limit(limit)
)
rows = list(result.scalars().all())
```
The `get_24hr_history()` CRUD function adds `.where(InteractionEventModel.timestamp >= since)` before `.order_by()`. Always use `datetime.now(timezone.utc) - timedelta(hours=24)` — never `datetime.utcnow()` (naive datetime fails against UTC-aware column).

**Batch mastery load pattern** (`services/knowledge_tracing.py` lines 455–460):
```python
stmt = (
    select(MasteryStateModel)
    .where(MasteryStateModel.child_id == child_id)
    .where(MasteryStateModel.kc_id.in_(topic_ids))
)
result = await db.execute(stmt)
mastery_rows = list(result.scalars().all())
mastery_by_kc = {r.kc_id: r for r in mastery_rows}
```
`build_prereq_tree_context()` uses the same pattern: gather all prereq IDs first, then batch-load their mastery rows in one query.

**_mastery_bucket() usage** (`services/knowledge_tracing.py` lines 462–469):
```python
for topic in topics:
    row = mastery_by_kc.get(topic.id)
    p = row.p_mastery if row is not None else None
    bucket = _mastery_bucket(p)
    if bucket == "solid":
        continue
```
For `build_prereq_tree_context()`, filter condition is `bucket in ("fragile", "not_started")` — skip `in_progress` and `solid` per D-13.

**Pattern 6 — build_prereq_tree_context() output dict format** (D-06, D-07 counter key contract):

The internal accumulator dict is keyed by `prereq_id` (the KC ID string), NOT by `prereq_name`, to avoid collision when two prerequisite topics share the same name string:
```python
prereq_to_unlocks: dict[str, list[str]] = {}  # keyed by prereq KC id
for topic in candidates:
    for prereq_id in topic.prerequisites:
        row = mastery_by_kc.get(prereq_id)
        p = row.p_mastery if row is not None else None
        bucket = _mastery_bucket(p)
        if bucket in ("in_progress", "solid"):  # D-13: skip mastered prereqs
            continue
        prereq_to_unlocks.setdefault(prereq_id, []).append(topic.name)

output = [
    {
        "prereq_name": _by_id[pid].name,   # human-readable name for prompt
        "prereq_kc_id": pid,               # KC ID for counter lookup — CRITICAL for D-07/D-06
        "unlocks": unlocks[:3],             # D-12: cap at 3
    }
    for pid, unlocks in prereq_to_unlocks.items()
    if pid in _by_id
]
```

The `prereq_kc_id` field is the counter key used by `increment_prereq_turn(child_id, entry["prereq_kc_id"])` in `api/chat.py` and `reset_prereq_turn(child_id, kc_id)` in the D-06 reset path. Without this field, counter lookups in `_format_escalation_signal` and D-06 reset comprehensions always miss — the escalation counter never advances and reset never fires.

**`update_interests()` call pattern** (`db/crud.py` lines 87–97):
```python
async def update_interests(
    child_id: str, new_interests: list, session: AsyncSession
) -> None:
    child = await get_child_by_id(child_id, session)
    if child is None:
        return
    existing = set(child.interests or [])
    merged = list(existing | set(new_interests))
    child.interests = merged
    await session.commit()
```
Call as `await update_interests(child_id, extracted_topics, db)`. It is idempotent — calling it twice for the same session is safe (set union, no duplicates).

---

### `services/tutor.py` — extend `build_system_prompt()` (lines 242–274)

**Analog:** self (current implementation)

**Current signature** (`services/tutor.py` lines 242):
```python
async def build_system_prompt(child, mastery_context: Optional[list] = None) -> str:
```

**Extended signature** (add three new `Optional[list/dict]` params with `None` defaults):
```python
async def build_system_prompt(
    child,
    mastery_context: Optional[list] = None,
    history_context: Optional[list] = None,
    prereq_tree: Optional[list] = None,
    session_prereq_state: Optional[dict] = None,
) -> str:
```
All three new params default to `None` — existing callers (`tests/services/test_tutor.py` tests) are unaffected.

**Template + formatter pattern** (`services/tutor.py` lines 190–218):
```python
MASTERY_CONTEXT_TEMPLATE = "\nFocus topics this session:\n{topic_lines}\n"

def _format_mastery_context(mastery_context: list) -> str:
    lines = []
    for item in mastery_context:
        name = item["name"]
        bucket = item["bucket"]
        if bucket == "fragile":
            lines.append(f"- {name} (fragile — needs reinforcement)")
        ...
    if not lines:
        return ""
    return MASTERY_CONTEXT_TEMPLATE.format(topic_lines="\n".join(lines))
```
Follow this exact pattern for `HISTORY_CONTEXT_TEMPLATE` + `_format_history_context()` and `PREREQ_TREE_TEMPLATE` + `_format_prereq_tree()`.

**String concatenation at end of `build_system_prompt()`** (`services/tutor.py` lines 273–274):
```python
mastery_section = _format_mastery_context(mastery_context) if mastery_context else ""
return base_prompt + mastery_section
```
Extend to:
```python
mastery_section = _format_mastery_context(mastery_context) if mastery_context else ""
history_section = _format_history_context(history_context) if history_context else ""
prereq_section = _format_prereq_tree(prereq_tree) if prereq_tree else ""
return base_prompt + mastery_section + history_section + prereq_section
```
`session_prereq_state` is not formatted as a separate section — it controls which escalation signal is embedded in the prereq section rendering.

---

### `services/knowledge_tracing.py` — extend `next_topics()` (lines 347–426)

**Analog:** self (current implementation)

**Mastered IDs list** (`services/knowledge_tracing.py` line 378):
```python
mastered_ids = [r.kc_id for r in mastery_rows if r.p_mastery >= 0.95]
```
The supersedes unlock check (D-14) runs immediately after this line, before `curriculum_next_topics()` is called. Build the `_superseded_by` reverse-index at module level (import time, one-off cost).

**Module-level reverse index** (add after imports, before any function definition):
```python
# Reverse supersedes index: {superseded_topic_id: [superseding_topic_id, ...]}
# Built once at import time — O(N) over CURRICULUM (870 topics).
_superseded_by: dict[str, list[str]] = {}
for _t in CURRICULUM:
    if _t.supersedes:
        _superseded_by.setdefault(_t.supersedes, []).append(_t.id)
```

**Candidates list extension point** (insert after line 381, after `curriculum_next_topics()` call):
```python
candidates = curriculum_next_topics(child.age, mastered_ids, child.interests)

# D-14: add supersedes unlocks for fully-mastered (solid) KCs
for kc_id in mastered_ids:
    for superseding_id in _superseded_by.get(kc_id, []):
        superseding_topic = _by_id.get(superseding_id)
        if superseding_topic and superseding_id not in mastered_ids:
            if superseding_topic not in candidates:
                candidates.append(superseding_topic)
```
`_by_id` is already imported from `services.curriculum`. `mastered_ids` uses `p_mastery >= 0.95` as the solid threshold (RESEARCH.md Pitfall 4 / Assumption A1).

---

### `db/crud.py` — add `get_24hr_history()` and `get_turns_by_session_id()`

**Analog:** `get_session_history()` (`db/crud.py` lines 161–178)

**Module-level import already present** — `from datetime import datetime, timezone` at line 19. Add `timedelta` to that import.

**`get_24hr_history()` — timestamp filter variant** (add after `get_session_history()`):
```python
async def get_24hr_history(
    child_id: str,
    session: AsyncSession,
    limit: int = 50,
) -> list[InteractionEventModel]:
    """Return interaction events for child_id in the past 24 hours, DESC order.

    HIST-01 (D-03): Uses UTC-aware datetime comparison — never datetime.utcnow().
    Security note: child_id parameterised via SQLAlchemy ORM.
    """
    since = datetime.now(timezone.utc) - timedelta(hours=24)
    result = await session.execute(
        select(InteractionEventModel)
        .where(InteractionEventModel.child_id == child_id)
        .where(InteractionEventModel.timestamp >= since)
        .order_by(InteractionEventModel.timestamp.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
```

**`get_turns_by_session_id()` — session-scoped variant** (add after `get_24hr_history()`):
```python
async def get_turns_by_session_id(
    session_id: str,
    db: AsyncSession,
) -> list[InteractionEventModel]:
    """Return all interaction events for session_id, ordered ASC by timestamp.

    HIST-03: Scoped to session_id (not child_id). Same IDOR exposure as
    get_session_history() — fix both together in auth phase (CR-02).
    """
    result = await db.execute(
        select(InteractionEventModel)
        .where(InteractionEventModel.session_id == session_id)
        .order_by(InteractionEventModel.timestamp.asc())
    )
    return list(result.scalars().all())
```

Note: parameter is named `db` (not `session`) to match the `end_session()` convention in `api/sessions.py` — avoid confusion with `SessionModel`.

---

### `api/chat.py` — extend `chat()` endpoint (lines 38–85)

**Analog:** self (current implementation)

**Current import block** (`api/chat.py` lines 1–15):
```python
from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, field_validator
from typing import Optional
import json

from sqlalchemy.ext.asyncio import AsyncSession

from db.crud import create_session
from db.session import get_db
from services.tutor import build_system_prompt, route_model
from services.profiles import get_child_by_device_id, get_child_by_id
from services.sessions import log_turn
from services.knowledge_tracing import mastery_context_for_prompt
```
Add three imports from the new service:
```python
from services.session_intelligence import (
    build_24hr_history_context,
    build_prereq_tree_context,
    get_session_prereq_state,
    extract_and_update_interests,
)
from db.crud import get_most_recent_ended_session  # new CRUD for D-08 catch-up
```

**Current mastery_ctx + build_system_prompt wiring** (`api/chat.py` lines 57–58):
```python
mastery_ctx = await mastery_context_for_prompt(child_id, session, limit=5)
system_prompt = await build_system_prompt(child, mastery_context=mastery_ctx or None)
```
Extend to (add BEFORE `build_system_prompt`, AFTER child is resolved):
```python
mastery_ctx = await mastery_context_for_prompt(child_id, session, limit=5)
history_ctx = await build_24hr_history_context(child_id, session)
prereq_tree = await build_prereq_tree_context(child_id, session, limit=5)
prereq_state = get_session_prereq_state(child_id)

# D-08 catch-up: extract interests from previous session that missed /end call
prev_session = await get_most_recent_ended_session(child_id, session)
if prev_session and prev_session.id:
    await extract_and_update_interests(prev_session.id, child_id, session)

system_prompt = await build_system_prompt(
    child,
    mastery_context=mastery_ctx or None,
    history_context=history_ctx or None,
    prereq_tree=prereq_tree or None,
    session_prereq_state=prereq_state or None,
)
```
All DB calls go before `build_system_prompt()` — the prompt builder receives pre-fetched data and never calls DB itself (RESEARCH.md Anti-Pattern 1).

---

### `api/sessions.py` — extend `end_session()` and add HIST-03 route

**Analog:** self (current `end_session()` and `get_sessions()`)

**Current end of `end_session()`** (`api/sessions.py` lines 64–71):
```python
    bkt_updates = await update_bkt_for_session(session_id, db)
    await fit_fsrs_params(session_row.child_id, db)

    return {
        "session_id": session_id,
        "ended_at": session_row.ended_at.isoformat(),
        "kcs_updated": len(bkt_updates),
    }
```
Insert interest extraction AFTER `fit_fsrs_params`, BEFORE the `return`:
```python
    bkt_updates = await update_bkt_for_session(session_id, db)
    await fit_fsrs_params(session_row.child_id, db)
    await extract_and_update_interests(session_id, session_row.child_id, db)  # D-08

    return {
        "session_id": session_id,
        "ended_at": session_row.ended_at.isoformat(),
        "kcs_updated": len(bkt_updates),
    }
```
`db` is already in scope as `AsyncSession = Depends(get_db)` — no new dependency injection needed. This is NOT the streaming path (CR-01 non-regression confirmed).

**HIST-03 new endpoint** — follow `get_sessions()` pattern (`api/sessions.py` lines 14–35):
```python
@router.get("/sessions/{child_id}")
async def get_sessions(
    child_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
):
    turns = await get_session_history(child_id, session, limit)
    return {
        "child_id": child_id,
        "turns": [
            {
                "id": t.id,
                "child_id": t.child_id,
                "session_id": t.session_id,
                "question": t.question,
                "answer": t.answer,
                "topic": t.topic,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            }
            for t in turns
        ],
    }
```
New HIST-03 endpoint matches this shape exactly (no auth, same IDOR exposure as CR-02 — fix both together):
```python
@router.get("/sessions/{session_id}/turns")
async def get_session_turns(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    turns = await get_turns_by_session_id(session_id, db)
    return {
        "session_id": session_id,
        "turns": [
            {
                "id": t.id,
                "child_id": t.child_id,
                "question": t.question,
                "answer": t.answer,
                "topic": t.topic,
                "timestamp": t.timestamp.isoformat() if t.timestamp else None,
            }
            for t in turns
        ],
    }
```
Path `/sessions/{session_id}/turns` is non-overlapping with `/sessions/{child_id}` — no route conflict.

---

### `tests/services/test_session_intelligence.py` (new test file)

**Analog:** `tests/services/test_knowledge_tracing.py`

**sys.path pattern** — `tests/services/conftest.py` (lines 1–7) handles this automatically; no `__init__.py` needed in the test directory.

**Pure function test pattern** (`tests/services/test_knowledge_tracing.py` lines 37–45):
```python
def test_bkt_correct_increases_mastery():
    """correct=True observation raises p_mastery from baseline."""
    result = update_bkt(
        p_mastery=0.1, p_learn=0.2, p_slip=0.1, p_guess=0.2, correct=True,
    )
    assert result > 0.1
    assert result <= 1.0
```
Use `def` (not `async def`) for pure function tests (escalation cadence functions).

**Async DB integration test pattern** (`tests/services/test_knowledge_tracing.py` lines 111–139):
```python
async def test_update_bkt_for_session_raises_mastery(db_session):
    """Two correct events for a KC in one session raise p_mastery above the default 0.1."""
    child = await create_child(db_session, id="child-bkt-01", name="Alice", age=9)
    session_row = await create_session(child.id, db_session)
    # ... log_turn calls ...
    result = await some_service_function(session_row.id, db_session)
    assert ...
```
No `@pytest.mark.asyncio` needed — `asyncio_mode = auto` in `pytest.ini`.

**`_make_child()` namespace helper** (`tests/services/test_tutor.py` lines 21–33):
```python
def _make_child(**kwargs):
    """Create a minimal child-like namespace for testing build_system_prompt()."""
    defaults = {
        "name": "TestChild", "age": 9, "interests": ["space"],
        "reading_level": "grade-4", "current_topic": "planets",
        "current_books": [], "neurodivergence": [],
    }
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)
```
Re-use this helper in `test_session_intelligence.py` for `build_system_prompt` extension tests.

---

### `tests/db/test_crud_session_intelligence.py` (new test file)

**Analog:** `tests/db/test_crud_events.py`

**DB fixture** — `db_session` fixture is auto-available from `tests/conftest.py` (no `__init__.py` in `tests/db/` — confirmed existing pattern from `tests/db/__init__.py` present). Import from `db.crud` and `db.models` directly.

**CRUD test pattern** (`tests/db/test_crud_events.py` lines 21–31):
```python
async def test_log_turn_creates_row(db_session):
    """log_turn returns InteractionEventModel with correct fields."""
    await create_child(db_session, id="child-b1", name="Bob", age=8)
    event = await log_turn("child-b1", "What is gravity?", "A force.", db_session)
    assert event.id is not None
    assert event.child_id == "child-b1"
```
Follow this shape for `test_get_24hr_history` (assert events older than 24h are excluded) and `test_get_turns_by_session_id` (assert only events from the given session_id are returned).

---

### `tests/api/test_session_turns.py` (new test file)

**Analog:** `tests/api/test_session_end.py`

**Full integration test fixture stack** (`tests/api/test_session_end.py` lines 29–83):
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

@pytest_asyncio.fixture
async def test_client(mem_engine, test_data):
    factory = async_sessionmaker(mem_engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.pop(get_db, None)
```
Copy this fixture stack verbatim. The `test_data` fixture should create a child, a session, and log 2–3 turns with `session_id` set so the HIST-03 endpoint has data to return.

**HTTP assertion pattern** (`tests/api/test_session_end.py` lines 90–98):
```python
async def test_session_end_200(test_client, test_data):
    child_id, session_id = test_data
    response = await test_client.post(f"/v1/sessions/{session_id}/end")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    body = response.json()
    assert "session_id" in body
```
Follow this for the HIST-03 GET test: assert `response.status_code == 200`, assert `"session_id"` and `"turns"` in body, assert `len(body["turns"]) == expected_count`.

---

## Shared Patterns

### Async SQLAlchemy Session Dependency Injection
**Source:** `api/sessions.py` line 41, `api/chat.py` line 43
**Apply to:** All new endpoint functions and new CRUD functions
```python
db: AsyncSession = Depends(get_db)
```
Note: `end_session()` names the parameter `db` to avoid shadowing `SessionModel` rows. `get_sessions()` uses `session`. New code should prefer `db` for the `AsyncSession` parameter to match the convention established in Phase 2 `end_session()` and `db/crud.py`.

### UTC-Aware Datetime
**Source:** `db/crud.py` line 218, `services/knowledge_tracing.py` line 385
**Apply to:** `get_24hr_history()` cutoff, any new `datetime.now()` calls
```python
from datetime import datetime, timezone, timedelta
datetime.now(timezone.utc)  # always — never datetime.utcnow()
```

### `Optional[list]` Parameter Style
**Source:** `services/tutor.py` line 242, `services/knowledge_tracing.py` line 325
**Apply to:** All new function parameters that accept list/dict or None
```python
from typing import Optional
def foo(param: Optional[list] = None) -> str:
```
Not `list | None` — Python 3.9 compatibility is a project requirement (confirmed in Phase 2 code review).

### SQLAlchemy Parameterised SELECT Pattern
**Source:** `db/crud.py` lines 65–68, 171–177
**Apply to:** `get_24hr_history()`, `get_turns_by_session_id()`, `build_prereq_tree_context()`
```python
result = await session.execute(
    select(Model)
    .where(Model.column == value)
    .order_by(Model.timestamp.desc())
    .limit(limit)
)
return list(result.scalars().all())
```
Never string-interpolate values into WHERE clauses — always use ORM column comparisons.

### No-op on Empty Result
**Source:** `services/knowledge_tracing.py` lines 369–371, `db/crud.py` lines 91–93
**Apply to:** `build_24hr_history_context()`, `build_prereq_tree_context()`, `extract_and_update_interests()`
```python
if not some_list:
    return []   # or return ""
```
All new service functions must return their empty-case type cleanly without raising.

### Security Note Comment Pattern
**Source:** `db/crud.py` lines 9–17, `services/knowledge_tracing.py` lines 115–118
**Apply to:** All new CRUD functions and the new HIST-03 endpoint
```python
# Security note (T-3-XX): <column> parameterised via SQLAlchemy ORM — never string-interpolated.
# IDOR note (CR-02): <endpoint> has same IDOR exposure as GET /sessions/{child_id} — fix together.
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `services/session_intelligence.py` — `_prereq_turn_counter` module-level dict | in-memory state | event-driven | No existing in-memory session state in the codebase; use standard Python `defaultdict(int)` pattern from RESEARCH.md Pattern 3 |
| `db/crud.py` — `get_most_recent_ended_session()` (D-08 catch-up) | utility | CRUD | No analog for "most recent session by child_id with ended_at IS NOT NULL"; follow `get_session()` pattern with `order_by(SessionModel.ended_at.desc()).limit(1)` |

---

## Metadata

**Analog search scope:** `services/`, `db/`, `api/`, `tests/services/`, `tests/db/`, `tests/api/`
**Files read:** 16 source files + 2 planning documents
**Pattern extraction date:** 2026-07-17
