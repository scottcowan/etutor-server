"""
Integration tests: GET /v1/sessions/{session_id}/turns endpoint (HIST-03).

Tests:
  1. 200 response with session_id and turns list scoped to the session
  2. turns contain the expected child_id

Uses httpx AsyncClient + FastAPI dependency_overrides pattern from test_session_end.py.
asyncio_mode = auto is inherited from pytest.ini.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.main import app
from db.models import Base
from db.crud import create_child, create_session, log_turn
from db.session import get_db


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture
async def mem_engine():
    """In-memory SQLite engine with all tables created."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def mem_session(mem_engine):
    """A single AsyncSession for the test lifetime (used for assertions)."""
    factory = async_sessionmaker(mem_engine, expire_on_commit=False)
    async with factory() as session:
        yield session


@pytest_asyncio.fixture
async def test_data(mem_session):
    """Insert a child profile, a session row, and 2 turns. Return (child_id, session_id)."""
    child = await create_child(
        mem_session,
        id="child-turns-01",
        name="TurnsKid",
        age=9,
        device_id="device-turns-01",
        interests=["volcanoes"],
        reading_level="grade 4",
    )
    session_row = await create_session(child.id, mem_session)
    # Log 2 turns under this session
    await log_turn(
        child.id,
        "What is a volcano?",
        "A volcano is a mountain that erupts magma.",
        mem_session,
        session_id=session_row.id,
        topic="volcanoes",
    )
    await log_turn(
        child.id,
        "What is magma?",
        "Magma is molten rock under the earth's crust.",
        mem_session,
        session_id=session_row.id,
        topic="volcanoes",
    )
    return child.id, session_row.id


@pytest_asyncio.fixture
async def test_client(mem_engine, test_data):
    """
    FastAPI TestClient with get_db overridden to use the in-memory engine.
    """
    factory = async_sessionmaker(mem_engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_get_session_turns_200(test_client, test_data):
    """GET /v1/sessions/{session_id}/turns returns 200 with session_id and turns list."""
    child_id, session_id = test_data
    response = await test_client.get(f"/v1/sessions/{session_id}/turns")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    body = response.json()
    assert "session_id" in body
    assert "turns" in body
    assert len(body["turns"]) == 2
    assert body["turns"][0]["child_id"] == child_id
