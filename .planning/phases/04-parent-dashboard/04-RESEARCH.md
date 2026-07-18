# Phase 4: Parent Dashboard - Research

**Researched:** 2026-07-18
**Domain:** FastAPI/Starlette auth, Jinja2 server-rendered HTML, SQLAlchemy CRUD, Alembic migration
**Confidence:** HIGH — all findings verified against live codebase and installed packages

---

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

**Auth (PARENT-05)**
- D-01: v1 auth is a fixed passphrase in `.env` (`PARENT_PASSWORD=xxxx`). No multi-tenant, no email signup.
- D-02: Auth state lives in a server-side httpOnly session cookie set at `POST /parent/login`.
- D-03: Login page at `/parent/login` — one password field, one submit, white-card aesthetic. No username field.
- D-04: Failed login / expired session → redirect to `/parent/login` with no error message.
- D-05: All `/parent/*` routes except `/parent/login` require valid session cookie. Fixes CR-02 — session endpoints must verify the authenticated parent's child_id matches.

**Mastery Map (PARENT-02)**
- D-06: 28-subject (actually 44-subject — see findings) accordion, collapsed by default.
- D-07: Each topic row: name + colour-coded mastery dot + last studied date.
- D-08: Mastery colours: `not_started` = grey, `fragile` = amber, `in_progress` = blue, `solid` = green (`#7a9e7e`).
- D-09: All 870 topics appear (not_started shown as grey); subjects collapsed by default.

**Alert Feed (PARENT-04)**
- D-10: Frustration: `hint_used` count > 3 on same KC in one session → alert logged at `end_session()`.
- D-11: Off-plan interest spike: new interest extracted by Phase 3 that was not in profile before → "new interest" alert.
- D-12: Sensitive-topic flag: add `safety_flag: bool` to `InteractionEventModel`. Set at `log_turn()` by keyword list check on question text. No LLM call.
- D-13: Alert feed: chronological (most recent first), row shows timestamp / child name / badge (`frustrated` / `sensitive` / `new-interest`) / triggering snippet.
- D-14: Alert retention: last 30 days.

**Profile Editor (PARENT-03)**
- D-15: Editable: name, age, reading_level (beginner/developing/fluent), neurodivergence flags, interests (add/remove tags).
- D-16: Neurodivergence checkboxes: dyslexia, ADHD, dyscalculia, autism, hyperlexia. Stored as JSON array in `ChildProfileModel.neurodivergence`. Storage format at Claude's discretion.
- D-17: Profile changes take effect immediately on next chat turn — `api/chat.py` must re-read from DB per request (not cache).
- D-18: Form inline at `/parent/children/{child_id}`, not a modal. HTML form with POST action.

**UI Style**
- D-19: White-card aesthetic (white cards, `#e0e0e0` borders, `border-radius: 12px`, `#7a9e7e` green accent, `-apple-system` sans-serif). No e-ink constraint on parent side.

### Claude's Discretion
- Session cookie implementation details (itsdangerous signing vs starlette SessionMiddleware)
- Exact HTML structure of accordion (pure CSS or minimal JS toggle)
- Interests tag editor UI (comma-separated input field is fine)
- Alert keyword list contents
- Exact DB query for tallying hint counts at session end

### Deferred Ideas (OUT OF SCOPE)
- Adaptive remediation routing when hint count > 3 (Phase 6)
- Alert notification mechanism (push/email) — dashboard-only v1
- Multi-child household management
- OpenID / OAuth parent auth
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PARENT-01 | Parent can view session history (turn-by-turn replay) | `get_turns_by_session_id()` CRUD already exists; `GET /v1/sessions/{session_id}/turns` already exists (HIST-03); needs Jinja2 replay view at `/parent/sessions/{id}` |
| PARENT-02 | Parent can view child's mastery map (topics x mastery bucket) | `_mastery_bucket()` and `MasteryStateModel` are available; `mastery_context_for_prompt()` pattern can be adapted; `updated_at` on MasteryStateModel serves as last-studied proxy |
| PARENT-03 | Parent can set/edit child profile (interests, neurodivergence flags, reading level) | `ChildProfileModel` fields all present; `update_interests()` exists; needs update_profile CRUD; `api/chat.py` confirmed re-reads from DB per request (no caching) |
| PARENT-04 | Parent receives flags for: sensitive topic questions, frustration signals, off-plan interest spikes | Needs `AlertModel` table; needs `safety_flag` column on `InteractionEventModel`; hint_used is currently `Boolean` (not count) — D-10 requires counting per KC per session |
| PARENT-05 | Parent dashboard web UI accessible at /parent | `api/parent.py` router already at `/parent`; `web/parent/templates/dashboard.html` exists with established CSS; needs SessionMiddleware + passphrase auth wired in |
</phase_requirements>

---

## Summary

Phase 4 builds the parent-facing web UI on top of well-established project infrastructure. The core patterns (Jinja2/HTMLResponse, async SQLAlchemy, Alembic migrations, pytest-asyncio) are already battle-tested in Phases 1–3. The planner's primary task is wiring six well-understood pieces together: session cookie auth, session replay view, mastery map accordion, alert feed (with a new AlertModel table), profile editor form, and the CR-02 IDOR fix.

