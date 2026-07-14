from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from services.profiles import list_children

router = APIRouter()
templates = Jinja2Templates(directory="web/parent/templates")


@router.get("/", response_class=HTMLResponse)
async def parent_dashboard(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    children = await list_children(session)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "children": children, "sessions": {}},
    )
