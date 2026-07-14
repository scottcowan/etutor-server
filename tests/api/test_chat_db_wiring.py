"""
Integration test: api/chat.py DB wiring.

Verifies that a POST to /v1/chat/completions:
  1. Injects an AsyncSession via Depends(get_db)
  2. Calls create_session(child_id, session) — writes a row to sessions table
  3. Calls log_turn(..., session_id=...) — writes a row to interaction_events table

Uses httpx AsyncClient + FastAPI dependency_overrides to inject an in-memory
SQLite database. litellm.acompletion is patched to avoid real API calls.

asyncio_mode = auto is inherited from pytest.ini.
"""
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from api.main import app
from db.models import Base, ChildProfileModel, SessionModel, InteractionEventModel
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
async def child_kida(mem_session):
    """Insert a KidA child profile into the in-memory DB."""
    child = ChildProfileModel(
        id="child-kida",
        name="KidA",
        age=7,
        device_id="device-001",
        reading_level="grade 2",
        interests=["dinosaurs", "space"],
        neurodivergence=[],
        current_topic="prehistoric life",
        current_books=[],
        session_count=0,
    )
    mem_session.add(child)
    await mem_session.commit()
    return child


@pytest_asyncio.fixture
async def test_client(mem_engine, child_kida):
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

    # Clean up override after test
    app.dependency_overrides.pop(get_db, None)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_mock_response(content: str = "Great question about dinosaurs!"):
    """Build a mock that matches litellm's acompletion response shape."""
    mock_choice = MagicMock()
    mock_choice.message.content = content
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    return mock_resp


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_chat_creates_session_row(test_client, mem_engine):
    """POST /v1/chat/completions writes a row to the sessions table."""
    mock_resp = make_mock_response()

    with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_resp):
        response = await test_client.post(
            "/v1/chat/completions",
            json={
                "model": "etutor",
                "messages": [{"role": "user", "content": "Tell me about T-Rex"}],
            },
            headers={"X-Child-ID": "child-kida"},
        )

    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"

    # Verify sessions table has a row
    factory = async_sessionmaker(mem_engine, expire_on_commit=False)
    async with factory() as session:
        result = await session.execute(
            select(SessionModel).where(SessionModel.child_id == "child-kida")
        )
        rows = list(result.scalars().all())

    assert len(rows) >= 1, "Expected at least one session row after chat request"
    assert rows[0].child_id == "child-kida"
    assert rows[0].id is not None


async def test_chat_creates_interaction_event_row(test_client, mem_engine):
    """POST /v1/chat/completions writes a row to interaction_events with session_id set."""
    mock_resp = make_mock_response("A T-Rex had tiny arms but powerful jaws.")

    with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_resp):
        response = await test_client.post(
            "/v1/chat/completions",
            json={
                "model": "etutor",
                "messages": [{"role": "user", "content": "How big were T-Rex arms?"}],
            },
            headers={"X-Child-ID": "child-kida"},
        )

    assert response.status_code == 200

    factory = async_sessionmaker(mem_engine, expire_on_commit=False)
    async with factory() as session:
        event_result = await session.execute(
            select(InteractionEventModel).where(InteractionEventModel.child_id == "child-kida")
        )
        events = list(event_result.scalars().all())

    assert len(events) >= 1, "Expected at least one interaction_event row"
    event = events[0]
    assert event.child_id == "child-kida"
    assert event.session_id is not None, "session_id must be set on interaction_event"
    assert event.question == "How big were T-Rex arms?"


async def test_chat_missing_child_id_returns_400(test_client):
    """POST without X-Child-ID or X-Device-ID returns 400."""
    mock_resp = make_mock_response()

    with patch("litellm.acompletion", new_callable=AsyncMock, return_value=mock_resp):
        response = await test_client.post(
            "/v1/chat/completions",
            json={
                "model": "etutor",
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )

    assert response.status_code == 400