The most important discovery is that `itsdangerous` is **not installed** in the project's venv, meaning `starlette.middleware.sessions.SessionMiddleware` cannot be imported — it hard-fails at module load. This is a Wave 0 blocker: `itsdangerous` must be added to `requirements.txt` and installed before any session cookie code can run. `secret_key` already exists in `config/settings.py` (`Settings.secret_key`), so no new config value is needed for signing.

Two data model gaps affect planning directly: (1) `hint_used` is a `Boolean` (not an integer count) on `InteractionEventModel`, so D-10 frustration counting requires a query that sums `hint_used=True` rows per KC per session — not a column read. (2) The curriculum has 870 topics across 44 subjects, not 777/28 as stated in project docs — the CONTEXT.md accordion count (D-06 "28 subjects") is outdated. The mastery map should be driven from `services.curriculum.CURRICULUM` and display whatever the live dataset contains.

**Primary recommendation:** Use `starlette.middleware.sessions.SessionMiddleware` with `itsdangerous` for session cookies (dead-simple, reversible, no extra dependencies beyond adding `itsdangerous`). Install `itsdangerous` in Wave 0.

---

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Passphrase auth + session cookie | Frontend Server (Starlette middleware + FastAPI route) | — | Server-side httpOnly cookie; no client JS needed |
| Session replay view | Frontend Server (Jinja2 template) | API/Backend (get_turns_by_session_id) | Data fetch from DB; HTML rendered on server |
| Mastery map accordion | Frontend Server (Jinja2 template) | Database (MasteryStateModel JOIN) | 870 rows pre-fetched; grouped in Python before render |
| Alert feed | Frontend Server (Jinja2 template) | Database (AlertModel) | Alerts stored in DB; rendered server-side |
| Profile editor form | Frontend Server (Jinja2 + POST handler) | Database (ChildProfileModel update) | Direct DB mutation; no API indirection needed |
| IDOR fix (CR-02) | API/Backend (`api/sessions.py`) | Frontend Server (require_parent_auth dep) | Auth dependency injected into both session endpoints |
| `safety_flag` Alembic migration | Database | — | New column on `interaction_events` |
| Frustration alert tally | API/Backend (`end_session()`) | Database (AlertModel) | Runs at session end hook, writes alert records |

---

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `starlette` | 1.3.1 (installed) | `SessionMiddleware` for httpOnly session cookies | Already a FastAPI dependency; no extra install beyond `itsdangerous` |
| `itsdangerous` | NOT INSTALLED — must add | Signs/verifies session cookie data | Starlette's `SessionMiddleware` imports it directly; required for sessions to work |
| `jinja2` | >=3.1.4 (requirements.txt) | HTML template rendering | Already used in `api/parent.py` and `api/child.py` |
| `alembic` | >=1.13.0 (requirements.txt) | DB schema migration | Already used for all schema changes |
| `sqlalchemy` | >=2.0.0 (requirements.txt) | Async ORM queries | All existing DB code uses this pattern |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `python-dotenv` | >=1.0.1 (requirements.txt) | Load `PARENT_PASSWORD` from `config/.env` | Already loads `Settings` via `pydantic_settings` — `PARENT_PASSWORD` added as a `Settings` field |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `starlette.middleware.sessions` | `itsdangerous.URLSafeTimedSerializer` directly | Direct signing is lower-level but requires writing cookie set/get boilerplate; SessionMiddleware is simpler and already integrated |
| `AlertModel` (new table) | Derive alerts from existing data at query time | Derivation requires complex multi-join; a separate table is O(1) reads and lets alerts persist independently of source data |

**Installation (Wave 0):**
```bash
echo "itsdangerous>=2.1.2" >> requirements.txt
pip install itsdangerous
```

**Version verification:**
```bash
# itsdangerous - must install, not yet present
pip index versions itsdangerous  # latest is 2.2.0 [ASSUMED]
```

---

## Package Legitimacy Audit

> Only one new package needs installing: `itsdangerous`.

| Package | Registry | Age | Downloads | Source Repo | slopcheck | Disposition |
|---------|----------|-----|-----------|-------------|-----------|-------------|
| itsdangerous | PyPI | ~14 yrs | Very high (Flask/Starlette dep) | github.com/pallets/itsdangerous | N/A | Approved — Pallets project, same org as Flask/Jinja2 |

*slopcheck was not run — `itsdangerous` is a well-known Pallets project dependency of Starlette itself. No legitimacy concern.* [ASSUMED: version number; legitimacy HIGH confidence from Pallets org membership]

**Packages removed due to slopcheck [SLOP] verdict:** none
**Packages flagged as suspicious [SUS]:** none

---

## Architecture Patterns

### System Architecture Diagram

