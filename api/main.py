from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from api import stt, chat, sync, sessions, dashboard
from api.child import router as child_router
from api.parent import router as parent_router

app = FastAPI(title="eTutor Server", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# OpenAI-compatible endpoints (device-facing)
app.include_router(stt.router, prefix="/v1")
app.include_router(chat.router, prefix="/v1")
app.include_router(sync.router, prefix="/v1")
app.include_router(sessions.router, prefix="/v1")
app.include_router(dashboard.router, prefix="/v1")

# Web interfaces
app.include_router(child_router, prefix="/child")
app.include_router(parent_router, prefix="/parent")

app.mount("/static", StaticFiles(directory="web/static"), name="static")


@app.get("/health")
async def health():
    return {"status": "ok"}
