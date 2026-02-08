import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock

from project_manager import ProjectManager
from paths import SCENES_FILE, MILESTONES_FILE
from excel_validator import (
    SCENES_REQUIRED_COLUMNS,
    MILESTONES_REQUIRED_COLUMNS,
)


# -------------------------
# Helpers
# -------------------------

def create_valid_excel(path: Path, columns: list[str]):
    df = pd.DataFrame(columns=columns)
    df.to_excel(path, index=False)


# -------------------------
# Fall 1: leerer Ordner
# -------------------------

def test_set_project_creates_empty_project_files(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "project_manager.validate_project_path",
        lambda path, must_exist=True: None
    )

    save_config = Mock()
    monkeypatch.setattr("project_manager.save_config", save_config)

    manager = ProjectManager()

    result = manager.set_project(str(tmp_path))

    scenes = tmp_path / SCENES_FILE
    milestones = tmp_path / MILESTONES_FILE

    assert scenes.exists()
    assert milestones.exists()

    scenes_df = pd.read_excel(scenes)
    milestones_df = pd.read_excel(milestones)

    assert list(scenes_df.columns) == SCENES_REQUIRED_COLUMNS
    assert list(milestones_df.columns) == MILESTONES_REQUIRED_COLUMNS

    assert result == str(tmp_path)
    save_config.assert_called_once()


# -------------------------
# Fall 2: gültige Dateien
# -------------------------

def test_set_project_valid_existing_files(tmp_path, monkeypatch):
    create_valid_excel(tmp_path / SCENES_FILE, SCENES_REQUIRED_COLUMNS)
    create_valid_excel(tmp_path / MILESTONES_FILE, MILESTONES_REQUIRED_COLUMNS)

    monkeypatch.setattr(
        "project_manager.validate_project_path",
        lambda path, must_exist=True: None
    )

    validate_excel = Mock()
    monkeypatch.setattr(
        "project_manager.validate_excel_file",
        validate_excel
    )

    monkeypatch.setattr("project_manager.save_config", Mock())

    manager = ProjectManager()

    result = manager.set_project(str(tmp_path))

    assert result == str(tmp_path)

    validate_excel.assert_any_call(
        tmp_path / SCENES_FILE,
        SCENES_REQUIRED_COLUMNS
    )
    validate_excel.assert_any_call(
        tmp_path / MILESTONES_FILE,
        MILESTONES_REQUIRED_COLUMNS
    )


# -------------------------
# Fall 3: Scenes.xlsx fehlt
# -------------------------

def test_set_project_missing_scenes_file_raises(tmp_path, monkeypatch):
    create_valid_excel(tmp_path / MILESTONES_FILE, MILESTONES_REQUIRED_COLUMNS)

    monkeypatch.setattr(
        "project_manager.validate_project_path",
        lambda path, must_exist=True: None
    )

    monkeypatch.setattr("project_manager.save_config", Mock())

    manager = ProjectManager()

    with pytest.raises(Exception):
        manager.set_project(str(tmp_path))


# -------------------------
# Fall 4: Milestones.xlsx fehlt
# -------------------------

def test_set_project_missing_milestones_file_raises(tmp_path, monkeypatch):
    create_valid_excel(tmp_path / SCENES_FILE, SCENES_REQUIRED_COLUMNS)

    monkeypatch.setattr(
        "project_manager.validate_project_path",
        lambda path, must_exist=True: None
    )

    monkeypatch.setattr("project_manager.save_config", Mock())

    manager = ProjectManager()

    with pytest.raises(Exception):
        manager.set_project(str(tmp_path))


# -------------------------
# Fall 5: falsche Spalten
# -------------------------

def test_set_project_invalid_scenes_excel_raises(tmp_path, monkeypatch):
    create_valid_excel(tmp_path / SCENES_FILE, ["wrong", "columns"])
    create_valid_excel(tmp_path / MILESTONES_FILE, MILESTONES_REQUIRED_COLUMNS)

    monkeypatch.setattr(
        "project_manager.validate_project_path",
        lambda path, must_exist=True: None
    )

    def raise_validation_error(*args, **kwargs):
        raise ValueError("Invalid Excel structure")

    monkeypatch.setattr(
        "project_manager.validate_excel_file",
        raise_validation_error
    )

    monkeypatch.setattr("project_manager.save_config", Mock())

    manager = ProjectManager()

    with pytest.raises(ValueError):
        manager.set_project(str(tmp_path))


# -------------------------
# Fall 6: Datei nicht lesbar
# -------------------------

def test_set_project_excel_not_readable_exception_propagates(tmp_path, monkeypatch):
    create_valid_excel(tmp_path / SCENES_FILE, SCENES_REQUIRED_COLUMNS)
    create_valid_excel(tmp_path / MILESTONES_FILE, MILESTONES_REQUIRED_COLUMNS)

    monkeypatch.setattr(
        "project_manager.validate_project_path",
        lambda path, must_exist=True: None
    )

    def io_error(*args, **kwargs):
        raise IOError("File is locked")

    monkeypatch.setattr(
        "project_manager.validate_excel_file",
        io_error
    )

    monkeypatch.setattr("project_manager.save_config", Mock())

    manager = ProjectManager()

    with pytest.raises(IOError):
        manager.set_project(str(tmp_path))
