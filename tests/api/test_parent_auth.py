"""
Integration tests: parent dashboard auth flow.

Tests:
  1. GET /parent without session cookie redirects to /parent/login
  2. GET /parent/login returns 200
  3. POST /parent/login with correct passphrase sets session cookie and redirects to /parent
  4. POST /parent/login with wrong passphrase redirects back to /parent/login (no error)
  5. POST /parent/logout clears session and redirects to /parent/login
  6. GET /parent after login returns 200 (dashboard)

Uses httpx AsyncClient + FastAPI dependency_overrides pattern from test_session_end.py.
asyncio_mode = auto is inherited from pytest.ini.
"""
import os
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from api.main import app
from config.settings import get_settings
from db.models import Base
from db.crud import create_child
from db.session import get_db

TEST_PASSWORD = "test-password-for-auth"


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
async def test_client(mem_engine):
    """
    FastAPI TestClient with:
    - get_db overridden to use the in-memory engine
    - PARENT_PASSWORD env var set to TEST_PASSWORD so auth tests are deterministic
    """
    # Set env var before clearing cache so Settings picks it up
    os.environ["PARENT_PASSWORD"] = TEST_PASSWORD
    get_settings.cache_clear()

    factory = async_sessionmaker(mem_engine, expire_on_commit=False)

    async def override_get_db():
        async with factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    # Seed a child profile so GET /parent doesn't 500 on missing data
    async with factory() as session:
        await create_child(
            session,
            id="child-auth-test",
            name="TestKid",
            age=9,
            device_id=None,
        )

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

    app.dependency_overrides.pop(get_db, None)
    # Restore clean settings state
    os.environ.pop("PARENT_PASSWORD", None)
    get_settings.cache_clear()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

async def test_protected_route_without_cookie_redirects(test_client):
    """GET /parent without a session cookie ultimately redirects to /parent/login (D-05).

    Note: FastAPI emits a 307 (trailing-slash normalisation) before the auth
    dependency runs.  We follow all redirects and assert the final landing page
    is the login form.
    """
    response = await test_client.get("/parent", follow_redirects=True)
    # After following all redirects the final page should be the login form
    assert response.status_code == 200
    assert "Passphrase" in response.text


async def test_login_page_returns_200(test_client):
    """GET /parent/login renders the login form without auth."""
    response = await test_client.get("/parent/login")
    assert response.status_code == 200
    assert "Passphrase" in response.text


async def test_login_sets_cookie_and_redirects(test_client):
    """POST /parent/login with correct passphrase sets session cookie and redirects to /parent."""
    response = await test_client.post(
        "/parent/login",
        data={"password": TEST_PASSWORD},
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)
    assert "session" in response.cookies


async def test_wrong_passphrase_redirects_no_error(test_client):
    """POST /parent/login with wrong passphrase redirects to /parent/login with no error (D-04)."""
    response = await test_client.post(
        "/parent/login",
        data={"password": "totally-wrong"},
        follow_redirects=False,
    )
    assert response.status_code in (302, 303)
    assert "/parent/login" in response.headers["location"]
    # No session cookie should be set on failed login
    assert "session" not in response.cookies


async def test_logout_clears_session(test_client):
    """POST /parent/logout clears session cookie and redirects to /parent/login."""
    # First login
    await test_client.post(
        "/parent/login",
        data={"password": TEST_PASSWORD},
        follow_redirects=False,
    )
    # Now logout
    response = await test_client.post("/parent/logout", follow_redirects=False)
    assert response.status_code in (302, 303)
    assert "/parent/login" in response.headers["location"]


async def test_authenticated_get_parent_returns_200(test_client):
    """GET /parent/ after successful login returns 200 dashboard page."""
    # Login first (follow_redirects so cookies are stored in the client)
    await test_client.post(
        "/parent/login",
        data={"password": TEST_PASSWORD},
        follow_redirects=True,
    )
    # Use /parent/ (with trailing slash) to avoid the 307 normalisation redirect;
    # cookies are preserved by the httpx AsyncClient session.
    response = await test_client.get("/parent/", follow_redirects=False)
    assert response.status_code == 200
