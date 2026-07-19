---
phase: 04-parent-dashboard
plan: 01
subsystem: parent-auth
tags: [auth, session, middleware, migration, alembic]
dependency_graph:
  requires: []
  provides:
    - require_parent_auth FastAPI dependency (gates all /parent/* except login/logout)
    - POST /parent/login + GET /parent/login + POST /parent/logout routes
    - SessionMiddleware wired into FastAPI app
    - AlertModel ORM class + safety_flag column on InteractionEventModel
    - Alembic migration 9f194421a0c6 (down_revision d8909e3e5f75)
  affects:
    - api/main.py (SessionMiddleware + ParentAuthRequired handler)
    - api/parent.py (auth routes + require_parent_auth dep)
    - db/models.py (AlertModel + safety_flag)
    - requirements.txt (itsdangerous)
    - config/settings.py (parent_password field)
tech_stack:
  added:
    - itsdangerous>=2.2.0 (SessionMiddleware signing)
    - starlette.middleware.sessions.SessionMiddleware
  patterns:
    - FastAPI custom exception + exception_handler for auth redirect (D-05)
    - hmac.compare_digest constant-time passphrase check (T-4-01-01)
    - Starlette 1.x TemplateResponse(request, name) API (not old dict form)
key_files:
  created:
    - api/parent.py (updated — auth routes + require_parent_auth)
    - web/parent/templates/login.html
    - tests/api/test_parent_auth.py
    - migrations/versions/9f194421a0c6_phase4_parent_safety_flag_and_alerts.py
  modified:
    - requirements.txt
    - config/settings.py
    - api/main.py
    - db/models.py
decisions:
  - "raise ParentAuthRequired() custom exception + app.exception_handler pattern chosen over raise RedirectResponse (which fails — Response is not BaseException)"
  - "Starlette 1.x TemplateResponse(request, name) positional API used — avoids Jinja2 LRU unhashable dict bug on Python 3.14"
  - "Test uses /parent/ (trailing slash) to skip FastAPI 307 normalisation redirect"
metrics:
  duration: ~20 min
  completed: 2026-07-20
  tasks_completed: 3
  files_changed: 8
---

# Phase 04 Plan 01: Parent Auth + DB Schema Summary

**One-liner:** Cookie-session parent auth with hmac passphrase gate, SessionMiddleware, login template, AlertModel + safety_flag Alembic migration.

---

## Tasks Completed

| Task | Name | Commit | Key Files |
|------|------|--------|-----------|
| 1 | itsdangerous dep, parent_password config, SessionMiddleware | 857e10c | requirements.txt, config/settings.py, api/main.py |
| 2 | Auth routes, require_parent_auth dep, login template, auth tests | 87db154 | api/parent.py, web/parent/templates/login.html, tests/api/test_parent_auth.py |
| 3 | AlertModel + safety_flag migration | 74d9216 | db/models.py, migrations/versions/9f194421a0c6_… |

---

## Verification Results

- `pytest tests/api/test_parent_auth.py -x -q`: **6 passed**
- `alembic downgrade -1 && alembic upgrade head`: **clean round-trip**
- `from db.models import AlertModel, InteractionEventModel; assert hasattr(InteractionEventModel, 'safety_flag')`: **PASS**
- `pytest tests/ -x -q --ignore=tests/evals`: **94 passed, 0 failed**
- `from api.main import app` + middleware check: **SessionMiddleware wired**

---

## D-17 Verification (confirmed, no code change)

`api/chat.py` calls `get_child_by_id(child_id, session)` inside the request handler
using a fresh `AsyncSession` from `Depends(get_db)` — no module-level child caching.
D-17 (no stale child profile) is satisfied as-is.

---

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `raise RedirectResponse(...)` fails — Response is not BaseException**
- **Found during:** Task 2 first test run
- **Issue:** `require_parent_auth` raised `RedirectResponse` as an exception. Python 3.x requires exceptions to derive from `BaseException`; `Response` does not.
- **Fix:** Introduced `ParentAuthRequired(Exception)` sentinel class; registered `app.exception_handler(ParentAuthRequired)` in `api/main.py` to return the 303 redirect.
- **Files modified:** `api/parent.py`, `api/main.py`
- **Commit:** 87db154

**2. [Rule 1 - Bug] Starlette 1.x `TemplateResponse` API change — old dict form raises `TypeError`**
- **Found during:** Task 2 first test run (Jinja2 LRU cache TypeError: unhashable dict key)
- **Issue:** `templates.TemplateResponse("name.html", {"request": request, ...})` fails with Starlette ≥ 1.0 / Python 3.14 due to Jinja2 LRU cache treating the context dict as part of the cache key.
- **Fix:** Changed all `TemplateResponse` calls in `api/parent.py` to the new `TemplateResponse(request, "name.html", context_dict)` positional API.
- **Files modified:** `api/parent.py`
- **Commit:** 87db154
- **Note:** `api/child.py` has the same issue (pre-existing, out of scope of this plan). Logged to deferred-items.

**3. [Rule 1 - Bug] Test for auth redirect needed adjustment for FastAPI trailing-slash 307**
- **Found during:** Task 2 test run
- **Issue:** FastAPI emits a 307 (trailing-slash normalisation) when `GET /parent` hits the router before the auth dep runs.
- **Fix 1 (test_protected_route_without_cookie_redirects):** Changed to `follow_redirects=True` and assert final page has "Passphrase" in body.
- **Fix 2 (test_authenticated_get_parent_returns_200):** Changed assertion URL to `/parent/` (with trailing slash) to avoid the 307.
- **Files modified:** `tests/api/test_parent_auth.py`
- **Commit:** 87db154

---

## Known Stubs

None — all routes in this plan are fully wired. The `sessions = {}` dict in `parent_dashboard` is a documented Phase 1 placeholder, unrelated to this plan's objectives and will be populated in 04-03.

---

## Threat Surface

| Flag | File | Description |
|------|------|-------------|
| T-4-01-02 note | api/main.py | `https_only=False` on SessionMiddleware is correct for dev HTTP; **production must set `https_only=True`** — SessionMiddleware's httpOnly flag prevents XSS theft, but without https_only the signed cookie can be intercepted in transit on plain HTTP. Set via env var or deployment config before going live. |

---

## Self-Check

Files exist:
- `api/parent.py` — FOUND
- `web/parent/templates/login.html` — FOUND
- `tests/api/test_parent_auth.py` — FOUND
- `migrations/versions/9f194421a0c6_phase4_parent_safety_flag_and_alerts.py` — FOUND

Commits exist:
- 857e10c — FOUND
- 87db154 — FOUND
- 74d9216 — FOUND

## Self-Check: PASSED
