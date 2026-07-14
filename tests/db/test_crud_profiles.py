"""
Tests for ChildProfile CRUD operations in db/crud.py (DB-02).

All tests use the in-memory SQLite db_session fixture from conftest.py — no live file needed.
"""
import pytest
from db.crud import (
    create_child,
    get_child_by_id,
    get_child_by_device_id,
    list_children,
    update_interests,
)


async def test_get_child_by_id_returns_none_for_unknown(db_session):
    """get_child_by_id returns None for an id not in the database."""
    result = await get_child_by_id("nonexistent", db_session)
    assert result is None


async def test_create_and_get_by_id(db_session):
    """create_child inserts a row; get_child_by_id retrieves it with matching fields."""
    child = await create_child(
        db_session,
        id="child-001",
        name="Alice",
        age=8,
    )
    assert child.id == "child-001"
    assert child.name == "Alice"
    assert child.age == 8

    fetched = await get_child_by_id("child-001", db_session)
    assert fetched is not None
    assert fetched.id == "child-001"
    assert fetched.name == "Alice"
    assert fetched.age == 8


async def test_get_by_device_id(db_session):
    """create with device_id; get_child_by_device_id returns the matching child."""
    await create_child(
        db_session,
        id="child-002",
        name="Bob",
        age=10,
        device_id="device-test",
    )
    result = await get_child_by_device_id("device-test", db_session)
    assert result is not None
    assert result.device_id == "device-test"
    assert result.name == "Bob"


async def test_get_by_device_id_returns_none_for_unknown(db_session):
    """get_child_by_device_id returns None for a device_id not in the database."""
    result = await get_child_by_device_id("no-such-device", db_session)
    assert result is None


async def test_list_children(db_session):
    """list_children returns all child rows."""
    await create_child(db_session, id="child-a", name="ChildA", age=7)
    await create_child(db_session, id="child-b", name="ChildB", age=9)

    children = await list_children(db_session)
    assert len(children) == 2
    ids = {c.id for c in children}
    assert ids == {"child-a", "child-b"}


async def test_update_interests_merges(db_session):
    """update_interests merges new interests with existing (set union, not replace)."""
    child = await create_child(
        db_session,
        id="child-merge",
        name="Merge",
        age=9,
        interests=["a"],
    )
    assert child.interests == ["a"]

    await update_interests("child-merge", ["b", "c"], db_session)

    updated = await get_child_by_id("child-merge", db_session)
    assert updated is not None
    assert set(updated.interests) == {"a", "b", "c"}
