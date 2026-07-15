---
phase: 01-database-foundation
fixed_at: 2026-07-15T00:00:00Z
review_path: .planning/phases/01-database-foundation/01-REVIEW.md
iteration: 1
findings_in_scope: 11
fixed: 11
skipped: 0
status: all_fixed
---

# Phase 01: Code Review Fix Report

**Fixed at:** 2026-07-15T00:00:00Z
**Source review:** .planning/phases/01-database-foundation/01-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 11
- Fixed: 11
- Skipped: 0

## Fixed Issues

### CR-01: `chat` endpoint crashes on empty `messages` list

**Files modified:** `api/chat.py`
**Commit:** c154a71
**Applied fix:** Added `field_validator("messages")` to `ChatRequest` model that raises `ValueError("messages must not be empty")` when the list is empty. Also imported `field_validator` from pydantic.

---

### CR-02: `chat` endpoint does not check if `child_id` resolves to an existing child

**Files modified:** `api/chat.py`
**Commit:** 8c2fad2
**Applied fix:** Added `if not child: raise HTTPException(status_code=404, detail="Child not found")` immediately after `get_child_by_id()` call, preventing `AttributeError` when `child` is `None`.

---

### CR-03: `device_id` is not unique — one device can be mapped to multiple children

**Files modified:** `db/models.py`, `migrations/versions/9f229414e92b_initial_schema.py`
**Commit:** 0b83d09
**Applied fix:** Added `unique=True` to the `device_id` `mapped_column` in `ChildProfileModel`. Updated the initial migration to set `unique=True` on `ix_child_profiles_device_id` index so the constraint is enforced at the database level.

---

### CR-04: `build_recommendation_message` crashes with `IndexError` when `child.interests` is empty

**Files modified:** `services/recommender.py`
**Commit:** 68216a7
**Applied fix:** Changed the guard from `if not books:` to `if not books or not child.interests:` so the function returns `""` when either books list or interests list is empty, preventing `IndexError` on `child.interests[0]`.

---

### CR-05: CORS `allow_origins=["*"]` with no authentication

**Files modified:** `api/main.py`
**Commit:** 52098ad
**Applied fix:** Replaced `allow_origins=["*"]`, `allow_methods=["*"]`, `allow_headers=["*"]` with restricted values: `allow_origins=["http://localhost", "http://127.0.0.1"]`, `allow_methods=["POST", "GET"]`, `allow_headers=["X-Child-ID", "X-Device-ID", "Content-Type"]`.

---

### WR-01: `get_session_history` fetches all rows then slices in Python

**Files modified:** `db/crud.py`
**Commit:** 0d9b115
**Applied fix:** Replaced the unbounded SQL fetch + Python slice with `ORDER BY timestamp DESC LIMIT limit` in the query, then `list(reversed(rows))` to restore ASC order for callers. Updated the docstring accordingly.

---

### WR-02: `_transcribe_local` is blocking CPU-bound code inside an `async` function

**Files modified:** `api/stt.py`
**Commit:** 20dc4f6
**Applied fix:** (Combined with WR-03) Wrapped the synchronous transcription work in a nested `_sync_transcribe()` function and delegated it via `loop.run_in_executor(None, _sync_transcribe)`. Added `import asyncio` at the top.

---

### WR-03: `WhisperModel` is re-instantiated on every request

**Files modified:** `api/stt.py`
**Commit:** 20dc4f6
**Applied fix:** (Combined with WR-02) Introduced a module-level `_whisper_model = None` singleton and a `_get_whisper_model()` accessor that lazy-initialises the model on first call and reuses it on all subsequent calls. The lazy-init approach avoids requiring changes to the `lifespan` function while still paying the model-load cost only once.

---

### WR-04: Streaming path in `chat` does not log the turn to the database

**Files modified:** `api/chat.py`
**Commit:** 75d5e63
**Applied fix:** Inside the `generate()` async generator, added `db_session_row = await create_session(child_id, session)` before streaming, accumulated chunks into `full_content`, and added `await log_turn(...)` after `yield "data: [DONE]\n\n"` so the complete response is persisted to the database after the stream ends.

---

### WR-05: `api/sessions.py` — `limit` parameter has no upper bound

**Files modified:** `api/sessions.py`
**Commit:** 9019832
**Applied fix:** Added `Query` import from `fastapi` and changed `limit: int = 50` to `limit: int = Query(default=50, ge=1, le=500)`, enforcing a minimum of 1 and maximum of 500.

---

### WR-06: `datetime.utcnow()` is deprecated in Python 3.12+

**Files modified:** `db/models.py`, `db/crud.py`
**Commit:** 70be973
**Applied fix:** Added `timezone` to the `from datetime import ...` statement in both files. Replaced all three ORM column defaults in `db/models.py` (`started_at`, `timestamp`, `updated_at`) with `default=lambda: datetime.now(timezone.utc)` and `DateTime(timezone=True)`. Replaced `datetime.utcnow()` call in `update_mastery_state` in `db/crud.py` with `datetime.now(timezone.utc)`.

---

_Fixed: 2026-07-15T00:00:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
