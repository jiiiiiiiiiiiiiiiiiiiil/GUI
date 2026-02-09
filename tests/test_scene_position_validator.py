import pytest

from scene_position_validator import (
    validate_scene_position,
    ScenePositionError,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def scenes():
    return [
        {"id": 10, "number": 1},
        {"id": 20, "number": 2},
        {"id": 30, "number": 3},
    ]


@pytest.fixture
def milestones():
    return [
        {"id": 1, "name": "Milestone A", "scene_id": 10},  # Scene 1
        {"id": 2, "name": "Milestone B", "scene_id": 30},  # Scene 3
    ]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_valid_position_no_conflict(scenes, milestones):
    """
    1. Gültige Position (kein Konflikt)
    """
    result = validate_scene_position(
        attach_after_number=1,
        scenes=scenes,
        milestones=milestones,
        must_happen_before=[2],     # Milestone B liegt nach neuer Szene
        cant_happen_before=[1],     # Milestone A liegt vor neuer Szene
    )

    assert result is None


def test_must_happen_before_violation(scenes, milestones):
    """
    2. Verstoß gegen must happen before
    """
    with pytest.raises(
        ScenePositionError,
        match='Scene must happen before milestone "Milestone A"',
    ):
        validate_scene_position(
            attach_after_number=1,
            scenes=scenes,
            milestones=milestones,
            must_happen_before=[1],   # Milestone A liegt in Scene 1
            cant_happen_before=[],
        )


def test_cant_happen_before_violation(scenes, milestones):
    """
    3. Verstoß gegen can't happen before
    """
    with pytest.raises(
        ScenePositionError,
        match='Scene can\'t happen before milestone "Milestone B"',
    ):
        validate_scene_position(
            attach_after_number=1,
            scenes=scenes,
            milestones=milestones,
            must_happen_before=[],
            cant_happen_before=[2],   # Milestone B liegt in Scene 3
        )


def test_no_scenes_allowed_everywhere():
    """
    4. Keine Szenen vorhanden → immer erlaubt
    """
    result = validate_scene_position(
        attach_after_number=0,
        scenes=[],
        milestones=[],
        must_happen_before=[1],
        cant_happen_before=[2],
    )

    assert result is None


def test_missing_milestone_is_ignored(scenes, milestones):
    """
    5. Milestone existiert nicht → wird ignoriert
    """
    result = validate_scene_position(
        attach_after_number=1,
        scenes=scenes,
        milestones=milestones,
        must_happen_before=[999],
        cant_happen_before=[],
    )

    assert result is None


def test_first_rule_wins_must_before_checked_first(scenes, milestones):
    """
    6. Erste Regel gewinnt (must before vor cant before)
    """
    with pytest.raises(
        ScenePositionError,
        match='Scene must happen before milestone "Milestone A"',
    ):
        validate_scene_position(
            attach_after_number=1,
            scenes=scenes,
            milestones=milestones,
            must_happen_before=[1],   # Verstoß
            cant_happen_before=[2],   # Wäre auch ein Verstoß
        )


def test_attach_after_zero_boundary(scenes, milestones):
    """
    attach_after_number = 0
    Neue Szene wird vor Szene 1 eingefügt → gültig
    """
    result = validate_scene_position(
        attach_after_number=0,
        scenes=scenes,
        milestones=milestones,
        must_happen_before=[1],
        cant_happen_before=[],
    )

    assert result is None

