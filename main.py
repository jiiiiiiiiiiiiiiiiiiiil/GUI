# main.py

import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
)

from config import load_last_project_path, save_last_project_path


# -------------------------
# Project selection dialog
# -------------------------

def open_project_selection_dialog(parent=None) -> Path | None:
    folder = QFileDialog.getExistingDirectory(
        parent,
        "Select project folder"
    )

    if not folder:
        QMessageBox.critical(
            parent,
            "No project selected",
            "A project folder is required to start the application."
        )
        return None

    return Path(folder)


# -------------------------
# Project initialization
# -------------------------

SCENES_FILENAME = "Scenes.xlsx"
MILESTONES_FILENAME = "Milestones.xlsx"

SCENES_HEADERS = [
    "Number",
    "ID",
    "Title",
    "Content",
    "POV",
    "Can't happen before",
    "Must happen before",
    "Status",
]

MILESTONES_HEADERS = [
    "Milestone",
    "Scene Title",
    "Milestone ID",
    "Scene ID",
]


def initialize_project(project_path: Path, parent=None) -> bool:
    scenes_path = project_path / SCENES_FILENAME
    milestones_path = project_path / MILESTONES_FILENAME

    # Case 1: empty folder → create files
    if not scenes_path.exists() and not milestones_path.exists():
        try:
            import pandas as pd

            pd.DataFrame(columns=SCENES_HEADERS).to_excel(scenes_path, index=False)
            pd.DataFrame(columns=MILESTONES_HEADERS).to_excel(milestones_path, index=False)
            return True
        except Exception as e:
            QMessageBox.critical(
                parent,
                "Initialization failed",
                f"Could not create project files:\n{e}"
            )
            return False

    # Case 2: files exist → validate
    for path, headers, name in [
        (scenes_path, SCENES_HEADERS, SCENES_FILENAME),
        (milestones_path, MILESTONES_HEADERS, MILESTONES_FILENAME),
    ]:
        if not path.exists():
            QMessageBox.critical(
                parent,
                "Invalid project",
                f"Missing required file: {name}"
            )
            return False

        try:
            import pandas as pd
            df = pd.read_excel(path)
        except Exception:
            QMessageBox.critical(
                parent,
                "Invalid project",
                f"File is not a readable Excel file: {name}"
            )
            return False

        if list(df.columns) != headers:
            QMessageBox.critical(
                parent,
                "Invalid project",
                f"Invalid columns in {name}.\nExpected:\n{headers}"
            )
            return False