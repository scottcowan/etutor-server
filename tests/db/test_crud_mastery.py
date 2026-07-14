"""
Tests for MasteryState CRUD functions (DB-05).

Covers:
  - create_or_get_mastery_state creates row with BKT defaults
  - create_or_get_mastery_state returns existing row on second call (no duplicate insert)
  - update_mastery_state updates a field and persists it
  - composite PK allows different kc_id values for same child_id
"""
from sqlalchemy import func, select

from db.crud import create_child, create_or_get_mastery_state, update_mastery_state
from db.models import MasteryStateModel


async def test_create_mastery_state(db_session):
    """create_or_get_mastery_state creates a row with BKT defaults."""
    await create_child(db_session, id="child-c1", name="Grace", age=9)
    ms = await create_or_get_mastery_state("child-c1", "kc-fractions", db_session)

    assert ms.child_id == "child-c1"
    assert ms.kc_id == "kc-fractions"
    assert ms.p_mastery == pytest.approx(0.1)
    assert ms.p_learn == pytest.approx(0.2)
    assert ms.p_slip == pytest.approx(0.1)
    assert ms.p_guess == pytest.approx(0.2)


async def test_get_existing_mastery_state(db_session):
    """Second call to create_or_get_mastery_state returns the same row; DB count stays at 1."""
    await create_child(db_session, id="child-c2", name="Hana", age=10)
    ms1 = await create_or_get_mastery_state("child-c2", "kc-decimals", db_session)
    ms2 = await create_or_get_mastery_state("child-c2", "kc-decimals", db_session)

    assert ms1.child_id == ms2.child_id
    assert ms1.kc_id == ms2.kc_id

    result = await db_session.execute(
        select(func.count()).select_from(MasteryStateModel).where(
            MasteryStateModel.child_id == "child-c2",
            MasteryStateModel.kc_id == "kc-decimals",
        )
    )
    count = result.scalar_one()
    assert count == 1


async def test_update_mastery_state(db_session):
    """update_mastery_state persists the new p_mastery value."""
    await create_child(db_session, id="child-c3", name="Ivan", age=11)
    await create_or_get_mastery_state("child-c3", "kc-geometry", db_session)

    await update_mastery_state("child-c3", "kc-geometry", db_session, p_mastery=0.8)

    # Re-fetch to confirm persistence
    ms = await create_or_get_mastery_state("child-c3", "kc-geometry", db_session)
    assert ms.p_mastery == pytest.approx(0.8)


async def test_mastery_state_composite_pk(db_session):
    """Composite PK allows two rows with same child_id but different kc_id."""
    await create_child(db_session, id="child-c4", name="Julia", age=8)
    await create_or_get_mastery_state("child-c4", "kc-1", db_session)
    await create_or_get_mastery_state("child-c4", "kc-2", db_session)

    result = await db_session.execute(
        select(func.count()).select_from(MasteryStateModel).where(
            MasteryStateModel.child_id == "child-c4"
        )
    )
    count = result.scalar_one()
    assert count == 2


# pytest.approx is used for float comparisons — import needed
import pytest
