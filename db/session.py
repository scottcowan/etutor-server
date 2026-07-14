"""
Async SQLAlchemy session factory and FastAPI dependency for etutor-server.

Exports:
  - engine: AsyncEngine (module-level singleton)
  - AsyncSessionLocal: async_sessionmaker bound to engine
  - get_db: FastAPI dependency generator yielding AsyncSession per request
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from config.settings import get_settings

settings = get_settings()
engine = create_async_engine(settings.database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    """FastAPI dependency: yield an AsyncSession for the duration of a request."""
    async with AsyncSessionLocal() as session:
        yield session
