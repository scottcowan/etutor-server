---
phase: 04-parent-dashboard
reviewed: 2026-07-20T00:00:00Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - api/parent.py
  - api/main.py
  - api/sessions.py
  - config/settings.py
  - db/crud.py
  - db/models.py
  - services/session_intelligence.py
  - web/parent/templates/login.html
  - web/parent/templates/dashboard.html
  - web/parent/templates/child_profile.html
  - web/parent/templates/session_replay.html
  - web/parent/templates/alert_feed.html
  - tests/api/test_parent_auth.py
  - tests/api/test_parent_views.py
  - tests/db/test_crud_parent.py
findings:
  critical: 3
  warning: 4
  info: 4
  total: 11
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-07-20
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

Phase 04 introduces a parent dashboard with passphrase authentication, session replay, a mastery
map accordion, a profile editor, and a three-type alert feed. The security decisions are largely
sound — constant-time compare, no error leakage on failed login, SQLAlchemy-parameterised queries
throughout. However, three blockers were found: the "Sign out" link is broken in every template
(GET link on a POST-only route), unvalidated age input crashes the server with a 500, and the
hardcoded `secret_key` default allows session-cookie forgery if the env var is not set.

---

## Critical Issues

### CR-01: "Sign out" link broken — GET request hits POST-only route → 405

**File:** `web/parent/templates/dashboard.html:57`, `web/parent/templates/child_profile.html:80`,
`web/parent/templates/session_replay.html:37`, `web/parent/templates/alert_feed.html:44`

**Issue:** All four templates render the Sign Out control as `<a href="/parent/logout">`. The
`do_logout` handler is decorated `@router.post("/logout")` — it only accepts POST. Clicking the
link sends a GET request, which FastAPI responds to with 405 Method Not Allowed. The user cannot
log out from any page.

The `onclick` attribute in `dashboard.html` sets `data-method='post'` on the anchor, which has
no effect on the HTTP method — it is not a JavaScript form-submission pattern. The remaining three
templates have no JavaScript at all.

**Fix:** Replace the anchor tag with a minimal `<form>` that submits a POST:

```html
<form method="POST" action="/parent/logout" style="display:inline;margin:0;">
  <button type="submit"
          style="background:none;border:none;color:#7a9e7e;font-size:0.95rem;
                 margin-left:auto;cursor:pointer;padding:0;">
    Sign out
  </button>
</form>
```

Apply this same pattern to all four header Sign Out controls.

---

### CR-02: Unvalidated age input — `int()` on arbitrary string raises uncaught ValueError → 500

**File:** `api/parent.py:170`

**Issue:**
```python
age_raw = form.get("age")
age = int(age_raw) if age_raw else None
```
Any non-numeric value in the age field (e.g., `"abc"`, `"1.5"`, `" "`) raises `ValueError`.
FastAPI has no exception handler for this, so the server returns a 500 Internal Server Error.
A parent who accidentally tabs into an unexpected value, or any client that sends a malformed
form, will see a crash response.

**Fix:**
```python
age_raw = form.get("age")
try:
    age = int(age_raw) if age_raw else None
except (ValueError, TypeError):
    age = None
```
Optionally add a bounds check (`4 <= age <= 18`) to match the HTML `min`/`max` constraints.

---

### CR-03: Hardcoded `secret_key` default allows session-cookie forgery

**File:** `config/settings.py:8`

**Issue:**
```python
secret_key: str = "dev-secret-change-me"
```
The `SessionMiddleware` at `api/main.py:45` uses this value to sign itsdangerous session cookies.
If the `SECRET_KEY` environment variable is not set in production, all sessions are signed with the
publicly-known string `"dev-secret-change-me"`. An attacker who knows this default can construct
a valid session cookie containing `{"parent_authenticated": true}` and gain full dashboard access
without knowing the passphrase.

**Fix:** Fail fast at startup if the secret is still the default, rather than silently using it:
```python
from pydantic import field_validator

class Settings(BaseSettings):
    secret_key: str = "dev-secret-change-me"

    @field_validator("secret_key")
    @classmethod
    def reject_default_secret(cls, v: str) -> str:
        import os
        if v == "dev-secret-change-me" and os.getenv("ENV", "dev") == "production":
            raise ValueError("SECRET_KEY must be set to a strong random value in production")
        return v
```
Or unconditionally require the field to be explicitly set (no default), so the server refuses to
start at all without `SECRET_KEY` in the environment.

---

## Warnings

### WR-01: `https_only=False` hardcoded — session cookie lacks Secure flag in production

**File:** `api/main.py:45`

**Issue:**
```python
app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key, https_only=False)
```
`https_only=False` is hardcoded rather than read from settings. The Starlette source confirms
that `https_only=False` omits the `Secure` cookie attribute. In a production deployment over
HTTPS the session cookie will be sent over any HTTP request as well, making it trivially
interceptable on a network.

**Fix:** Read the flag from settings:
```python
# config/settings.py
https_only: bool = False  # override to True in production via env var HTTPS_ONLY=true

# api/main.py
app.add_middleware(
    SessionMiddleware,
    secret_key=get_settings().secret_key,
    https_only=get_settings().https_only,
)
```

---

### WR-02: `neurodivergence` checkbox values not validated server-side

**File:** `api/parent.py:174`

