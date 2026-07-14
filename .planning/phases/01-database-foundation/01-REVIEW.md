---
phase: 01-database-foundation
reviewed: 2026-07-15T00:00:00Z
depth: standard
files_reviewed: 25
files_reviewed_list:
  - alembic.ini
  - api/chat.py
  - api/child.py
  - api/dashboard.py
  - api/main.py
  - api/parent.py
  - api/sessions.py
  - api/stt.py
  - api/sync.py
  - db/__init__.py
  - db/crud.py
  - db/models.py
  - db/seeds.py
  - db/session.py
  - migrations/env.py
  - migrations/versions/9f229414e92b_initial_schema.py
  - pytest.ini
  - services/profiles.py
  - services/recommender.py
  - services/sessions.py
  - tests/api/test_chat_db_wiring.py
  - tests/conftest.py
  - tests/db/test_crud_events.py
  - tests/db/test_crud_mastery.py
  - tests/db/test_crud_profiles.py
  - tests/db/test_crud_sessions.py
  - tests/db/test_seeds.py
findings:
  critical: 5
  warning: 6
  info: 3
  total: 14
status: issues_found
---

# Phase 01: Code Review Report

**Reviewed:** 2026-07-15T00:00:00Z
**Depth:** standard
**Files Reviewed:** 25
**Status:** issues_found

## Summary

The database foundation is structurally sound: models are clean, CRUD functions use parameterised ORM queries, and the test suite covers the happy paths well. However, five blocker-level defects exist — two that can crash the server at runtime on valid inputs, one COPPA-relevant privacy gap, one missing authentication guard, and one data-integrity hole from a missing uniqueness constraint. Six warnings cover code correctness and robustness issues that will surface under normal production use.

---

## Critical Issues

### CR-01: `chat` endpoint crashes on empty `messages` list

**File:** `api/chat.py:66`
**Issue:** `req.messages[-1].content` is accessed unconditionally. If a client sends `"messages": []`, `[-1]` on an empty list raises `IndexError`, returning a 500 Internal Server Error instead of a 400 validation error. FastAPI does not validate `list[Message]` as non-empty by default.

**Fix:**
```python
class ChatRequest(BaseModel):
    model: str = "etutor"
    messages: list[Message]
    stream: bool = False
    child_id: Optional[str] = None

    @field_validator("messages")
    @classmethod
    def messages_not_empty(cls, v):
        if not v:
            raise ValueError("messages must not be empty")
        return v
```
Or guard inline before use:
```python
if not req.messages:
    raise HTTPException(status_code=400, detail="messages must not be empty")
```

---

### CR-02: `chat` endpoint does not check if `child_id` resolves to an existing child

**File:** `api/chat.py:46-47`
**Issue:** When `child_id` is supplied via header or body, `get_child_by_id` is called but its return value is never checked for `None`. If the child does not exist, `child` is `None` and `build_system_prompt(child)` and `route_model(child)` both receive `None`, likely crashing with an `AttributeError`. This also means an attacker can enumerate valid child IDs by probing response differences.

**Fix:**
```python
child = await get_child_by_id(child_id, session)
if not child:
    raise HTTPException(status_code=404, detail="Child not found")
```

---

### CR-03: `device_id` is not unique — one device can be mapped to multiple children

**File:** `db/models.py:30` and `migrations/versions/9f229414e92b_initial_schema.py:37`
**Issue:** `device_id` is indexed with `unique=False`. Because `get_child_by_device_id` uses `scalar_one_or_none()`, inserting two children with the same `device_id` will raise `MultipleResultsFound` at runtime, crashing the sync and chat endpoints for that device. The invariant "one device → one child" is enforced nowhere.

**Fix:**
```python
# db/models.py
device_id: Mapped[Optional[str]] = mapped_column(String, nullable=True, index=True, unique=True)
```
Add a new Alembic migration to enforce this at the DB level:
```python
op.create_index('ix_child_profiles_device_id', 'child_profiles', ['device_id'], unique=True)
```

---

### CR-04: `build_recommendation_message` crashes with `IndexError` when `child.interests` is empty

