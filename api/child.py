from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db
from services.profiles import list_children, get_child_by_id

router = APIRouter()
templates = Jinja2Templates(directory="web/child/templates")


@router.get("/", response_class=HTMLResponse)
async def child_home(
    request: Request,
    session: AsyncSession = Depends(get_db),
):
    children = await list_children(session)
    return templates.TemplateResponse("home.html", {"request": request, "children": children})


@router.get("/{child_id}", response_class=HTMLResponse)
async def child_chat(
    request: Request,
    child_id: str,
    session: AsyncSession = Depends(get_db),
):
    child = await get_child_by_id(child_id, session)
    if not child:
        return HTMLResponse("Child not found", status_code=404)
    return templates.TemplateResponse("chat.html", {"request": request, "child": child})