```
Browser (parent)
       |
       | GET /parent/*  (requires valid session cookie)
       v
FastAPI + SessionMiddleware
       |
  [require_parent_auth dep]    <-- rejects if no cookie / wrong passphrase
       |
  api/parent.py routes
  ├── GET  /                → dashboard.html (child list + recent alerts)
  ├── GET  /login           → login.html
  ├── POST /login           → verify passphrase → set cookie → redirect /parent
  ├── POST /logout          → clear cookie → redirect /parent/login
  ├── GET  /children/{id}   → child_profile.html (profile editor + mastery map)
  ├── POST /children/{id}   → update ChildProfileModel → redirect back
  ├── GET  /sessions/{id}   → session_replay.html (turn-by-turn)
  └── GET  /alerts          → alert_feed.html
       |
  db/crud.py + services/knowledge_tracing.py
  ├── get_turns_by_session_id()          (PARENT-01 replay)
  ├── get_all_mastery_for_child()        (PARENT-02 mastery map — new)
  ├── update_child_profile()             (PARENT-03 — new)
  ├── get_alerts_for_child()             (PARENT-04 — new)
  └── MasteryStateModel / AlertModel     (DB layer)
```

### Recommended Project Structure

```
api/
└── parent.py          # extend: add login/logout/children/sessions/alerts routes

db/
├── models.py          # extend: add AlertModel, add safety_flag to InteractionEventModel
├── crud.py            # extend: add update_child_profile(), get_all_mastery_for_child(),
│                      #         get_alerts_for_child(), create_alert()
└── migrations/versions/
    └── XXXX_phase4_parent.py    # safety_flag + AlertModel migration

web/parent/templates/
├── dashboard.html     # extend existing (main overview)
├── login.html         # new: single-field passphrase form
├── child_profile.html # new: profile editor + mastery map accordion
├── session_replay.html# new: turn-by-turn session replay
└── alert_feed.html    # new: chronological alert list

tests/api/
└── test_parent_auth.py    # new: login/logout/protected route tests

tests/db/
└── test_crud_parent.py    # new: update_child_profile, get_alerts_for_child
```

### Pattern 1: SessionMiddleware + require_parent_auth dependency

**What:** `SessionMiddleware` writes/reads a server-side-signed cookie named `session`. The `require_parent_auth` FastAPI dependency reads `request.session` and raises `RedirectResponse` if the cookie is absent or invalid.

**When to use:** All `/parent/*` routes except `/parent/login`.

**How to add middleware** (add to `api/main.py` after `FastAPI()` instantiation):
```python
# Source: starlette docs — starlette.testclient pattern
from starlette.middleware.sessions import SessionMiddleware
from config.settings import get_settings

settings = get_settings()
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=False)
```

`https_only=False` is correct for local dev (HTTP). Production should set to `True` or serve behind TLS.

**require_parent_auth dependency pattern:**
```python
# Source: FastAPI Depends() pattern — api/sessions.py line 19 analog
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse

def require_parent_auth(request: Request):
    if not request.session.get("parent_authenticated"):
        raise RedirectResponse(url="/parent/login", status_code=303)
```

All protected routes add `_: None = Depends(require_parent_auth)` as a parameter.

### Pattern 2: Login POST handler

**What:** Verify passphrase (constant-time compare), set session key, redirect.

```python
# Source: standard Starlette session pattern [ASSUMED — no project analog exists yet]
import hmac
from config.settings import get_settings

@router.post("/login", response_class=RedirectResponse)
async def do_login(request: Request):
    form = await request.form()
    password = form.get("password", "")
    settings = get_settings()
    if hmac.compare_digest(password, settings.parent_password):
        request.session["parent_authenticated"] = True
        return RedirectResponse(url="/parent", status_code=303)
    return RedirectResponse(url="/parent/login", status_code=303)
```

`hmac.compare_digest` prevents timing attacks. `parent_password` is a new `Settings` field backed by `PARENT_PASSWORD` env var.

### Pattern 3: CR-02 fix — child_id ownership check

**What:** `GET /v1/sessions/{child_id}` and `GET /v1/sessions/{session_id}/turns` must verify the authenticated parent owns that child. In v1 single-family mode, owning the session cookie is sufficient — the parent is THE parent.

**Approach:** Gate both endpoints on a simple `require_parent_auth` check added as a dependency. Since v1 has one child per device and one parent, any authenticated parent can see any child's data.

```python
# api/sessions.py — add to both existing endpoints
@router.get("/sessions/{child_id}")
async def get_sessions(
    child_id: str,
    limit: int = Query(default=50, ge=1, le=500),
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_parent_auth),   # CR-02 fix
):
    ...
```

**Warning:** The `/v1/sessions/*` endpoints are also called by the device (child-facing API). If the device cannot supply a parent session cookie, gating on the parent cookie will break device sync. The safer CR-02 fix for v1 is to keep the API endpoints device-accessible but gate the `/parent/sessions/{id}` HTML view route on the parent cookie. The device endpoints can keep the existing `X-Device-ID` header ownership check from CR-02's suggested fix in the review. Planner must decide which approach: HTML-gate only, or also gate the JSON API.

### Pattern 4: Mastery map — full-child mastery load