**File:** `services/recommender.py:45`
**Issue:** `child.interests[0]` is accessed without a length check. If a child has no interests (a valid state — `neurodivergence=[]` and `interests=[]` are both seeded as acceptable defaults), calling `build_recommendation_message` raises `IndexError`. This crashes the `/v1/devices/{device_id}/sync` endpoint.

Note: the `get_recommendations` guard (`if not books: return ""`) prevents the crash only when Calibre-Web is unavailable. If Calibre-Web is reachable and returns books matched by some other path, the guard is bypassed.

**Fix:**
```python
async def build_recommendation_message(child: ChildProfileModel) -> str:
    books = await get_recommendations(child)
    if not books or not child.interests:
        return ""
    titles = ", ".join(f'"{b["title"]}"' for b in books[:3])
    return f"Based on your interest in {child.interests[0]}, you might enjoy: {titles}."
```

---

### CR-05: CORS `allow_origins=["*"]` with no authentication — unauthenticated cross-origin API access

**File:** `api/main.py:38-43`
**Issue:** CORS is set to allow all origins. There is no authentication on any endpoint (no API keys, no tokens, no session cookies). Any web page can make cross-origin requests to all endpoints including `/v1/chat/completions`, `/v1/sessions/{child_id}`, and `/v1/devices/{device_id}/sync`, reading private child interaction history and triggering LLM completions billed to the operator. This is a COPPA-relevant exposure: children's interaction data is accessible to any origin.

**Fix:** For a device-local server, restrict origins to device-local addresses. For a networked deployment, add an API key check and restrict origins:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],  # tighten per deployment
    allow_methods=["POST", "GET"],
    allow_headers=["X-Child-ID", "X-Device-ID", "Content-Type"],
)
```
Additionally, add an API key dependency to device-facing routes.

---

## Warnings

### WR-01: `get_session_history` fetches all rows then slices in Python — unbounded memory load

**File:** `db/crud.py:163-170`
**Issue:** The comment explicitly notes "No .limit() in SQL — fetch all, slice in Python for most-recent-N semantics." This loads every interaction event for a child from the database into memory to return the last N. A child with years of history (thousands of rows, potentially MBs of question/answer text) will cause significant memory pressure and slow response times. The stated reason — "SQL complexity" — does not hold: SQL `ORDER BY timestamp DESC LIMIT N` is standard and equivalent.

**Fix:**
```python
result = await session.execute(
    select(InteractionEventModel)
    .where(InteractionEventModel.child_id == child_id)
    .order_by(InteractionEventModel.timestamp.desc())
    .limit(limit)
)
rows = list(result.scalars().all())
return list(reversed(rows))  # restore ASC order for callers
```

---

### WR-02: `_transcribe_local` is blocking CPU-bound code inside an `async` function

**File:** `api/stt.py:36-41`
**Issue:** `WhisperModel` is instantiated and `model.transcribe()` is called inside an `async def` function with no `await` or executor delegation. `faster-whisper` transcription is synchronous and CPU-bound, blocking the entire asyncio event loop for the duration of inference (seconds). Under load this stalls all other requests.

**Fix:**
```python
import asyncio
from functools import partial

async def _transcribe_local(path: str) -> str:
    from faster_whisper import WhisperModel
    settings = get_settings()

    def _sync_transcribe():
        model = WhisperModel(settings.whisper_model, device="cpu", compute_type="int8")
        segments, _ = model.transcribe(path, beam_size=1)
        return " ".join(s.text.strip() for s in segments)

    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _sync_transcribe)
```

---

### WR-03: `WhisperModel` is re-instantiated on every request — model load cost paid each time

**File:** `api/stt.py:39`
**Issue:** A new `WhisperModel` is constructed inside `_transcribe_local` on every call. Loading a Whisper model involves reading hundreds of MB from disk and initialising quantised weights. This adds multiple seconds of cold-start latency to every transcription request, far exceeding the <2s end-to-end latency target.

**Fix:** Instantiate the model once at application startup and cache it as a module-level or `lifespan` singleton:
```python
_whisper_model: WhisperModel | None = None

