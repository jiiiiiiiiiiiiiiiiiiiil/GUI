from pathlib import Path
import pandas as pd


def load_milestones(milestones_path: Path) -> list[dict]:
    """
    Loads milestones from Milestones.xlsx.

    Returns a list of dicts:
    {
        "id": int,
        "name": str,
        "scene_id": int,
        "scene_title": str,
    }

    Read-only. No validation. No side effects.
    """
    df = pd.read_excel(milestones_path)

    required_columns = [
        "Milestone",
        "Scene Title",
        "Milestone ID",
        "Scene ID",
    ]

    for column in required_columns:
        if column not in df.columns:
            return []

    milestones: list[dict] = []

    for _, row in df.iterrows():
        if not isinstance(row["Milestone"], str):
            continue

        name = row["Milestone"].strip()
        if not name:
            continue

        milestones.append({
            "id": int(row["Milestone ID"]),
            "name": name,
            "scene_id": int(row["Scene ID"]),
            "scene_title": row["Scene Title"],
        })

    milestones.sort(key=lambda m: m["id"])
    return milestones
