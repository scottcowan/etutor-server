# Phase 4: Parent Dashboard - Pattern Map

**Mapped:** 2026-07-18
**Files analyzed:** 16 new/modified files
**Analogs found:** 15 / 16

---

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `api/parent.py` | controller | request-response | `api/child.py` | exact |
| `api/sessions.py` | controller | request-response | `api/sessions.py` (self — add dep) | exact |
| `api/chat.py` | controller | streaming/request-response | `api/chat.py` (self — verify D-17) | exact |
| `api/main.py` | config | request-response | `api/main.py` (self — add middleware) | exact |
| `db/models.py` | model | CRUD | `db/models.py` → `InteractionEventModel`, `MasteryStateModel` | exact |
| `db/crud.py` | service | CRUD | `db/crud.py` → `get_24hr_history()`, `update_mastery_state()` | exact |
| `config/settings.py` | config | — | `config/settings.py` (self — add field) | exact |
| `requirements.txt` | config | — | `requirements.txt` (self — add dep) | exact |
| `web/parent/templates/login.html` | component | request-response | `web/parent/templates/dashboard.html` | role-match |
| `web/parent/templates/dashboard.html` | component | request-response | `web/parent/templates/dashboard.html` (extend) | exact |
| `web/parent/templates/child_profile.html` | component | CRUD | `web/child/templates/home.html` | role-match |
| `web/parent/templates/session_replay.html` | component | request-response | `web/parent/templates/dashboard.html` `.turn` pattern | role-match |
| `web/parent/templates/alert_feed.html` | component | request-response | `web/parent/templates/dashboard.html` `.session-list` pattern | role-match |
| `tests/api/test_parent_auth.py` | test | request-response | `tests/api/test_session_end.py` | exact |
| `tests/db/test_crud_parent.py` | test | CRUD | `tests/db/test_crud_profiles.py` | exact |
| Alembic migration (`migrations/versions/XXXX_phase4_parent.py`) | migration | CRUD | `migrations/versions/d8909e3e5f75_add_child_fsrs_params.py` | exact |

---

## Pattern Assignments

### `api/parent.py` (controller, request-response)

**Analog:** `api/child.py` (Jinja2/HTMLResponse router pattern) + `api/sessions.py` (Depends pattern)

**Imports pattern** (`api/child.py` lines 1–8, `api/parent.py` lines 1–8 — extend):
```python
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
import hmac

from db.session import get_db
from config.settings import get_settings
```

**Existing router wiring** (`api/parent.py` lines 9–23 — keep, extend):
```python
router = APIRouter()
templates = Jinja2Templates(directory="web/parent/templates")

@router.get("/", response_class=HTMLResponse)
async def parent_dashboard(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    ...
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "children": children, "sessions": sessions},
    )
```

**Auth dependency pattern** (new — copy structure from `api/sessions.py` `Depends(get_db)` style):
```python
from fastapi.responses import RedirectResponse

def require_parent_auth(request: Request):
    if not request.session.get("parent_authenticated"):
        raise RedirectResponse(url="/parent/login", status_code=303)

# Apply to all protected routes:
@router.get("/alerts", response_class=HTMLResponse)
async def alert_feed(
    request: Request,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_parent_auth),   # auth gate
):
    ...
```

**Login POST handler pattern** (new — based on RESEARCH.md Pattern 2):
```python
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

**HTMLResponse + TemplateResponse return pattern** (`api/child.py` lines 14–19, `api/parent.py` lines 13–23):
```python
return templates.TemplateResponse(
    "child_profile.html",
    {"request": request, "child": child, "subjects": subjects},
)
```

**Profile POST handler pattern** (new — based on RESEARCH.md Pattern 8):
```python
@router.post("/children/{child_id}", response_class=RedirectResponse)
async def update_profile(
    request: Request,
    child_id: str,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_parent_auth),
):
    form = await request.form()
    name = form.get("name") or None
    age_raw = form.get("age")
    age = int(age_raw) if age_raw else None
    reading_level = form.get("reading_level") or None
    neurodivergence = list(form.getlist("neurodivergence"))
    interests_raw = form.get("interests", "")
    interests = [i.strip() for i in interests_raw.split(",") if i.strip()] or None
    await update_child_profile(child_id, session, name=name, age=age,
                               reading_level=reading_level,
                               neurodivergence=neurodivergence,
                               interests=interests)
    return RedirectResponse(url=f"/parent/children/{child_id}", status_code=303)
