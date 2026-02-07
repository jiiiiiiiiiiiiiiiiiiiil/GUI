# project_manager.py
from paths import (
    validate_project_path,
    init_project_if_empty,
)
from config import load_config, save_config


class ProjectManager:
    def __init__(self):
        self.config = load_config()
        self.project_path = self.config.get("last_project_path")

    def load_last_project(self):
        if self.project_path and validate_project_path(self.project_path):
            return self.project_path
        return None

    def set_project(self, path: str):
        validate_project_path(path, must_exist=True)
        init_project_if_empty(path)

        self.project_path = path
        self.config["last_project_path"] = path
        save_config(self.config)

        return path
