"""
Tests for seed_dev_data idempotency and correctness (D-06).

All tests use the in-memory SQLite db_session fixture from conftest.py.
"""
from sqlalchemy import func, select

from db.crud import get_child_by_id
from db.models import ChildProfileModel
from db.seeds import seed_dev_data


async def test_seed_is_idempotent(db_session):
    """Calling seed_dev_data twice leaves exactly 2 rows in child_profiles."""
    await seed_dev_data(db_session)
    await seed_dev_data(db_session)

    result = await db_session.execute(select(func.count()).select_from(ChildProfileModel))
    count = result.scalar_one()
    assert count == 2


async def test_seed_kida_profile(db_session):
    """After seed, child-kida profile name is KidA."""
    await seed_dev_data(db_session)
    child = await get_child_by_id("child-kida", db_session)
    assert child is not None
    assert child.name == "KidA"


async def test_seed_kidb_profile(db_session):
    """After seed, child-kidb profile name is KidB."""
    await seed_dev_data(db_session)
    child = await get_child_by_id("child-kidb", db_session)
    assert child is not None
    assert child.name == "KidB"
