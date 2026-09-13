---
phase: 02-knowledge-tracing-backend
reviewed: 2026-07-16T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - api/chat.py
  - api/sessions.py
  - services/knowledge_tracing.py
  - services/tutor.py
  - tests/api/test_session_end.py
  - tests/services/conftest.py
  - tests/services/test_knowledge_tracing.py
  - tests/services/test_tutor.py
findings:
  critical: 3
  warning: 4
  info: 3
  total: 10
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-07-16
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Eight files were reviewed covering the BKT/FSRS knowledge tracing service, the chat and session API endpoints, the tutor prompt builder, and associated tests. The core BKT math (`update_bkt()`) and `next_topics()` ranking are correct. The FSRS scheduling path and the optimizer invocation are structurally sound against the installed library (fsrs>=6.3.1).

Three critical issues were found. The streaming path in `api/chat.py` uses the FastAPI-managed `AsyncSession` after the HTTP response headers have been sent, which will cause silent session corruption or errors when the connection is closed mid-stream. The `GET /sessions/{child_id}` endpoint has no authorization check, exposing any child's full session history to any caller with a valid `child_id`. The `State[mastery.card_state]` lookup in `update_fsrs_schedule()` will raise an unhandled `KeyError` if the DB contains any state string not in the current `State` enum (e.g., a value stored by an older schema or a manual DB edit).

---

## Critical Issues

### CR-01: Streaming generator uses FastAPI-managed session after response completes

**File:** `api/chat.py:66-76`

**Issue:** The `generate()` async generator captures `session` (the `AsyncSession` injected via `Depends(get_db)`). FastAPI's `get_db` dependency closes the session via its `async with` block when the *request handler returns* — which happens when `StreamingResponse(generate(), ...)` is returned on line 77, before any chunk has been sent. From that point onward, all `session` access inside `generate()` (including `create_session` on line 67 and `log_turn` on line 75) operates on a session that is already closed or in an undefined state. On asyncpg/aiosqlite drivers this surfaces as `MissingGreenlet` errors or silent no-ops depending on timing.

**Fix:** The generator must own its own session, opened independently of the request-scoped dependency:

```python
from db.session import AsyncSessionLocal

async def generate():
    async with AsyncSessionLocal() as gen_session:
        db_session_row = await create_session(child_id, gen_session)
        full_content = []
        response = await litellm.acompletion(model=model, messages=messages, stream=True)
        async for chunk in response:
            delta = chunk.choices[0].delta.content or ""
            full_content.append(delta)
            yield f"data: {json.dumps({'choices': [{'delta': {'content': delta}}]})}\n\n"
        yield "data: [DONE]\n\n"
        await log_turn(child_id, req.messages[-1].content, "".join(full_content),
                       gen_session, session_id=db_session_row.id)
```

---

### CR-02: No authorization on GET /sessions/{child_id} — IDOR / COPPA exposure

**File:** `api/sessions.py:14-35`

**Issue:** `GET /sessions/{child_id}` returns the full turn history (questions, answers, topics) for *any* child_id supplied in the URL path. There is no check that the caller owns or is authorized to access that child's data. Any device — or any HTTP client that can guess or enumerate a `child_id` — can read another child's complete session history. This is an insecure direct object reference (IDOR) and is especially serious under COPPA because it exposes a minor's learning session data to unauthenticated third parties.

The `POST /sessions/{session_id}/end` endpoint (line 38) has the same exposure — it can close any session given only a `session_id`, with no ownership verification.

**Fix (minimum):** Gate both endpoints on a device/auth token that is verified against the target `child_id` before returning data or triggering mutations. Until a proper auth layer exists, add an ownership check:

```python
@router.get("/sessions/{child_id}")
async def get_sessions(
    child_id: str,
    x_device_id: str = Header(None),
    ...
):
    # Verify the requesting device is linked to this child
    child = await get_child_by_id(child_id, session)
    if child is None or child.device_id != x_device_id:
        raise HTTPException(status_code=403, detail="Forbidden")
    ...
```

---

### CR-03: Unhandled KeyError when stored card_state is not in fsrs State enum

**File:** `services/knowledge_tracing.py:233`

**Issue:** `card.state = State[mastery.card_state]` uses dict-style enum access which raises `KeyError` for any string value that is not a member of the current `State` enum. The installed `fsrs>=6.3.1` has `State.Learning`, `State.Review`, `State.Relearning` — but notably **no `State.New`**. If any row in `mastery_state` has `card_state = 'New'` (stored by an older code version, a migration, or a manual insert), this line raises an unhandled `KeyError`, crashing the FSRS scheduling for that child with a 500 error. There is no try/except around this lookup.

**Fix:** Use `getattr` or a guard that falls back to a fresh card on unknown state strings:

```python
try:
    card.state = State[mastery.card_state]
except KeyError:
    # Unknown or stale state string — treat as new card to avoid crash
    pass  # card already initialized as Card() with default state
```

Or validate the value before using it:

```python
if mastery.card_state and mastery.card_state in State.__members__:
    card.state = State[mastery.card_state]
```

---

## Warnings

### WR-01: litellm imported inside the function body — masks ImportError, inhibits IDE support

**File:** `api/chat.py:64`