```

---

### `api/sessions.py` (controller, request-response — CR-02 IDOR fix)

**Analog:** `api/sessions.py` itself (lines 39–59) — add `require_parent_auth` dep to HTML session view only.

**Existing GET /sessions/{session_id}/turns** (`api/sessions.py` lines 39–59):
```python
@router.get("/sessions/{session_id}/turns")
async def get_session_turns(
    session_id: str,
    db: AsyncSession = Depends(get_db),
):
    # HIST-03 (CR-02 note): same IDOR exposure as GET /sessions/{child_id}
    turns = await get_turns_by_session_id(session_id, db)
    ...
```

**CR-02 note (RESEARCH.md Pitfall 5):** The `/v1/sessions/` JSON API endpoints are called by the device (child e-ink reader). Do NOT add `require_parent_auth` to `/v1/sessions/*` — that breaks device sync. The IDOR fix for the device API path is an `X-Device-ID` ownership check (logged in CR-02). The parent HTML view route at `/parent/sessions/{id}` is separately gated by `require_parent_auth` in `api/parent.py`.

---

### `api/chat.py` (controller, streaming — D-17 verification)

**Analog:** `api/chat.py` itself (lines 63–65) — no change needed; D-17 is already satisfied.

**Confirmed pattern** (`api/chat.py` lines 63–65):
```python
child = await get_child_by_id(child_id, session)
if not child:
    raise HTTPException(status_code=404, detail="Child not found")
```

`get_child_by_id` is called per-request with a fresh `AsyncSession` from `Depends(get_db)`. No module-level caching of `child`. D-17 is satisfied as-is — no code change needed, but planner should note this as a verification step.

---

### `api/main.py` (config — add SessionMiddleware)

**Analog:** `api/main.py` lines 38–43 — existing `CORSMiddleware` wiring shows the `add_middleware` pattern.

**Existing middleware pattern** (`api/main.py` lines 38–43):
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],
    allow_methods=["POST", "GET"],
    allow_headers=["X-Child-ID", "X-Device-ID", "Content-Type"],
)
```

**New SessionMiddleware** — add AFTER CORSMiddleware (starlette executes in reverse-addition order):
```python
from starlette.middleware.sessions import SessionMiddleware
# After the CORSMiddleware block:
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, https_only=False)
```

`settings.secret_key` already exists (`config/settings.py` line 8: `secret_key: str = "dev-secret-change-me"`). Call `get_settings()` at module level (it is `@lru_cache`): `settings = get_settings()` after imports.

---

### `db/models.py` (model, CRUD — add safety_flag + AlertModel)

**Analog:** `db/models.py` — `InteractionEventModel` (lines 52–71) for column addition; `MasteryStateModel` (lines 74–92) for the new `AlertModel` table pattern.

**Existing InteractionEventModel column block** (`db/models.py` lines 68–71):
```python
kc_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
correct: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
response_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
hint_used: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
```

**New column to add** (append after line 71):
```python
safety_flag: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
```

**New AlertModel** — follows `InteractionEventModel` structure (FK pattern from lines 57–62, `DateTime` default from line 66, `Optional` typing from line 65):
```python
class AlertModel(Base):
    """Parent alerts: frustration / sensitive-topic / new-interest (PARENT-04)."""
    __tablename__ = "alerts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    child_id: Mapped[str] = mapped_column(
        String, ForeignKey("child_profiles.id"), nullable=False, index=True
    )
    alert_type: Mapped[str] = mapped_column(String, nullable=False)  # 'frustrated'|'sensitive'|'new-interest'
    triggered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    snippet: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    kc_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(
        String, ForeignKey("sessions.id"), nullable=True
    )
```

**Import addition** — add `AlertModel` to the `from db.models import ...` lines in `db/crud.py`.

---

### `db/crud.py` (service, CRUD — new functions)

**Analog:** `db/crud.py` — `get_24hr_history()` (lines 200–218) for time-window query; `update_mastery_state()` (lines 258–277) for field-patch pattern; `get_child_by_id()` (lines 61–68) for single-row fetch.

**`get_24hr_history` query pattern** (`db/crud.py` lines 208–218) — copy for `get_alerts_for_child`:
```python
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

**`update_mastery_state` field-patch pattern** (`db/crud.py` lines 258–277) — copy for `update_child_profile`:
```python
model = await session.get(MasteryStateModel, (child_id, kc_id))
if model is None:
    raise ValueError(...)
for k, v in fields.items():
    setattr(model, k, v)
model.updated_at = datetime.now(timezone.utc)
await session.commit()
```

**New `get_all_mastery_for_child`** — follows `get_session_history` (lines 180–197) select pattern:
```python
async def get_all_mastery_for_child(
    child_id: str, session: AsyncSession
) -> dict[str, MasteryStateModel]:
    """Return all MasteryState rows for child_id as {kc_id: row} dict."""
    result = await session.execute(
        select(MasteryStateModel).where(MasteryStateModel.child_id == child_id)
    )
    rows = list(result.scalars().all())
    return {r.kc_id: r for r in rows}
```

**New `get_alerts_for_child`** — copy `get_24hr_history` pattern with 30-day window:
```python
async def get_alerts_for_child(
    child_id: str, session: AsyncSession, days: int = 30
) -> list[AlertModel]:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    result = await session.execute(
        select(AlertModel)
        .where(AlertModel.child_id == child_id)
        .where(AlertModel.triggered_at >= since)
        .order_by(AlertModel.triggered_at.desc())
    )
    return list(result.scalars().all())
```

**New `create_alert`** — copy `create_session` pattern (lines 104–110):
```python
async def create_alert(
    child_id: str,
    alert_type: str,
    session: AsyncSession,
    *,
    snippet: Optional[str] = None,
    kc_id: Optional[str] = None,
    session_id: Optional[str] = None,
) -> AlertModel:
    model = AlertModel(
        id=str(uuid.uuid4()),
        child_id=child_id,
        alert_type=alert_type,
        snippet=snippet,
        kc_id=kc_id,
        session_id=session_id,
    )
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model
```

**New `update_child_profile`** — follows `update_mastery_state` pattern with `Optional` field-patch:
```python
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

**Frustration alert tally in `end_session()`** — add after existing BKT/interest extraction block in `api/sessions.py` lines 88–90; uses `func.count()` aggregation (from `tests/db/test_crud_mastery.py` line 11 `from sqlalchemy import func, select` pattern):
```python
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
for row in result.all():
    if row.hint_count > 3:
        await create_alert(
            child_id=session_row.child_id,
            alert_type="frustrated",
            kc_id=row.kc_id,
            session_id=session_id,
            db=db,
        )
```

---

### `config/settings.py` (config — add parent_password field)

**Analog:** `config/settings.py` lines 1–32 — add one field following the existing `BaseSettings` pattern.

**Existing Settings class** (`config/settings.py` lines 5–28):
```python
class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8000
    secret_key: str = "dev-secret-change-me"
    database_url: str = "sqlite+aiosqlite:///./data/etutor.db"
    ...
    class Config:
        env_file = "config/.env"
```

**New field to add** (after `secret_key` line):
```python
parent_password: str = "change-me-in-env"   # set PARENT_PASSWORD in config/.env
```

---

### `requirements.txt` (config — add itsdangerous)

**Analog:** `requirements.txt` — existing entries use `>=` version pinning.

Add one line:
```
itsdangerous>=2.1.2
```

This is a Wave 0 blocker — `SessionMiddleware` import fails without it.

---

### `web/parent/templates/login.html` (component, request-response — new)

**Analog:** `web/parent/templates/dashboard.html` (lines 1–91) — CSS variables, header pattern, white-card aesthetic.

**CSS variables to carry forward** (`dashboard.html` lines 7–45):
```css
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, sans-serif; background: #f8f8f8; color: #2c2c2c; }
header {
  background: white; border-bottom: 1px solid #e0e0e0;
  padding: 1rem 2rem; display: flex; align-items: center; gap: 1rem;
}
/* Card pattern: */
background: white; border: 1px solid #e0e0e0; border-radius: 12px; padding: 1.25rem 1.5rem;
/* Green accent: #7a9e7e */
```

**Login form structure** (D-03: one password field, one submit, no username):
```html
<form method="POST" action="/parent/login">
  <label>Password: <input type="password" name="password" autofocus></label>
  <button type="submit">Sign In</button>