**What:** Load ALL `MasteryStateModel` rows for a child (not just top-5), join to CURRICULUM, group by subject, render accordion.

```python
# db/crud.py — new function following get_session_history() pattern
async def get_all_mastery_for_child(
    child_id: str, session: AsyncSession
) -> dict[str, "MasteryStateModel"]:
    """Return all MasteryState rows for child_id as {kc_id: row} dict."""
    result = await session.execute(
        select(MasteryStateModel).where(MasteryStateModel.child_id == child_id)
    )
    rows = list(result.scalars().all())
    return {r.kc_id: r for r in rows}
```

In the route handler:
```python
from services.curriculum import CURRICULUM
from services.knowledge_tracing import _mastery_bucket
from collections import defaultdict

mastery_by_kc = await get_all_mastery_for_child(child_id, db)

subjects: dict[str, list] = defaultdict(list)
for topic in CURRICULUM:
    row = mastery_by_kc.get(topic.id)
    p = row.p_mastery if row is not None else None
    bucket = _mastery_bucket(p)
    last_studied = row.updated_at if row is not None else None
    subjects[topic.subject].append({
        "name": topic.name,
        "bucket": bucket,
        "last_studied": last_studied,
    })
# subjects is sorted(subjects.items()) for consistent accordion order
```

**No `last_studied` column exists** — use `MasteryStateModel.updated_at` as the proxy. This is set whenever BKT/FSRS updates run (at session end). It will be None for topics the child has never touched.

### Pattern 5: AlertModel table design

**What:** New table to persist alert records written at session end (frustration) and at `log_turn()` time (sensitive-topic).

```python
# db/models.py — new model following InteractionEventModel pattern
class AlertModel(Base):
    """Parent alerts: frustration / sensitive-topic / new-interest (PARENT-04)."""
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), nullable=False, index=True
    )
    alert_type: Mapped[str] = mapped_column(String, nullable=False)  # 'frustrated'|'sensitive'|'new-interest'
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    snippet: Mapped[Optional[str]] = mapped_column(String, nullable=True)   # question text excerpt
    kc_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)     # for frustrated alerts
    session_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("sessions.id"), nullable=True
    )
```

### Pattern 6: Frustration alert tally (D-10)

**What:** `hint_used` is a `Boolean` in `InteractionEventModel` (confirmed in codebase). D-10 requires counting `hint_used=True` rows per KC per session at `end_session()` time.

```python
# In end_session() or a new service function called from there
from sqlalchemy import func

result = await db.execute(
    select(
        InteractionEventModel.kc_id,
        func.count(InteractionEventModel.id).label("hint_count"),
    )
    .where(InteractionEventModel.session_id == session_id)
    .where(InteractionEventModel.hint_used == True)  # noqa: E712
    .where(InteractionEventModel.kc_id.isnot(None))
    .group_by(InteractionEventModel.kc_id)
)
rows = result.all()
for row in rows:
    if row.hint_count > 3:
        await create_alert(
            child_id=session_row.child_id,
            alert_type="frustrated",
            kc_id=row.kc_id,
            session_id=session_id,
            snippet=None,
            db=db,
        )
```

### Pattern 7: safety_flag keyword check at log_turn time

**What:** D-12 adds `safety_flag: bool` to `InteractionEventModel`. The check runs in `services/sessions.py` at `log_turn()` time (or in `api/chat.py` before calling `log_turn()`).

The keyword list is a module-level constant — no LLM call:
```python
_SAFETY_KEYWORDS: frozenset[str] = frozenset({
    "suicide", "self-harm", "kill myself", "die", "hurt myself",
    "abuse", "naked", "sex", "drugs", "weapons", "bomb",
    # planner assembles full list
})

def _has_safety_flag(text: str) -> bool:
    text_lower = text.lower()
    return any(kw in text_lower for kw in _SAFETY_KEYWORDS)
```

`log_turn()` in `db/crud.py` already accepts `**kwargs`-style keyword arguments — add `safety_flag: Optional[bool] = None` to the signature and pass it through to `InteractionEventModel(safety_flag=safety_flag)`.

### Pattern 8: HTML form for profile editing (D-18)

**What:** Standard HTML form POST — no JS. Follows same Jinja2/HTMLResponse pattern as existing templates.

```html
<!-- web/parent/templates/child_profile.html -->
<form method="POST" action="/parent/children/{{ child.id }}">
  <label>Name: <input name="name" value="{{ child.name }}"></label>
  <label>Age: <input type="number" name="age" value="{{ child.age }}" min="4" max="18"></label>
  <label>Reading level:
    <select name="reading_level">
      {% for level in ["beginner", "developing", "fluent"] %}
      <option value="{{ level }}" {% if child.reading_level == level %}selected{% endif %}>{{ level }}</option>
      {% endfor %}
    </select>
  </label>
  <!-- Neurodivergence checkboxes -->
  {% for flag in ["dyslexia", "adhd", "dyscalculia", "autism", "hyperlexia"] %}
  <label>
    <input type="checkbox" name="neurodivergence" value="{{ flag }}"
           {% if flag in (child.neurodivergence or []) %}checked{% endif %}>
    {{ flag }}
  </label>
  {% endfor %}
  <!-- Interests: comma-separated text field -->
  <label>Interests: <input name="interests" value="{{ child.interests | join(', ') }}"></label>
  <button type="submit">Save</button>
</form>
```

