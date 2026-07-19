import hmac

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_settings
from db.session import get_db
from services.profiles import list_children

router = APIRouter()
templates = Jinja2Templates(directory="web/parent/templates")


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
    children = await list_children(session)
    sessions = {}  # Phase 1: session replay deferred to Phase 4
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {"children": children, "sessions": sessions},
    )
