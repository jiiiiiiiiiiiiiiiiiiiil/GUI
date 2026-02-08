import pytest
from unittest.mock import Mock

import main


# =========================
# determine_start_state
# =========================

def test_determine_start_state_project_loaded():
    project_manager = Mock()
    project_manager.load_last_project.return_value = "/some/project"

    result = main.determine_start_state(project_manager)

    assert result is True
    project_manager.load_last_project.assert_called_once()


def test_determine_start_state_no_project():
    project_manager = Mock()
    project_manager.load_last_project.return_value = None

    result = main.determine_start_state(project_manager)

    assert result is False
    project_manager.load_last_project.assert_called_once()


# =========================
# start flow decision logic
# =========================

def test_start_flow_project_already_loaded(monkeypatch):
    project_manager = Mock()

    monkeypatch.setattr(
        main,
        "determine_start_state",
        lambda pm: True
    )

    open_dialog = Mock()
    monkeypatch.setattr(main, "open_project_selection_dialog", open_dialog)

    project_loaded = main.determine_start_state(project_manager)

    if not project_loaded:
        selected = main.open_project_selection_dialog(project_manager)
        if selected is not None:
            project_manager.set_project(selected)

    open_dialog.assert_not_called()
    project_manager.set_project.assert_not_called()


def test_start_flow_no_project_dialog_aborted(monkeypatch):
    project_manager = Mock()

    monkeypatch.setattr(
        main,
        "determine_start_state",
        lambda pm: False
    )

    monkeypatch.setattr(
        main,
        "open_project_selection_dialog",
        lambda pm: None
    )

    project_loaded = main.determine_start_state(project_manager)

    if not project_loaded:
        selected = main.open_project_selection_dialog(project_manager)
        if selected is not None:
            project_manager.set_project(selected)

    project_manager.set_project.assert_not_called()


def test_start_flow_no_project_folder_selected(monkeypatch):
    project_manager = Mock()

    monkeypatch.setattr(
        main,
        "determine_start_state",
        lambda pm: False
    )

    monkeypatch.setattr(
        main,
        "open_project_selection_dialog",
        lambda pm: "some/path"
    )

    project_loaded = main.determine_start_state(project_manager)

    if not project_loaded:
        selected = main.open_project_selection_dialog(project_manager)
        if selected is not None:
            project_manager.set_project(selected)

    project_manager.set_project.assert_called_once_with("some/path")
