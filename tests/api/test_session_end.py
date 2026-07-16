"""
Integration tests: POST /v1/sessions/{session_id}/end endpoint (KT-04).

Tests:
  1. 200 response with session_id, ended_at, kcs_updated fields
  2. sessions.ended_at is set in DB after 200
  3. 404 when session_id does not exist
  4. 409 when session is already ended (second call)

Uses httpx AsyncClient + FastAPI dependency_overrides pattern from test_chat_db_wiring.py.
asyncio_mode = auto is inherited from pytest.ini.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.main import app
from db.models import Base, ChildProfileModel, SessionModel
from db.crud import create_child, create_session
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
    """Insert a child profile and a session row, return (child_id, session_id)."""
    child = await create_child(
        mem_session,
        id="child-test-01",
        name="TestKid",
        age=8,
        device_id="device-test-01",
        interests=["maths"],
        reading_level="grade 3",
    )
    session_row = await create_session(child.id, mem_session)
    return child.id, session_row.id


@pytest_asyncio.fixture
async def test_client(mem_engine, test_data):
    """
    FastAPI TestClient with get_db overridden to use the in-memory engine.

    A fresh session is yielded per-request — the same mem_engine is used,
    so rows written in the route handler are visible to assertion queries
    using a separate session on the same engine.
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

async def test_session_end_200(test_client, test_data):
    """POST /v1/sessions/{id}/end returns 200 with session_id, ended_at, kcs_updated."""
    child_id, session_id = test_data
    response = await test_client.post(f"/v1/sessions/{session_id}/end")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    body = response.json()
    assert "session_id" in body, "Response must contain session_id"
    assert "ended_at" in body, "Response must contain ended_at"
    assert "kcs_updated" in body, "Response must contain kcs_updated"
    assert body["session_id"] == session_id
    assert body["kcs_updated"] >= 0


async def test_session_end_sets_ended_at(test_client, test_data, mem_engine):
    """After POST, sessions.ended_at is set in DB."""
    child_id, session_id = test_data
    await test_client.post(f"/v1/sessions/{session_id}/end")

    factory = async_sessionmaker(mem_engine, expire_on_commit=False)
    async with factory() as session:
        result = await session.execute(
            select(SessionModel).where(SessionModel.id == session_id)
        )
        row = result.scalar_one_or_none()

    assert row is not None, "Session row must exist after endpoint call"
    assert row.ended_at is not None, "sessions.ended_at must be set after endpoint call"


async def test_session_end_404(test_client):
    """POST with unknown session_id returns 404."""
    response = await test_client.post("/v1/sessions/nonexistent-session-id/end")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


async def test_session_end_409(test_client, test_data):
    """POST twice on the same session returns 409 on the second call."""
    child_id, session_id = test_data
    first = await test_client.post(f"/v1/sessions/{session_id}/end")
    assert first.status_code == 200
    second = await test_client.post(f"/v1/sessions/{session_id}/end")
    assert second.status_code == 409
    assert "already ended" in second.json()["detail"].lower()
