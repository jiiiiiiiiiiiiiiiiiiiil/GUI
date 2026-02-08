import pytest
from pathlib import Path

from project_manager import ProjectManager


def test_load_last_project_no_path_in_config(monkeypatch):
    monkeypatch.setattr(
        "project_manager.load_config",
        lambda: {}
    )

    manager = ProjectManager()

    assert manager.load_last_project() is None


def test_load_last_project_path_does_not_exist(monkeypatch):
    monkeypatch.setattr(
        "project_manager.load_config",
        lambda: {"last_project_path": "/invalid/path"}
    )

    monkeypatch.setattr(Path, "exists", lambda self: False)

    manager = ProjectManager()

    assert manager.load_last_project() is None


def test_load_last_project_path_exists_but_not_directory(monkeypatch):
    monkeypatch.setattr(
        "project_manager.load_config",
        lambda: {"last_project_path": "/some/file"}
    )

    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "is_dir", lambda self: False)

    manager = ProjectManager()

    assert manager.load_last_project() is None


def test_load_last_project_valid_directory(monkeypatch):
    project_path = "/valid/project"

    monkeypatch.setattr(
        "project_manager.load_config",
        lambda: {"last_project_path": project_path}
    )

    monkeypatch.setattr(Path, "exists", lambda self: True)
    monkeypatch.setattr(Path, "is_dir", lambda self: True)

    manager = ProjectManager()

    assert manager.load_last_project() == project_path
