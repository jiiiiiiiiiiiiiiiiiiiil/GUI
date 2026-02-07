# paths.py
from pathlib import Path
import pandas as pd


SCENES_FILE = "Scenes.xlsx"
MILESTONES_FILE = "Milestones.xlsx"


def validate_project_path(path: str, must_exist=False) -> bool:
    p = Path(path)

    if must_exist and not p.exists():
        raise FileNotFoundError(f"Project path does not exist: {path}")

    if p.exists() and not p.is_dir():
        raise ValueError("Project path must be a directory")

    return True


def init_project_if_empty(path: str):
    p = Path(path)
    files = list(p.iterdir())

    if not files:
        create_empty_project_files(p)
        return

    validate_existing_project(p)


def create_empty_project_files(p: Path):
    scenes_columns = [
        "Number", "ID", "Title", "Content", "POV",
        "Can't happen before", "Must happen before", "Status"
    ]

    milestones_columns = [
        "Milestone", "Scene Title", "Milestone ID", "Scene ID"
    ]

    pd.DataFrame(columns=scenes_columns).to_excel(
        p / SCENES_FILE, index=False
    )
    pd.DataFrame(columns=milestones_columns).to_excel(
        p / MILESTONES_FILE, index=False
    )


def validate_existing_project(p: Path):
    scenes = p / SCENES_FILE
    milestones = p / MILESTONES_FILE

    if not scenes.exists() or not milestones.exists():
        raise RuntimeError(
            "Project folder must contain Scenes.xlsx and Milestones.xlsx"
        )

    # Detailvalidierung (Spalten etc.) → Phase 2
