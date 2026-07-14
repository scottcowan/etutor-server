"""
Shared pytest fixtures for etutor-server tests.

db_session: async pytest-asyncio fixture providing a fresh in-memory SQLite
            AsyncSession with all ORM tables created via Base.metadata.create_all.
            Each test gets an isolated database — no cleanup required.

Note: asyncio_mode = auto is set in pytest.ini (not here) so all async test
functions and fixtures run automatically without @pytest.mark.asyncio decorators.
"""
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.models import Base


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Fresh in-memory SQLite database per test with all ORM tables created."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        yield session
    await engine.dispose()
