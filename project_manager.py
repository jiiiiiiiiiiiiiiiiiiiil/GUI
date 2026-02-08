from pathlib import Path

from config import load_config, save_config
from paths import validate_project_path, SCENES_FILE, MILESTONES_FILE
from excel_validator import (
    validate_excel_file,
    SCENES_REQUIRED_COLUMNS,
    MILESTONES_REQUIRED_COLUMNS,
)


class ProjectManager:
    def __init__(self):
        self.config = load_config()
        self.project_path = self.config.get("last_project_path")

    def load_last_project(self):
        if not self.project_path:
            return None

        path = Path(self.project_path)

        if not path.exists():
            return None

        if not path.is_dir():
            return None

        return self.project_path

    def set_project(self, path: str):
        validate_project_path(path, must_exist=True)

        project_dir = Path(path)
        files = list(project_dir.iterdir())

        scenes_path = project_dir / SCENES_FILE
        milestones_path = project_dir / MILESTONES_FILE

        # -------------------------
        # Fall 1: Ordner leer
        # -------------------------
        if not files:
            self._create_empty_project(project_dir)

        # -------------------------
        # Fall 2: Dateien existieren
        # -------------------------
        else:
            validate_excel_file(scenes_path, SCENES_REQUIRED_COLUMNS)
            validate_excel_file(milestones_path, MILESTONES_REQUIRED_COLUMNS)

        # Projekt gilt ab hier als gültig
        self.project_path = path
        self.config["last_project_path"] = path
        save_config(self.config)

        return path

    def _create_empty_project(self, project_dir: Path):
        import pandas as pd

        scenes_columns = SCENES_REQUIRED_COLUMNS
        milestones_columns = MILESTONES_REQUIRED_COLUMNS

        pd.DataFrame(columns=scenes_columns).to_excel(
            project_dir / SCENES_FILE, index=False
        )
        pd.DataFrame(columns=milestones_columns).to_excel(
            project_dir / MILESTONES_FILE, index=False
        )