def get_whisper_model() -> WhisperModel:
    global _whisper_model
    if _whisper_model is None:
        settings = get_settings()
        _whisper_model = WhisperModel(settings.whisper_model, device="cpu", compute_type="int8")
    return _whisper_model
```

---

### WR-04: Streaming path in `chat` does not log the turn to the database

**File:** `api/chat.py:54-61`
**Issue:** When `req.stream=True`, the SSE generator streams the response but never calls `create_session` or `log_turn`. The non-streaming path (lines 65-66) writes both records. Streaming sessions are silently unlogged — mastery state, session history, and parent dashboard will be blind to all streamed interactions. This is a data-loss defect, not a deferred feature.

**Fix:** Accumulate chunks inside the generator and log after the stream completes:
```python
async def generate():
    db_session_row = await create_session(child_id, session)
    full_content = []
    response = await litellm.acompletion(model=model, messages=messages, stream=True)
    async for chunk in response:
        delta = chunk.choices[0].delta.content or ""
        full_content.append(delta)
        yield f"data: {json.dumps({'choices': [{'delta': {'content': delta}}]})}\n\n"
    yield "data: [DONE]\n\n"
    await log_turn(child_id, req.messages[-1].content, "".join(full_content),
                   session, session_id=db_session_row.id)
```

---

### WR-05: `api/sessions.py` — `limit` parameter has no upper bound, allowing large data dumps

**File:** `api/sessions.py:13`
**Issue:** `limit: int = 50` accepts any integer. A caller sending `limit=100000` triggers a full table scan of interaction events for that child (compounded by WR-01's in-Python slicing), consuming significant memory and CPU. There is no validation or cap.

**Fix:**
```python
from fastapi import Query
...
limit: int = Query(default=50, ge=1, le=500),
```

---

### WR-06: `datetime.utcnow()` is deprecated in Python 3.12+ and produces naive datetimes

**File:** `db/models.py:47`, `db/models.py:65`, `db/models.py:91`, `db/crud.py:210`
**Issue:** `datetime.utcnow()` is deprecated since Python 3.12 (will be removed in a future version) and produces a timezone-naive datetime. SQLite stores it as a string without timezone info, making timestamp comparisons and ordering ambiguous when the server runs in a non-UTC timezone. The deprecation warning will appear in logs on Python 3.12+.

**Fix:**
```python
from datetime import datetime, timezone

# Replace all occurrences of datetime.utcnow with:
datetime.now(timezone.utc)
```
For ORM column defaults:
```python
started_at: Mapped[datetime] = mapped_column(
    DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
)
```

---

## Info

### IN-01: `import pytest` at bottom of file in `test_crud_mastery.py`

**File:** `tests/db/test_crud_mastery.py:76`
**Issue:** `import pytest` appears at the bottom of the file (line 76) but is used at lines 23, 25-26. Python resolves module-level names at import time so this happens to work, but it violates PEP 8 (all imports at top), confuses readers, and will cause `NameError` if the import is ever made conditional.

**Fix:** Move `import pytest` to the top of the file with the other imports.

---

### IN-02: Streaming `chat` path: missing guard for empty `req.messages` before `req.messages[-1]`

**File:** `api/chat.py:66`
**Issue:** This is the same root cause as CR-01 but noted separately for the streaming path fix suggested in WR-04 — both code paths access `req.messages[-1]` without checking for an empty list.

**Fix:** Covered by the guard added in CR-01 fix.

---

### IN-03: `conftest.py` `db_session` fixture leaks engine if session setup fails mid-fixture

**File:** `tests/conftest.py:17-25`
**Issue:** The fixture creates an engine, then enters a session context. If `create_all` succeeds but the session context manager raises during setup, `await engine.dispose()` is never reached because it is placed after the `yield` in an `async with` scope. The engine leak is minor in tests but the pattern is fragile.

**Fix:**
```python
@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        factory = async_sessionmaker(engine, expire_on_commit=False)
        async with factory() as session:
            yield session
    finally:
        await engine.dispose()
```

---

_Reviewed: 2026-07-15T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
