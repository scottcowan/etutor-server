import hmac

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from db.session import get_db
from db.crud import (
    get_alerts_for_child,
    get_all_mastery_for_child,
    get_child_by_id,
    get_turns_by_session_id,
    list_children,
    list_sessions_for_child,
    update_child_profile,
    get_session,
)
from services.curriculum import CURRICULUM
from services.knowledge_tracing import _mastery_bucket

router = APIRouter()
templates = Jinja2Templates(directory="web/parent/templates")

# Allowed reading_level values — server validation (T-4-03-05)
_VALID_READING_LEVELS = {"beginner", "developing", "fluent"}


class ParentAuthRequired(Exception):
    """Raised by require_parent_auth when no valid session cookie is present (D-05).

    api/main.py registers an exception handler that returns a 303 redirect to
    /parent/login — keeping the dependency itself free of response-construction
    logic and making it testable without a live HTTP response cycle.
    """


def require_parent_auth(request: Request) -> None:
    """Dependency: raise ParentAuthRequired if session cookie is not set (D-05)."""
    if not request.session.get("parent_authenticated"):
        raise ParentAuthRequired()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """GET /parent/login — render passphrase login form (D-03)."""
    return templates.TemplateResponse(request, "login.html")


@router.post("/login", response_class=RedirectResponse)
async def do_login(request: Request):
    """POST /parent/login — constant-time passphrase check (T-4-01-01).

    On success: set session flag and redirect to /parent.
    On failure: redirect back to /parent/login with no error message (D-04).
    """
    form = await request.form()
    password = form.get("password", "")
    settings = get_settings()
    if hmac.compare_digest(str(password), settings.parent_password):
        request.session["parent_authenticated"] = True
        return RedirectResponse(url="/parent", status_code=303)
    return RedirectResponse(url="/parent/login", status_code=303)


@router.post("/logout", response_class=RedirectResponse)
async def do_logout(request: Request):
    """POST /parent/logout — clear session and redirect to login."""
    request.session.clear()
    return RedirectResponse(url="/parent/login", status_code=303)


@router.get("/", response_class=HTMLResponse)
async def parent_dashboard(
    request: Request,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_parent_auth),
):
    """GET /parent — authenticated dashboard: child cards, recent alerts, recent sessions."""
    children = await list_children(session)

    # v1 single-child: get first child's alerts and sessions
    recent_alerts = []
    recent_sessions = []
    if children:
        child = children[0]
        recent_alerts = await get_alerts_for_child(child.id, session, days=30)
        recent_sessions = await list_sessions_for_child(child.id, session, limit=5)

    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "children": children,
            "recent_alerts": recent_alerts,
            "recent_sessions": recent_sessions,
        },
    )


@router.get("/sessions/{session_id}", response_class=HTMLResponse)
async def session_replay(
    session_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_parent_auth),
):
    """GET /parent/sessions/{session_id} — turn-by-turn session replay (PARENT-01)."""
    session_obj = await get_session(session_id, session)
    if session_obj is None:
        return HTMLResponse(
            "Session not found. It may have been deleted or the link is invalid.",
            status_code=404,
        )
    turns = await get_turns_by_session_id(session_id, session)
    return templates.TemplateResponse(
        request,
        "session_replay.html",
        {"session_obj": session_obj, "turns": turns},
    )


@router.get("/children/{child_id}", response_class=HTMLResponse)
async def child_profile_get(
    child_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_parent_auth),
):
    """GET /parent/children/{child_id} — mastery map accordion + profile editor (PARENT-02)."""
    child = await get_child_by_id(child_id, session)
    if child is None:
        return HTMLResponse("Child not found.", status_code=404)

    mastery_by_kc = await get_all_mastery_for_child(child_id, session)

    # Build subjects dict grouped from CURRICULUM
    subjects: dict[str, list] = {}
    for topic in CURRICULUM:
        row = mastery_by_kc.get(topic.id)
        bucket = _mastery_bucket(row.p_mastery if row else None)
        last_studied = row.updated_at if row else None
        subjects.setdefault(topic.subject, []).append({
            "name": topic.name,
            "bucket": bucket,
            "last_studied": last_studied,
        })

    subjects_sorted = sorted(subjects.items())

    return templates.TemplateResponse(
        request,
        "child_profile.html",
        {"child": child, "subjects_sorted": subjects_sorted},
    )


@router.post("/children/{child_id}", response_class=RedirectResponse)
async def child_profile_post(
    child_id: str,
    request: Request,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_parent_auth),
):
    """POST /parent/children/{child_id} — update profile and redirect (PARENT-03)."""
    form = await request.form()
    name = form.get("name") or None
    age_raw = form.get("age")
    age = int(age_raw) if age_raw else None
    reading_level_raw = form.get("reading_level") or None
    # T-4-03-05: server-validate reading_level; silently ignore invalid values
    reading_level = reading_level_raw if reading_level_raw in _VALID_READING_LEVELS else None
    neurodivergence = list(form.getlist("neurodivergence"))
    interests_raw = form.get("interests", "")
    interests = [i.strip() for i in interests_raw.split(",") if i.strip()] or None

    await update_child_profile(
        child_id,
        session,
        name=name,
        age=age,
        reading_level=reading_level,
        neurodivergence=neurodivergence if neurodivergence else None,
        interests=interests,
    )
    return RedirectResponse(url=f"/parent/children/{child_id}", status_code=303)


@router.get("/alerts", response_class=HTMLResponse)
async def alert_feed(
    request: Request,
    session: AsyncSession = Depends(get_db),
    _: None = Depends(require_parent_auth),
):
    """GET /parent/alerts — chronological alert feed last 30 days (PARENT-04)."""
    children = await list_children(session)
    # v1 single-child: fetch first child's alerts
    alerts = []
    child = None
    if children:
        child = children[0]
        alerts = await get_alerts_for_child(child.id, session, days=30)

    return templates.TemplateResponse(
        request,
        "alert_feed.html",
        {"alerts": alerts, "child": child},
    )