</form>
```

No error message on failure (D-04) — clean redirect back to login only.

---

### `web/parent/templates/dashboard.html` (component, request-response — extend)

**Analog:** `web/parent/templates/dashboard.html` lines 1–91 — extend in-place; do not rewrite.

**Existing white-card structure** (lines 47–91) is the base. Extensions needed:
- Add logout link in `<header>` (`<a href="/parent/logout">Sign out</a>`)
- Replace `children` div with linked cards pointing to `/parent/children/{child.id}`
- Add alert count badge to each child card
- Add "Recent Alerts" section linking to `/parent/alerts`

**Header link pattern** (`dashboard.html` line 16):
```html
<header a { color: #7a9e7e; text-decoration: none; font-size: 0.95rem; margin-left: auto; }
<a href="/child">Child view →</a>
```
Copy this pattern for the logout link.

---

### `web/parent/templates/child_profile.html` (component, CRUD — new)

**Analog:** `web/parent/templates/dashboard.html` `.child-card` pattern (lines 18–27) + RESEARCH.md Pattern 8 HTML form.

**Card CSS** (`dashboard.html` lines 19–27):
```css
.child-card {
  background: white; border: 1px solid #e0e0e0; border-radius: 12px;
  padding: 1.25rem 1.5rem; min-width: 200px; flex: 1;
}
```

**Profile form** (D-15, D-16, D-18 — from RESEARCH.md Pattern 8):
```html
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
  {% for flag in ["dyslexia", "adhd", "dyscalculia", "autism", "hyperlexia"] %}
  <label>
    <input type="checkbox" name="neurodivergence" value="{{ flag }}"
           {% if flag in (child.neurodivergence or []) %}checked{% endif %}>
    {{ flag }}
  </label>
  {% endfor %}
  <label>Interests: <input name="interests" value="{{ child.interests | join(', ') }}"></label>
  <button type="submit">Save</button>
</form>
```

**Mastery map accordion** — use native `<details>/<summary>` (RESEARCH.md Pitfall 6). Colour mapping from RESEARCH.md Code Examples:
```html
{% set bucket_color = {
  "not_started": "#b0b0b0",
  "fragile": "#e6a817",
  "in_progress": "#4a90d9",
  "solid": "#7a9e7e"
} %}
{% for subject, topics in subjects %}
<details>
  <summary>{{ subject }} ({{ topics | length }} topics)</summary>
  {% for topic in topics %}
  <div class="topic-row">
    <span class="mastery-dot" style="background: {{ bucket_color[topic.bucket] }};
      width: 10px; height: 10px; border-radius: 50%; display: inline-block;"></span>
    {{ topic.name }}
    <span class="last-studied">{{ topic.last_studied.strftime('%Y-%m-%d') if topic.last_studied else 'never' }}</span>
  </div>
  {% endfor %}
</details>
{% endfor %}
```

---

### `web/parent/templates/session_replay.html` (component, request-response — new)

**Analog:** `web/parent/templates/dashboard.html` `.turn` pattern (lines 38–44).

**Turn CSS and structure** (`dashboard.html` lines 38–44):
```css
.turn { padding: 0.75rem 1.25rem; border-bottom: 1px solid #f0f0f0; }
.turn:last-child { border-bottom: none; }
.turn .q { font-weight: 500; margin-bottom: 0.25rem; }
.turn .q::before { content: "Q: "; color: #888; }
.turn .a { color: #444; font-size: 0.95rem; }
.turn .a::before { content: "A: "; color: #7a9e7e; font-weight: 600; }
```

**Jinja2 turn loop** (`dashboard.html` lines 76–81):
```html
{% for turn in turns %}
<div class="turn">
  <div class="q">{{ turn.question }}</div>
  <div class="a">{{ turn.answer }}</div>
</div>
{% endfor %}
```

---

### `web/parent/templates/alert_feed.html` (component, request-response — new)

**Analog:** `web/parent/templates/dashboard.html` `.session-list` / `.session-header` pattern (lines 26–37).

**Alert row structure** (D-13 format — timestamp / child name / badge / snippet):
```html
<div class="alert-row">
  <span class="alert-time">{{ alert.triggered_at.strftime('%Y-%m-%d %H:%M') }}</span>
  <span class="alert-badge badge-{{ alert.alert_type }}">{{ alert.alert_type }}</span>
  {% if alert.snippet %}<span class="alert-snippet">{{ alert.snippet }}</span>{% endif %}
</div>
```

Badge colours follow D-08 palette: `frustrated` = amber `#e6a817`, `sensitive` = red `#cc4444`, `new-interest` = blue `#4a90d9`.

---

### `tests/api/test_parent_auth.py` (test, request-response — new)

**Analog:** `tests/api/test_session_end.py` lines 1–145 — complete fixture + test structure.

**Fixture pattern** (`test_session_end.py` lines 29–83):
```python
@pytest_asyncio.fixture
async def mem_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

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

**Session cookie test pattern** (RESEARCH.md Pattern 9) — `httpx.AsyncClient` preserves cookies:
```python
async def test_protected_route_without_cookie_redirects(test_client):
    response = await test_client.get("/parent", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/parent/login" in response.headers["location"]

async def test_login_sets_cookie_and_redirects(test_client):
    response = await test_client.post(
        "/parent/login",
        data={"password": "test-password"},
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)
    assert "session" in response.cookies

async def test_authenticated_access_succeeds(test_client):
    await test_client.post("/parent/login", data={"password": "test-password"})
    response = await test_client.get("/parent")
    assert response.status_code == 200
```

**`PARENT_PASSWORD` env control** (`get_settings()` is `@lru_cache` — `config/settings.py` line 30): Call `get_settings.cache_clear()` in teardown, or set `PARENT_PASSWORD=test-password` in `config/.env` before test run.

---

### `tests/db/test_crud_parent.py` (test, CRUD — new)

**Analog:** `tests/db/test_crud_profiles.py` lines 1–89 — `db_session` fixture usage, `create_child` setup, assert-after-commit pattern.

**Fixture import pattern** (`test_crud_profiles.py` lines 1–13):
```python
import pytest
from db.crud import (
    create_child,
    get_child_by_id,
    ...
)
```

**Assert-after-commit pattern** (`test_crud_profiles.py` lines 22–36):
```python
async def test_create_and_get_by_id(db_session):
    child = await create_child(db_session, id="child-001", name="Alice", age=8)
    assert child.id == "child-001"
    fetched = await get_child_by_id("child-001", db_session)
    assert fetched is not None
    assert fetched.name == "Alice"
```

**Test for update_child_profile** — copy `test_update_interests_merges` structure (lines 73–88):
```python
async def test_update_child_profile_name(db_session):
    await create_child(db_session, id="child-p1", name="Alice", age=8)
    updated = await update_child_profile("child-p1", db_session, name="Alicia")
    assert updated is not None
    assert updated.name == "Alicia"
    fetched = await get_child_by_id("child-p1", db_session)
    assert fetched.name == "Alicia"
```

**Test for frustration alert** — needs `create_child` + `create_session` + `InteractionEventModel` rows with `hint_used=True`:
```python
async def test_frustration_alert_created(db_session):
    # Insert 4 hint_used=True events on the same kc_id in one session
    # Call the tally function / end_session
    # Assert AlertModel row with alert_type="frustrated" exists
    ...
```

---

### Alembic migration (`migrations/versions/XXXX_phase4_parent.py`) (migration, CRUD — new)

**Analog:** `migrations/versions/d8909e3e5f75_add_child_fsrs_params.py` lines 1–42 — complete migration file structure.

**Migration file header pattern** (lines 1–17):
```python
"""phase4 parent dashboard — safety_flag + alerts table

Revision ID: XXXX
Revises: d8909e3e5f75
Create Date: 2026-07-18 ...
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'XXXX'
down_revision: Union[str, Sequence[str], None] = 'd8909e3e5f75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
```

**Column addition pattern** — use `op.add_column`:
```python
def upgrade() -> None:
    op.add_column('interaction_events',
        sa.Column('safety_flag', sa.Boolean(), nullable=True)
    )
    op.create_table('alerts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('child_id', sa.String(), nullable=False),
        sa.Column('alert_type', sa.String(), nullable=False),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('snippet', sa.String(), nullable=True),
        sa.Column('kc_id', sa.String(), nullable=True),
        sa.Column('session_id', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['child_id'], ['child_profiles.id']),
        sa.ForeignKeyConstraint(['session_id'], ['sessions.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_child_id'), 'alerts', ['child_id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_alerts_child_id'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_column('interaction_events', 'safety_flag')
```

---

## Shared Patterns

### Authentication (SessionMiddleware + require_parent_auth)
**Source:** RESEARCH.md Patterns 1–2 (no existing project analog — new in Phase 4)
**Apply to:** All `api/parent.py` routes except `/parent/login` and `/parent/logout`
```python
# In api/parent.py — dependency function (stateless, no DB needed)
def require_parent_auth(request: Request):
    if not request.session.get("parent_authenticated"):
        raise RedirectResponse(url="/parent/login", status_code=303)

# On every protected route:
_: None = Depends(require_parent_auth)
```

### DB Session Dependency
**Source:** `api/parent.py` line 16, `api/child.py` line 16, `api/sessions.py` line 19
**Apply to:** All `api/parent.py` routes that query the DB
```python
session: AsyncSession = Depends(get_db)
```

### Datetime Convention
**Source:** `db/models.py` line 66, `db/crud.py` line 275
**Apply to:** `AlertModel.triggered_at` default, any `datetime.now()` call in Phase 4 code
```python
# Always:
datetime.now(timezone.utc)
# Never:
datetime.utcnow()
```

### Optional Typing
**Source:** `db/crud.py` lines 144–153 (function signature)
**Apply to:** All new function signatures in `db/crud.py` and `api/parent.py`
```python
from typing import Optional
# Use: Optional[str]  NOT: str | None
```

### SQLAlchemy ORM WHERE
**Source:** `db/crud.py` lines 65–67, 210–217
**Apply to:** All new queries in `db/crud.py`
```python
# Correct (parameterised):
select(AlertModel).where(AlertModel.child_id == child_id)
# Never: string interpolation in WHERE clauses
```

### Test In-Memory Engine
**Source:** `tests/api/test_session_end.py` lines 29–83, `tests/conftest.py` lines 17–26
**Apply to:** `tests/api/test_parent_auth.py`, `tests/db/test_crud_parent.py`
```python
engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)
```

### Jinja2 HTMLResponse Return
**Source:** `api/parent.py` lines 20–23, `api/child.py` lines 18–19
**Apply to:** All GET routes in `api/parent.py` that render templates
```python
return templates.TemplateResponse(
    "template_name.html",
    {"request": request, **context_vars},
)
```

### hmac.compare_digest for passphrase
**Source:** RESEARCH.md Pattern 2 (stdlib — no project analog needed)
**Apply to:** `api/parent.py` `do_login()` handler
```python
import hmac
if hmac.compare_digest(password, settings.parent_password):
    ...
```

---

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `web/parent/templates/login.html` | component | request-response | Closest is `dashboard.html` for CSS only; login form pattern is new to this project |

(All other files have direct analogs in the codebase.)

---

## Metadata

**Analog search scope:** `api/`, `db/`, `config/`, `web/`, `tests/`, `migrations/`
**Files scanned:** 16 source files read directly
**Key constraints confirmed in codebase:**
- `hint_used` is `Boolean` nullable (not int) — D-10 requires `func.count()` aggregation
- `itsdangerous` is NOT installed — Wave 0 blocker before any SessionMiddleware code
- `get_settings()` is `@lru_cache` — tests must `get_settings.cache_clear()` or set env before first call
- `secret_key` already exists in `Settings` — no new config needed for SessionMiddleware signing
- `api/chat.py` already calls `get_child_by_id` per-request — D-17 is already satisfied
- `MasteryStateModel.updated_at` serves as `last_studied` proxy — no dedicated column needed
- Device-facing `/v1/sessions/*` must NOT get `require_parent_auth` — breaks device sync (Pitfall 5)
**Pattern extraction date:** 2026-07-18
