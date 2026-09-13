"""
Unit tests for build_system_prompt() mastery_context extension (KT-05).

Tests verify:
  - No mastery_context (None) → "Focus topics" NOT in result (backward-compatible)
  - mastery_context=[] → "Focus topics" NOT in result (empty list = no-op)
  - mastery_context with fragile bucket → correct label in prompt
  - mastery_context with in_progress bucket → correct label in prompt
  - mastery_context with not_started bucket → correct label in prompt

No DB fixture needed — build_system_prompt() is pure async function taking a child object.
asyncio_mode=auto (from pytest.ini), so no @pytest.mark.asyncio decorator needed.
"""
import types

import pytest

from services.tutor import build_system_prompt


def _make_child(**kwargs):
    """Create a minimal child-like namespace for testing build_system_prompt()."""
    defaults = {
        "name": "TestChild",
        "age": 9,
        "interests": ["space"],
        "reading_level": "grade-4",
        "current_topic": "planets",
        "current_books": [],
        "neurodivergence": [],
    }
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


async def test_system_prompt_no_mastery_context():
    """build_system_prompt(child) with no mastery_context — "Focus topics" must NOT appear."""
    child = _make_child()
    result = await build_system_prompt(child)
    assert "Focus topics" not in result


async def test_system_prompt_none_mastery_context():
    """build_system_prompt(child, mastery_context=None) — "Focus topics" must NOT appear."""
    child = _make_child()
    result = await build_system_prompt(child, mastery_context=None)
    assert "Focus topics" not in result


async def test_system_prompt_empty_mastery_context():
    """build_system_prompt(child, mastery_context=[]) — empty list treated same as None."""
    child = _make_child()
    result = await build_system_prompt(child, mastery_context=[])
    assert "Focus topics" not in result


async def test_system_prompt_with_mastery_context_fragile():
    """fragile bucket → 'fragile — needs reinforcement' label in prompt."""
    child = _make_child()
    mastery_context = [{"name": "Fractions", "bucket": "fragile"}]
    result = await build_system_prompt(child, mastery_context=mastery_context)
    assert "Focus topics this session:" in result
    assert "fragile — needs reinforcement" in result
    assert "Fractions" in result


async def test_system_prompt_with_mastery_context_in_progress():
    """in_progress bucket → 'due for review' label in prompt."""
    child = _make_child()
    mastery_context = [{"name": "Long Division", "bucket": "in_progress"}]
    result = await build_system_prompt(child, mastery_context=mastery_context)
    assert "Focus topics this session:" in result
    assert "due for review" in result
    assert "Long Division" in result


async def test_system_prompt_with_mastery_context_not_started():
    """not_started bucket → 'not yet started — prerequisites met' label in prompt."""
    child = _make_child()
    mastery_context = [{"name": "Algebra Basics", "bucket": "not_started"}]
    result = await build_system_prompt(child, mastery_context=mastery_context)
    assert "Focus topics this session:" in result
    assert "not yet started" in result
    assert "Algebra Basics" in result


# ---------------------------------------------------------------------------
# Phase 3 new params: history_context, prereq_tree, session_prereq_state
# ---------------------------------------------------------------------------

async def test_system_prompt_with_history_context():
    """history_context list → 'Recent topics: X, Y' block in prompt."""
    child = _make_child()
    result = await build_system_prompt(child, history_context=["volcanoes", "plate tectonics"])
    assert "Recent topics: volcanoes, plate tectonics" in result


async def test_system_prompt_with_prereq_tree():
    """prereq_tree list → prereq names and unlock names in prompt."""
    child = _make_child()
    result = await build_system_prompt(
        child,
        prereq_tree=[{"prereq_name": "Rock Types", "prereq_kc_id": "rocks_soils", "unlocks": ["Volcanoes", "Plate Tectonics"]}],
    )
    assert "Rock Types" in result
    assert "Volcanoes" in result


async def test_system_prompt_prereq_escalation_turn1():
    """D-07: Turn 1 session_prereq_state → engage/hint instruction in prompt."""
    child = _make_child()
    prereq_entry = {"prereq_name": "Rock Types", "prereq_kc_id": "rocks_soils", "unlocks": ["Volcanoes"]}
    state_turn1 = {"rocks_soils": 1}
    result = await build_system_prompt(child, prereq_tree=[prereq_entry], session_prereq_state=state_turn1)
    assert "Turn 1" in result or "engage" in result


async def test_system_prompt_prereq_escalation_turn3():
    """D-07: Turn 3+ session_prereq_state → active steer instruction in prompt."""
    child = _make_child()
    prereq_entry = {"prereq_name": "Rock Types", "prereq_kc_id": "rocks_soils", "unlocks": ["Volcanoes"]}
    state_turn3 = {"rocks_soils": 3}
    result = await build_system_prompt(child, prereq_tree=[prereq_entry], session_prereq_state=state_turn3)
    assert "Turn 3" in result or "steer" in result


async def test_system_prompt_backward_compat_no_new_params():
    """build_system_prompt(child) with no new params — does not crash, no history section."""
    child = _make_child()
    result = await build_system_prompt(child)
    assert isinstance(result, str)
    assert len(result) > 0
    assert "Recent topics" not in result