**Issue:**
```python
neurodivergence = list(form.getlist("neurodivergence"))
```
The HTML form offers five known checkbox values (`dyslexia`, `adhd`, `dyscalculia`, `autism`,
`hyperlexia`), but the server performs no validation. A client can POST arbitrary strings and
they are stored verbatim in the `neurodivergence` JSON column. By contrast, `reading_level` is
correctly validated against `_VALID_READING_LEVELS`. The same defence should apply here.

**Fix:**
```python
_VALID_NEURODIVERGENCE = {"dyslexia", "adhd", "dyscalculia", "autism", "hyperlexia"}

# In child_profile_post:
raw_values = form.getlist("neurodivergence")
neurodivergence = [v for v in raw_values if v in _VALID_NEURODIVERGENCE] or None
```

---

### WR-03: `safety_flag` stored as `None` for clean turns instead of `False`

**File:** `db/crud.py:211`

**Issue:**
```python
safety_flag=True if flagged else None,
```
When a question does not match the keyword list, `safety_flag` is written as SQL `NULL` instead
of `False`. This conflates "was checked and is clean" with "was never checked." It makes the
column useless for queries like `WHERE safety_flag = FALSE` (to confirm which turns were
evaluated). The model declares the column `nullable=True`, which is correct for backwards
compatibility with events that predate this logic, but new turns should receive an explicit
`False`.

**Fix:**
```python
safety_flag=True if flagged else False,
```
If backward-compatible NULL semantics are genuinely needed (e.g., "this turn was logged before
Phase 4"), keep `None` only for pre-Phase-4 data and write `False` for all new turns.

---

### WR-04: Session cookie secret evaluated at import time — test env overrides arrive too late

**File:** `api/main.py:45`

**Issue:**
```python
app.add_middleware(SessionMiddleware, secret_key=get_settings().secret_key, https_only=False)
```
`get_settings()` is called during module import, before any test fixture can set
`os.environ["SECRET_KEY"]` or `os.environ["PARENT_PASSWORD"]`. The test fixtures in
`test_parent_auth.py` correctly clear the `lru_cache` for `get_settings` — but the
`SessionMiddleware` is already instantiated at that point with the cache's first-call value.

In practice the tests pass because the `secret_key` default is the same constant across all
test runs. But this means test cookies and production cookies are signed with the same key
when the env var is not set, and any accidental production config omission would be invisible
in CI.

**Fix:** Move settings resolution into the lifespan or use a lazy-init middleware wrapper:
```python
settings = get_settings()
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.secret_key,
    https_only=settings.https_only,
)
```
Combine with CR-03's startup validation so misconfiguration is caught before the middleware
is instantiated.

---

## Info

### IN-01: IDOR — session replay has no child-ownership check

**File:** `api/parent.py:102-121`

**Issue:** `GET /parent/sessions/{session_id}` fetches the `SessionModel` and its turns by UUID
without verifying that the session belongs to the authenticated family's children. An authenticated
parent can view any session by guessing (or enumerating) session UUIDs. For a v1 single-family
deployment the practical risk is low, but the gap should be documented and addressed before
multi-family deployment.

**Fix:** After fetching `session_obj`, check that `session_obj.child_id` is in the set of
children accessible to the authenticated parent:
```python
children = await list_children(session)
allowed_ids = {c.id for c in children}
if session_obj.child_id not in allowed_ids:
    return HTMLResponse("Not found.", status_code=404)
```

---

### IN-02: Test `test_session_replay_unauthenticated_redirects` does not assert redirect destination

**File:** `tests/api/test_parent_views.py:168-179`

**Issue:** The test checks that an unauthenticated request produces either a 200 with "Passphrase"
in the body or a 3xx status code. It never asserts that the `Location` header points to
`/parent/login`. If the route returned a 302 to `/parent/some-other-page`, the test would still
pass. The D-05 contract (redirect specifically to `/parent/login`) is not asserted.

**Fix:**
```python
assert response.status_code in (302, 303, 307)
assert "/parent/login" in response.headers.get("location", "")
```

---

### IN-03: `import pytest` is unused in both test files

**File:** `tests/api/test_parent_auth.py:2`, `tests/api/test_parent_views.py:2`

**Issue:** `import pytest` appears at the top of both test files. With `asyncio_mode = auto` in
`pytest.ini`, plain `async def` tests are collected without `@pytest.mark.asyncio`. No
`pytest.raises`, `pytest.mark`, or `pytest.param` constructs are used in either file.

**Fix:** Remove the unused import from both files.

---

### IN-04: Jinja2 autoescaping is implicit — no explicit opt-in

**File:** `api/parent.py:24`

**Issue:**
```python
templates = Jinja2Templates(directory="web/parent/templates")
```
FastAPI's `Jinja2Templates` enables autoescaping for `.html` files by default, so values like
`turn.question`, `turn.answer`, and `alert.snippet` are HTML-escaped at render time. This is
correct behaviour, but nothing in the code makes the dependency on autoescaping explicit. If a
future change passes a `Jinja2Templates(env=Environment(autoescape=False))`, the XSS protection
silently disappears. The snippet rendering in `session_replay.html` (which displays verbatim child
input) is the highest-risk target.

**Fix:** Make the dependency explicit in code or in a comment:
```python
# autoescape=True is the Jinja2Templates default for .html — do not override.
templates = Jinja2Templates(directory="web/parent/templates")
```
Or pass the environment explicitly:
```python
from jinja2 import Environment, FileSystemLoader, select_autoescape
env = Environment(
    loader=FileSystemLoader("web/parent/templates"),
    autoescape=select_autoescape(["html"]),
)
templates = Jinja2Templates(env=env)
```

---

_Reviewed: 2026-07-20_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