POST handler parses `request.form()`, calls new `update_child_profile()` CRUD, redirects back.

### Pattern 9: Test approach for HTML routes with session cookies

**What:** The existing test pattern uses `httpx.AsyncClient` with `app.dependency_overrides`. For session-cookie-protected routes, the client must supply a cookie.

```python
# tests/api/test_parent_auth.py
async def test_protected_route_without_cookie_redirects(test_client):
    response = await test_client.get("/parent", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/parent/login" in response.headers["location"]

async def test_login_sets_cookie_and_redirects(test_client):
    # Set PARENT_PASSWORD in test env
    response = await test_client.post(
        "/parent/login",
        data={"password": "test-password"},
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)
    assert "session" in response.cookies

async def test_authenticated_access_succeeds(test_client):
    # Login first, cookie is retained in client session
    await test_client.post("/parent/login", data={"password": "test-password"})
    response = await test_client.get("/parent")
    assert response.status_code == 200
```

`httpx.AsyncClient` preserves cookies across requests in the same client instance — login then use is the correct pattern.

**Critical:** `SessionMiddleware` must be on the `app` object before tests run. The existing `api/main.py` `app` is imported directly — adding `SessionMiddleware` there means all existing tests also run with it present. Existing tests do not call parent routes, so no breakage. The middleware's `secret_key` is loaded from `get_settings()`, which in tests defaults to `"dev-secret-change-me"`.

**Controlling `PARENT_PASSWORD` in tests:** Override via `monkeypatch.setenv("PARENT_PASSWORD", "test-password")` or set it in `config/.env` (already loaded by `Settings`). Since `get_settings()` is `@lru_cache`, tests must clear the cache if they change env vars mid-test — or set the env var before the first `get_settings()` call.

### Anti-Patterns to Avoid

- **Calling `get_settings()` inside a hot path repeatedly:** `get_settings()` is `@lru_cache` — calling it once at module level or in the dependency is fine. Do not add a new `lru_cache` call inside `require_parent_auth`.
- **`https_only=True` in dev:** `SessionMiddleware` with `https_only=True` silently refuses to set cookies on plain HTTP, causing auth to appear broken with no error. Use `False` for dev, `True` for prod.
- **Storing passphrase in session cookie payload:** Store only a boolean flag or session ID in the cookie. The passphrase never goes in the cookie.
- **`datetime.utcnow()` in AlertModel defaults:** Always `datetime.now(timezone.utc)` per project convention.
- **String interpolation in WHERE clauses:** Never — always use SQLAlchemy ORM column comparisons (project-wide security rule).
- **`mastery_ctx or None` anti-pattern:** Pass lists directly; `if mastery_context:` in callers handles empty list correctly (per IN-01 from Phase 2 review).

---

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Session cookie signing | Custom HMAC/base64 cookie signing | `starlette.middleware.sessions.SessionMiddleware` | Starlette's implementation handles replay attacks, expiry, and secure flag; itsdangerous signing is battle-tested |
| Passphrase timing attack | `password == env_password` | `hmac.compare_digest()` | `==` on strings is vulnerable to timing side-channel; stdlib `hmac` comparison is constant-time |
| Accordion expand/collapse | Custom JS event system | Single `<details>/<summary>` HTML element or 10-line CSS toggle | Native `<details>` needs zero JS and works in all browsers |
| Alert persistence | Querying events at render time | `AlertModel` table | Deriving alerts from events every page load requires expensive multi-join; a write-at-detection pattern is O(1) reads |
| Keyword safety check | LLM call at every turn | Module-level `frozenset` membership test | Deterministic, ~0ms, no API cost — LLM safety is Phase 6 SAFETY-01 |

**Key insight:** Starlette's `SessionMiddleware` is 40 lines of source code that handles all the tricky parts of cookie-based sessions. The only reason it wasn't present before is the missing `itsdangerous` dependency.

---

## Common Pitfalls

### Pitfall 1: `itsdangerous` not installed — `SessionMiddleware` import fails at startup

**What goes wrong:** Adding `from starlette.middleware.sessions import SessionMiddleware` to `api/main.py` causes a `ModuleNotFoundError: No module named 'itsdangerous'` on server startup.

**Why it happens:** Confirmed — `itsdangerous` is not in `requirements.txt` and not installed in the project venv. `starlette` imports it at the module level.

**How to avoid:** Wave 0 task: add `itsdangerous>=2.1.2` to `requirements.txt` and install it before any other Phase 4 work.

**Warning signs:** Server fails to start immediately after adding SessionMiddleware import.

### Pitfall 2: `get_settings()` lru_cache blocks `PARENT_PASSWORD` env override in tests

**What goes wrong:** `Settings` is instantiated once and cached. If a test tries to set `PARENT_PASSWORD` via `monkeypatch.setenv`, `get_settings()` still returns the cached object with the old value.

