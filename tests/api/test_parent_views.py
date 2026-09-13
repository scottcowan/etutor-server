"""
Integration tests: parent dashboard view routes (04-03).

Tests:
  1. GET /parent without cookie → redirect to /parent/login
  2. GET /parent authenticated → 200
  3. GET /parent/sessions/{id} authenticated → 200 with turn Q text
  4. GET /parent/sessions/{id} without cookie → redirect
  5. GET /parent/children/{id} authenticated → 200 with child name
  6. POST /parent/children/{id} authenticated → 303 redirect + DB updated
  7. GET /parent/alerts authenticated → 200 with alert snippet
  8. GET /parent/alerts without cookie → redirect

Uses the same mem_engine + dependency_overrides + AsyncClient pattern
as tests/api/test_parent_auth.py.
asyncio_mode = auto inherited from pytest.ini.
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.main import app
from config.settings import get_settings
from db.models import Base
from db.crud import (
    create_child,
    create_session,
    log_turn,
    create_or_get_mastery_state,
    create_alert,
    get_child_by_id,
)
from db.session import get_db

TEST_PASSWORD = "test-password-for-views"


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
async def test_data(mem_engine):
    """Seed one child, one session, two turns, one mastery row, one alert."""
    factory = async_sessionmaker(mem_engine, expire_on_commit=False)
    async with factory() as session:
        child = await create_child(
            session,
            id="child-views-test",
            name="TestChild",
            age=9,
            reading_level="developing",
        )
        sess_row = await create_session(child.id, session)
        # Manually set ended_at so session appears as completed
        from datetime import datetime, timezone
        sess_row.ended_at = datetime.now(timezone.utc)
        await session.commit()

        turn1 = await log_turn(
            child.id,
            "What is gravity?",
            "Gravity is a force that pulls objects together.",
            session,
            session_id=sess_row.id,
        )
        turn2 = await log_turn(
            child.id,
            "Why do apples fall?",
            "Because of the gravitational pull of the Earth.",
            session,
            session_id=sess_row.id,
        )
        mastery = await create_or_get_mastery_state(child.id, "phonics_phase1", session)
        alert = await create_alert(
            child.id,
            "frustrated",
            session,
            snippet="Stuck on fractions again",
        )

    return {
        "child_id": child.id,
        "child_name": child.name,
        "session_id": sess_row.id,
        "turn1_question": turn1.question,
        "alert_snippet": alert.snippet,
    }


@pytest_asyncio.fixture
async def test_client(mem_engine, test_data):
    """
    FastAPI TestClient with:
    - get_db overridden to in-memory engine
    - PARENT_PASSWORD env var set so auth works
    """
    os.environ["PARENT_PASSWORD"] = TEST_PASSWORD
    get_settings.cache_clear()

    factory = async_sessionmaker(mem_engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client, test_data

    app.dependency_overrides.pop(get_db, None)
    os.environ.pop("PARENT_PASSWORD", None)
    get_settings.cache_clear()


async def _login(client):
    """Helper: POST /parent/login with the test password."""
    await client.post(
        "/parent/login",
        data={"password": TEST_PASSWORD},
        follow_redirects=True,
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_dashboard_unauthenticated_redirects(test_client):
    """GET /parent without cookie → 302/303 to /parent/login."""
    client, _ = test_client
    response = await client.get("/parent/", follow_redirects=False)
    # May be a 303 auth redirect or a 307 trailing-slash → follow to login
    response2 = await client.get("/parent/", follow_redirects=True)
    assert "Passphrase" in response2.text


async def test_dashboard_authenticated_returns_200(test_client):
    """GET /parent authenticated → 200 HTML dashboard."""
    client, _ = test_client
    await _login(client)
    response = await client.get("/parent/", follow_redirects=False)
    assert response.status_code == 200


async def test_session_replay_returns_turns(test_client):
    """GET /parent/sessions/{id} authenticated → 200 with Q text."""
    client, data = test_client
    await _login(client)
    response = await client.get(f"/parent/sessions/{data['session_id']}")
    assert response.status_code == 200
    assert data["turn1_question"] in response.text


async def test_session_replay_unauthenticated_redirects(test_client):
    """GET /parent/sessions/{id} without cookie → 302/303."""
    client, data = test_client
    response = await client.get(
        f"/parent/sessions/{data['session_id']}", follow_redirects=False
    )
    # Accept redirect or follow to login page
    if response.status_code in (200,):
        # Shouldn't see the session data without auth
        assert "Passphrase" in response.text
    else:
        assert response.status_code in (302, 303, 307)


async def test_child_profile_get_returns_200(test_client):
    """GET /parent/children/{id} authenticated → 200 with child name."""
    client, data = test_client
    await _login(client)
    response = await client.get(f"/parent/children/{data['child_id']}")
    assert response.status_code == 200
    assert data["child_name"] in response.text


async def test_child_profile_post_updates_and_redirects(test_client):
    """POST /parent/children/{id} → 303 redirect; DB row updated."""
    client, data = test_client
    await _login(client)
    response = await client.post(
        f"/parent/children/{data['child_id']}",
        data={
            "name": "UpdatedName",
            "age": "10",
            "reading_level": "fluent",
            "interests": "space, music",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303

    # Verify DB updated via GET
    get_response = await client.get(f"/parent/children/{data['child_id']}")
    assert "UpdatedName" in get_response.text


async def test_alert_feed_returns_200(test_client):
    """GET /parent/alerts authenticated → 200 with alert snippet."""
    client, data = test_client
    await _login(client)
    response = await client.get("/parent/alerts")
    assert response.status_code == 200
    assert data["alert_snippet"] in response.text


async def test_alert_feed_unauthenticated_redirects(test_client):
    """GET /parent/alerts without cookie → 302/303."""
    client, _ = test_client
    response = await client.get("/parent/alerts", follow_redirects=False)
    if response.status_code == 200:
        # If we followed redirects, should see login
        assert "Passphrase" in response.text
    else:
        assert response.status_code in (302, 303, 307)
