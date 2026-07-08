from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from services.profiles import list_children

router = APIRouter()
templates = Jinja2Templates(directory="web/child/templates")


@router.get("/", response_class=HTMLResponse)
async def child_home(request: Request):
    children = await list_children()
    return templates.TemplateResponse("home.html", {"request": request, "children": children})


@router.get("/{child_id}", response_class=HTMLResponse)
async def child_chat(request: Request, child_id: str):
    from services.profiles import get_child_by_id
    child = await get_child_by_id(child_id)
    if not child:
        return HTMLResponse("Child not found", status_code=404)
    return templates.TemplateResponse("chat.html", {"request": request, "child": child})