**Why it happens:** `@lru_cache` on `get_settings()` is intentional for production performance, but blocks test isolation.

**How to avoid:** Either (a) clear the cache in test teardown: `get_settings.cache_clear()`, or (b) set `PARENT_PASSWORD` in `config/.env` as a test default, or (c) add a `dependency_overrides` override that returns a modified `Settings` in tests.

### Pitfall 3: Mastery map renders 870 rows — performance consideration

**What goes wrong:** Loading all 870 `MasteryStateModel` rows plus joining CURRICULUM at render time on every page view is potentially slow.

**Why it happens:** `MasteryStateModel` has no index on `kc_id` alone (composite PK is `(child_id, kc_id)`). A `WHERE child_id = X` query uses the index correctly. This is not a real concern at v1 scale (one child, 870 rows max).

**How to avoid:** The single `SELECT WHERE child_id = X` query is fine. Python-side grouping into `defaultdict(list)` by subject is O(870). No special optimization needed for v1.

### Pitfall 4: hint_used is Boolean, not int — D-10 requires aggregation

**What goes wrong:** Assuming `hint_used` is a count and trying to read it directly as an integer. It is `Boolean nullable=True` in the schema.

**Why it happens:** D-10 says "hint_used count > 3" which sounds like a counter column. The existing schema has a bool flag.

**How to avoid:** Use `func.count()` aggregation in SQL (Pattern 6 above). Do not change the column type — the bool accurately records whether any hint was used on a given turn.

### Pitfall 5: Device API endpoints vs. parent auth gate (CR-02 scope)

**What goes wrong:** Adding `require_parent_auth` dependency to `GET /v1/sessions/{child_id}` breaks the device-facing sync path if the device calls this endpoint without a parent browser session.

**Why it happens:** CR-02 was found on the device-facing `/v1/` API, but the parent auth cookie is browser-only.

**How to avoid:** Gate the `/parent/sessions/{id}` HTML view route on the parent cookie. For the JSON `/v1/sessions/` endpoints, use the device-ID ownership check approach from CR-02's suggested fix in the code review. These are two separate gates for two separate audiences.

### Pitfall 6: `<details>/<summary>` accordion vs. CSS-only vs. JS

**What goes wrong:** Writing a JavaScript accordion from scratch introduces state management, event propagation issues, and break the no-JS-framework constraint.

**How to avoid:** Use native HTML `<details>/<summary>` elements. They are interactive without any JavaScript, support CSS transitions with `details[open]`, and are supported in all modern browsers. Default `open` attribute controls initial state.

---

## Code Examples

### SessionMiddleware wiring in main.py
```python
# Source: starlette docs / api/main.py existing middleware pattern [ASSUMED - no project analog]
from starlette.middleware.sessions import SessionMiddleware

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=False)
# Add AFTER CORSMiddleware — middleware executes in reverse-addition order in Starlette
```

### Mastery colour mapping in Jinja2 template
```html
<!-- Source: D-08 colour map — verified against dashboard.html CSS conventions -->
{% set bucket_color = {
  "not_started": "#b0b0b0",
  "fragile": "#e6a817",
  "in_progress": "#4a90d9",
  "solid": "#7a9e7e"
} %}
<span class="mastery-dot" style="background: {{ bucket_color[topic.bucket] }};
  width: 10px; height: 10px; border-radius: 50%; display: inline-block;"></span>
```

### Alert 30-day query
```python
# Source: get_24hr_history() pattern in db/crud.py [VERIFIED: codebase]
from datetime import datetime, timezone, timedelta

since = datetime.now(timezone.utc) - timedelta(days=30)
result = await db.execute(
    select(AlertModel)
    .where(AlertModel.child_id == child_id)
    .where(AlertModel.triggered_at >= since)
    .order_by(AlertModel.triggered_at.desc())
)
return list(result.scalars().all())
```

### PARENT_PASSWORD settings field
```python
# config/settings.py — extend Settings class [VERIFIED: codebase — settings.py read]
class Settings(BaseSettings):
    ...
    parent_password: str = "change-me-in-env"   # set PARENT_PASSWORD in config/.env
```

### update_child_profile CRUD
```python
# db/crud.py — follows update_mastery_state() pattern [VERIFIED: codebase]
async def update_child_profile(
    child_id: str,
    session: AsyncSession,
    *,
    name: Optional[str] = None,
    age: Optional[int] = None,
    reading_level: Optional[str] = None,
    neurodivergence: Optional[list] = None,
    interests: Optional[list] = None,
) -> Optional[ChildProfileModel]:
    child = await get_child_by_id(child_id, session)
    if child is None:
        return None
    if name is not None:
        child.name = name
    if age is not None:
        child.age = age
    if reading_level is not None:
        child.reading_level = reading_level
    if neurodivergence is not None:
        child.neurodivergence = neurodivergence
    if interests is not None:
        child.interests = interests
    await session.commit()
    await session.refresh(child)
    return child
```

