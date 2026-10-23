"""Tests — Autonomy Levels."""

from backend.agents.autonomy import AutonomyLevel


def test_autonomy_levels_count():
    """There must be exactly 6 autonomy levels (0–5)."""
    assert len(AutonomyLevel) == 6


def test_autonomy_level_values():
    assert AutonomyLevel.LEVEL_0 == 0
    assert AutonomyLevel.LEVEL_1 == 1
    assert AutonomyLevel.LEVEL_2 == 2
    assert AutonomyLevel.LEVEL_3 == 3
    assert AutonomyLevel.LEVEL_4 == 4
    assert AutonomyLevel.LEVEL_5 == 5


def test_autonomy_level_ordering():
    assert AutonomyLevel.LEVEL_0 < AutonomyLevel.LEVEL_1
    assert AutonomyLevel.LEVEL_2 < AutonomyLevel.LEVEL_3
    assert AutonomyLevel.LEVEL_5 > AutonomyLevel.LEVEL_4


def test_allows_autonomous_execution():
    """Levels 0-2 require per-action approval; levels 3-5 allow autonomous execution."""
    assert not AutonomyLevel.LEVEL_0.allows_autonomous_execution
    assert not AutonomyLevel.LEVEL_1.allows_autonomous_execution
    assert not AutonomyLevel.LEVEL_2.allows_autonomous_execution
    assert AutonomyLevel.LEVEL_3.allows_autonomous_execution
    assert AutonomyLevel.LEVEL_4.allows_autonomous_execution
    assert AutonomyLevel.LEVEL_5.allows_autonomous_execution


def test_requires_per_action_approval():
    assert AutonomyLevel.LEVEL_0.requires_per_action_approval
    assert AutonomyLevel.LEVEL_1.requires_per_action_approval
    assert AutonomyLevel.LEVEL_2.requires_per_action_approval
    assert not AutonomyLevel.LEVEL_3.requires_per_action_approval
    assert not AutonomyLevel.LEVEL_4.requires_per_action_approval
    assert not AutonomyLevel.LEVEL_5.requires_per_action_approval


def test_autonomy_level_labels():
    """Every level must have a non-empty label."""
    for level in AutonomyLevel:
        assert level.label, f"AutonomyLevel.{level.name} has no label"


def test_autonomy_level_str():
    assert "LEVEL_0" in str(AutonomyLevel.LEVEL_0)
    assert "Human Only" in str(AutonomyLevel.LEVEL_0)
