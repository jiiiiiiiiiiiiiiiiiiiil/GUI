# scene_position_validator.py

class ScenePositionError(Exception):
    """
    Raised when a new scene cannot be inserted at the desired position
    due to milestone constraints.
    """
    pass


def validate_scene_position(
    *,
    attach_after_number: int,
    scenes: list[dict],
    milestones: list[dict],
    cant_happen_before: list[int],
    must_happen_before: list[int],
) -> None:
    """
    Validates whether a new scene may be inserted at the given position
    with respect to milestone constraints.

    Rules:
    - Scenes BEFORE the insertion position must NOT contain milestones
      listed in must_happen_before.
    - Scenes AFTER the insertion position must NOT contain milestones
      listed in cant_happen_before.

    Raises:
        ScenePositionError with a concrete, user-facing message
        if the position is invalid.

    Returns:
        None if the position is valid.
    """

    # -------------------------
    # Prepare data
    # -------------------------

    # New scene will get number = attach_after_number + 1
    new_scene_number = attach_after_number + 1

    # Sort scenes by number to be safe
    scenes_sorted = sorted(scenes, key=lambda s: s["number"])

    # Map scene_id -> scene_number
    scene_id_to_number: dict[int, int] = {
        scene["id"]: scene["number"]
        for scene in scenes_sorted
    }

    # Map milestone_id -> (milestone_name, scene_number)
    milestone_positions: dict[int, tuple[str, int]] = {}

    for milestone in milestones:
        milestone_id = milestone["id"]
        scene_id = milestone["scene_id"]

        if scene_id not in scene_id_to_number:
            # Milestone refers to a scene not present in scenes list
            # This is outside the responsibility of this validator
            continue

        milestone_positions[milestone_id] = (
            milestone["name"],
            scene_id_to_number[scene_id],
        )

    # -------------------------
    # Rule 1: must happen before
    # -------------------------

    for milestone_id in must_happen_before:
        if milestone_id not in milestone_positions:
            continue

        milestone_name, milestone_scene_number = milestone_positions[milestone_id]

        # Milestone is before or at the insertion boundary → invalid
        if milestone_scene_number <= attach_after_number:
            raise ScenePositionError(
                f'Scene must happen before milestone "{milestone_name}"'
            )

    # -------------------------
    # Rule 2: can't happen before
    # -------------------------

    for milestone_id in cant_happen_before:
        if milestone_id not in milestone_positions:
            continue

        milestone_name, milestone_scene_number = milestone_positions[milestone_id]

        # Milestone is after or at the new scene position → invalid
        if milestone_scene_number >= new_scene_number:
            raise ScenePositionError(
                f'Scene can\'t happen before milestone "{milestone_name}"'
            )

    # -------------------------
    # Position is valid
    # -------------------------
    return None
