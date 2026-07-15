from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware

from api import stt, chat, sync, sessions, dashboard
from api.child import router as child_router
from api.parent import router as parent_router
from config.settings import get_settings
from db.models import Base
from db.seeds import seed_dev_data
from db.session import AsyncSessionLocal, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure data/ directory exists before SQLite tries to create the file
    Path("data").mkdir(exist_ok=True)
    # Create tables that don't exist (Alembic handles schema evolution;
    # create_all is a startup safety net so dev server works without running alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    # Seed dev profiles — idempotent upserts; skipped in production (D-06)
    settings = get_settings()
    if getattr(settings, "env", "dev") != "production":
        async with AsyncSessionLocal() as session:
            await seed_dev_data(session)
    yield
    # Shutdown: no cleanup needed for SQLite; dispose engine on exit
    await engine.dispose()


app = FastAPI(title="eTutor Server", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://127.0.0.1"],  # tighten per deployment
    allow_methods=["POST", "GET"],
    allow_headers=["X-Child-ID", "X-Device-ID", "Content-Type"],
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