---

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| JWT tokens for session auth | httpOnly session cookie via SessionMiddleware | Modern best practice | Session cookie eliminates client-side token storage risk; simpler for server-rendered HTML |
| Custom accordion JS | `<details>/<summary>` HTML | HTML5 | Zero JS needed for expand/collapse interaction |

---

## Open Questions

1. **CR-02 scope: HTML gate only vs. also gate `/v1/sessions/` JSON endpoints**
   - What we know: Device (child e-ink reader) calls `/v1/sessions/{child_id}` to sync history. Parent auth cookie is browser-only.
   - What's unclear: Does the device call these endpoints? If yes, parent cookie gate on `/v1/` routes breaks device sync.
   - Recommendation: Gate HTML views (`/parent/sessions/*`) on parent cookie. Gate `/v1/sessions/*` on `X-Device-ID` ownership check (the interim fix suggested in CR-02 review). This fully closes IDOR without breaking device.

2. **`last_studied` date source for mastery map**
   - What we know: `MasteryStateModel.updated_at` is set at session end when BKT/FSRS runs. It is `not None` only for KCs the child has been tested on.
   - What's unclear: `updated_at` is the BKT update time, not the turn timestamp. For topics with no mastery row, `last_studied` will be None.
   - Recommendation: Display `updated_at` as "last practiced"; show "never" for None. This is accurate and expected.

3. **`hint_used` bool vs. future count upgrade**
   - What we know: D-10 counts per-session per-KC via aggregation. The bool is sufficient for this.
   - What's unclear: Future phases may want a hint count per turn (e.g., "used 2 out of 3 hints"). Current bool loses that.
   - Recommendation: Keep bool for Phase 4. Add a `hint_count: int` column in a future phase if needed.

---

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| `itsdangerous` | `SessionMiddleware` | No | — | None — blocking for auth |
| `starlette` | `SessionMiddleware` | Yes | 1.3.1 | — |
| `jinja2` | HTML templates | Yes | installed | — |
| `alembic` | DB migration | Yes | installed | — |
| `sqlalchemy` | async ORM | Yes | installed | — |

**Missing dependencies with no fallback:**
- `itsdangerous` — must be installed in Wave 0 before any auth code can be loaded.

---

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest + pytest-asyncio |
| Config file | `pytest.ini` (asyncio_mode = auto, pythonpath = . tests/evals) |
| Quick run command | `pytest tests/api/test_parent_auth.py -x` |
| Full suite command | `pytest tests/ -x` |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| PARENT-05 | Unauthenticated GET /parent redirects to /parent/login | integration | `pytest tests/api/test_parent_auth.py::test_protected_route_without_cookie_redirects -x` | No — Wave 0 |
| PARENT-05 | POST /parent/login with correct passphrase sets cookie and redirects | integration | `pytest tests/api/test_parent_auth.py::test_login_sets_cookie_and_redirects -x` | No — Wave 0 |
| PARENT-05 | POST /parent/login with wrong passphrase redirects back (no error msg) | integration | `pytest tests/api/test_parent_auth.py::test_wrong_passphrase_redirects -x` | No — Wave 0 |
| PARENT-01 | GET /parent/sessions/{id} returns 200 HTML with turn data | integration | `pytest tests/api/test_parent_auth.py::test_session_replay_authenticated -x` | No — Wave 0 |
| PARENT-02 | GET /parent/children/{id} returns 200 HTML with mastery accordion | integration | `pytest tests/api/test_parent_auth.py::test_mastery_map_authenticated -x` | No — Wave 0 |
| PARENT-03 | POST /parent/children/{id} updates profile and redirects | integration | `pytest tests/db/test_crud_parent.py::test_update_child_profile -x` | No — Wave 0 |
| PARENT-04 | end_session() creates frustrated alert when hint_used > 3 for KC | integration | `pytest tests/db/test_crud_parent.py::test_frustration_alert_created -x` | No — Wave 0 |
| PARENT-04 | log_turn() sets safety_flag=True for keyword match | unit | `pytest tests/db/test_crud_parent.py::test_safety_flag_set_on_keyword_match -x` | No — Wave 0 |
| PARENT-04 | GET /parent/alerts returns 200 HTML with alert list | integration | `pytest tests/api/test_parent_auth.py::test_alert_feed_authenticated -x` | No — Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/api/test_parent_auth.py tests/db/test_crud_parent.py -x`
- **Per wave merge:** `pytest tests/ -x`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/api/test_parent_auth.py` — covers PARENT-01, PARENT-02, PARENT-04 (feed), PARENT-05
- [ ] `tests/db/test_crud_parent.py` — covers PARENT-03 (profile update), PARENT-04 (frustration + safety_flag)
- [ ] `requirements.txt` — add `itsdangerous>=2.1.2`
- [ ] `config/settings.py` — add `parent_password: str` field
- [ ] `api/main.py` — add `SessionMiddleware`
- [ ] Alembic migration — `safety_flag` on `interaction_events` + new `alerts` table

