from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.profiles import list_children
from services.sessions import get_all_sessions

router = APIRouter()
templates = Jinja2Templates(directory="web/parent/templates")


@router.get("/", response_class=HTMLResponse)
async def parent_dashboard(request: Request):
    children = await list_children()
    sessions = await get_all_sessions()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "children": children, "sessions": sessions},
    )