**Issue:** `import litellm` is placed inside the `chat()` function body, not at module level. Python caches the import after the first call, so there is no performance cost. However, if `litellm` is not installed or fails to import, the error is not raised at server startup — it surfaces as a 500 on the first request. It also prevents IDEs from resolving `litellm` symbols.

**Fix:** Move the import to the top of the file with the other imports:
```python
import litellm
```

---

### WR-02: log_turn after "[DONE]" sentinel — client sees completion before turn is persisted

**File:** `api/chat.py:74-76`

**Issue:** In the streaming path, `yield "data: [DONE]\n\n"` (line 74) is emitted *before* `await log_turn(...)` (line 75). The client receives the stream-complete signal while the DB write is still pending. If `log_turn` raises (e.g., due to the session-scope bug in CR-01, or a network error), the turn is silently lost — the client already believes the response was complete and logged. For a tutoring product where session history drives BKT, a lost turn corrupts knowledge state.

**Fix:** Swap the order: persist first, then yield DONE:
```python
await log_turn(child_id, req.messages[-1].content, "".join(full_content),
               gen_session, session_id=db_session_row.id)
yield "data: [DONE]\n\n"
```

---

### WR-03: fit_fsrs_params() conflates all KCs into a single virtual card for optimization

**File:** `services/knowledge_tracing.py:296-298`

**Issue:** Every `ReviewLog` entry is assigned `card_id=1` regardless of which KC it belongs to. The comment acknowledges this ("all events treated as a single virtual card for optimization"), but the consequence is significant: the FSRS optimizer sees a single card's history as a mix of interleaved reviews across completely different knowledge components. FSRS-5 optimizes stability and difficulty parameters that model forgetting *for a specific item*. Treating phonics, maths, and history events as one card produces parameter estimates that do not represent any individual child–KC relationship, potentially degrading scheduling quality for all KCs.

**Fix:** Either assign `card_id=hash(kc_id) % MAX_INT` to preserve per-KC separation within the optimizer, or document explicitly that this is a deliberate approximation accepted for cold-start simplicity and add a TODO to upgrade to per-KC fitting once sufficient data exists:

```python
review_logs.append(
    ReviewLog(
        card_id=abs(hash(event.kc_id)) % (2**31),  # per-KC isolation
        rating=rating,
        review_datetime=ts,
        review_duration=None,
    )
)
```

---

### WR-04: get_child_by_id called twice in chat endpoint — double DB round-trip

**File:** `api/chat.py:47-54`

**Issue:** When `x_device_id` is provided and `x_child_id` is not, the code calls `get_child_by_device_id()` (line 47) to retrieve the child object, extracts `child.id` (line 49), then discards the object and calls `get_child_by_id(child_id, session)` again on line 54 to retrieve it a second time. This is an unnecessary double-fetch.

**Fix:** Reuse the child object from the device lookup:
```python
child_id = x_child_id or req.child_id
child = None
if not child_id and x_device_id:
    child = await get_child_by_device_id(x_device_id, session)
    if child:
        child_id = str(child.id)

if not child_id:
    raise HTTPException(status_code=400, detail="No child identity...")

if child is None:
    child = await get_child_by_id(child_id, session)
if not child:
    raise HTTPException(status_code=404, detail="Child not found")
```

---

## Info

### IN-01: `mastery_ctx or None` collapses empty list to None — semantically redundant

**File:** `api/chat.py:58`

**Issue:** `mastery_context_for_prompt()` returns `list[dict]`, which is either `[]` or a populated list. The expression `mastery_ctx or None` converts `[]` to `None` before passing to `build_system_prompt()`. `build_system_prompt()` already handles `mastery_context=None` and `mastery_context=[]` identically (the `if mastery_context:` guard on line 273 of `tutor.py` is falsy for both). The `or None` is therefore functionally harmless but misleading — it implies the two cases require separate handling.

**Fix:** Pass the list directly:
```python
system_prompt = await build_system_prompt(child, mastery_context=mastery_ctx)
```

---

### IN-02: `get_settings()` called on every `build_system_prompt()` and `route_model()` invocation but result is unused in `build_system_prompt()`

**File:** `services/tutor.py:243`

**Issue:** `settings = get_settings()` is called at line 243 inside `build_system_prompt()` but `settings` is never referenced in that function body. It is only used in `route_model()` (line 278). This is dead code that adds a pointless settings lookup on every prompt build.

**Fix:** Remove the `settings = get_settings()` line from `build_system_prompt()`.

---

### IN-03: Test file test_knowledge_tracing.py lacks `@pytest.mark.asyncio` decorators (relies on implicit asyncio_mode=auto)

**File:** `tests/services/test_knowledge_tracing.py:111` (and all async test functions)

**Issue:** All async test functions rely on `asyncio_mode = auto` being set in `pytest.ini`. This is a project-wide setting that makes the tests fragile to any change in test configuration or running tests in isolation with a different pytest config. If a developer runs a subset of tests without the project `pytest.ini`, all async tests will be silently collected but not awaited — they will "pass" as coroutine objects without executing.

**Fix:** Either add explicit `@pytest.mark.asyncio` decorators to each async test, or verify `pytest.ini` is committed and always present. This is a robustness issue rather than a current breakage.

---

_Reviewed: 2026-07-16_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