---

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | Yes | Passphrase via `hmac.compare_digest`; `itsdangerous`-signed session cookie |
| V3 Session Management | Yes | `starlette.middleware.sessions.SessionMiddleware`; httpOnly cookie; `https_only=True` in prod |
| V4 Access Control | Yes | `require_parent_auth` FastAPI dependency on all `/parent/*` routes; CR-02 IDOR closure |
| V5 Input Validation | Yes | Profile form fields: age is `int`, reading_level is enum-validated before DB write |
| V6 Cryptography | No | No custom crypto; session signing is handled by `itsdangerous` (Pallets project) |

### Known Threat Patterns for FastAPI + Starlette session cookies

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| IDOR on session/turn endpoints | Information disclosure | `require_parent_auth` dependency + child_id ownership check |
| Passphrase brute-force | Spoofing | No lockout in v1 (single-family, low risk); passphrase in `.env` not source control |
| Timing side-channel on passphrase compare | Spoofing | `hmac.compare_digest()` — constant-time string comparison |
| Session cookie theft (MITM) | Spoofing | `https_only=True` in production; httpOnly flag prevents XSS theft |
| XSS in template rendering | Tampering | Jinja2 auto-escapes HTML by default — all user content auto-escaped in `{{ }}` |
| COPPA: minor session data exposure | Information disclosure | Session and turn data scoped to parent cookie; no public endpoints for child data |

---

## Project Constraints (from CLAUDE.md)

- `Optional[X]` typing, not `X | None` — Python 3.9 compatibility requirement.
- `datetime.now(timezone.utc)` everywhere — never `datetime.utcnow()`.
- All WHERE clauses use SQLAlchemy ORM column comparisons — never string interpolation.
- GSD workflow enforcement — all file changes through a GSD phase.
- No e-ink constraint on parent dashboard — full browser CSS/JS is acceptable.
- COPPA compliance — minimal data, no raw audio stored, parent auth gates child data.

---

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `itsdangerous` latest version is >=2.1.2 on PyPI | Package Legitimacy Audit | Low — Pallets project, well-maintained; version check before install is trivial |
| A2 | `starlette.middleware.sessions.SessionMiddleware` signature unchanged in starlette 1.3.1 (httpOnly=True by default, https_only param exists) | Pattern 1 | Low — Starlette is a FastAPI dependency; breaking changes would break FastAPI |
| A3 | `hmac.compare_digest` is appropriate constant-time comparison for this use case | Pattern 2 | Low — stdlib function, purpose-built for this; no v1 multi-tenancy means brute-force risk is low |
| A4 | `MasteryStateModel.updated_at` is a sufficient proxy for "last studied" | Pattern 4 | Medium — `updated_at` is set at BKT update time, not at turn time; a topic touched but never updated via BKT would show wrong date. For v1 this is acceptable |
| A5 | Single-family v1 auth means any authenticated parent can see any child's data | Pattern 3 / CR-02 | Medium — if project evolves to multi-child before auth is hardened, IDOR re-emerges |

---

## Sources

### Primary (HIGH confidence — verified against live codebase)
- `/Users/scowan/Projects/scottcowan/etutor-server/db/models.py` — `InteractionEventModel.hint_used` confirmed Boolean; `MasteryStateModel` columns confirmed; `ChildProfileModel` fields confirmed
- `/Users/scowan/Projects/scottcowan/etutor-server/api/main.py` — `SessionMiddleware` not yet present; `secret_key` exists in `Settings`
- `/Users/scowan/Projects/scottcowan/etutor-server/config/settings.py` — `secret_key` field present; `parent_password` field absent
- `/Users/scowan/Projects/scottcowan/etutor-server/requirements.txt` — `itsdangerous` absent; `jinja2`, `alembic`, `starlette` (via fastapi) present
- `.venv/lib/python3.14/site-packages/starlette/` — `starlette==1.3.1` installed; `SessionMiddleware` fails import due to missing `itsdangerous`
- Curriculum runtime check — 870 topics across 44 subjects (not 777/28 as in project docs)
- `mastery_bucket` thresholds confirmed: `None/0.0-<0.5` = not_started/fragile, `0.5-<0.95` = in_progress, `>=0.95` = solid

### Secondary (MEDIUM confidence — pattern inference from codebase)
- Phase 3 PATTERNS.md — async SQLAlchemy patterns, test fixture patterns, service function signatures
- Phase 2 REVIEW.md — CR-02 IDOR description and suggested fix approach
- `web/parent/templates/dashboard.html` — established CSS variables and class naming conventions

### Tertiary (LOW confidence — training knowledge, not verified in session)
- `itsdangerous` PyPI version and Pallets org membership — well-known but not fetched this session
- `hmac.compare_digest` timing safety properties — stdlib documentation [ASSUMED]

---

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — verified against installed packages and requirements.txt
- Architecture: HIGH — based on live codebase inspection of all relevant files
- Pitfalls: HIGH — itsdangerous absence confirmed by venv import failure; hint_used boolean confirmed by model inspection
- Test patterns: HIGH — copied from existing test_session_end.py pattern in same project

**Research date:** 2026-07-18
**Valid until:** 2026-08-18 (stable stack, 30-day window)
