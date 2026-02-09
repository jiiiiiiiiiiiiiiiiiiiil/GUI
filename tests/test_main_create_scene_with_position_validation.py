import sys
from pathlib import Path
from unittest.mock import Mock

import pytest

from scene_position_validator import ScenePositionError


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def scenes():
    return [
        {"id": 1, "number": 1, "title": "S1", "content": "C1", "pov": "Alice"},
        {"id": 2, "number": 2, "title": "S2", "content": "C2", "pov": "Bob"},
    ]


@pytest.fixture
def dialog_result():
    return {
        "title": "New Scene",
        "content": "New Content",
        "pov": "Alice",
        "status": "draft",
        "attach_after_number": 1,
        "cant_happen_before": [],
        "must_happen_before": [],
    }


@pytest.fixture
def app_context(monkeypatch, scenes):
    """
    Kontrollierte Umgebung für main.run_app()
    Fokus: Create-Scene-Orchestrierung inkl. Positionsvalidierung
    """

    import main

    # --------------------------------------------------
    # ProjectManager
    # --------------------------------------------------
    project_manager = Mock()
    project_manager.load_last_project.return_value = "/project"
    project_manager.project_path = "/project"
    monkeypatch.setattr(main, "ProjectManager", lambda: project_manager)

    # --------------------------------------------------
    # Scene IO
    # --------------------------------------------------
    load_scenes = Mock(return_value=scenes)
    build_scene_list = Mock()

    monkeypatch.setattr(main, "load_scenes", load_scenes)
    monkeypatch.setattr(main, "build_scene_list", build_scene_list)

    # --------------------------------------------------
    # Call order tracking
    # --------------------------------------------------
    call_log = []

    def validate_wrapper(**kwargs):
        call_log.append("validate")

    def create_wrapper(**kwargs):
        call_log.append("create")

    validate_scene_position = Mock(side_effect=validate_wrapper)
    create_scene = Mock(side_effect=create_wrapper)

    monkeypatch.setattr(main, "validate_scene_position", validate_scene_position)
    monkeypatch.setattr(main, "create_scene", create_scene)

    # --------------------------------------------------
    # Error UI
    # --------------------------------------------------
    show_scene_error = Mock()
    monkeypatch.setattr(main, "show_scene_error", show_scene_error)

    # --------------------------------------------------
    # Helper
    # --------------------------------------------------
    monkeypatch.setattr(main, "get_all_povs", Mock(return_value=["Alice", "Bob"]))
    monkeypatch.setattr(main, "get_most_common_pov", Mock(return_value="Alice"))
    monkeypatch.setattr(main, "load_milestones", Mock(return_value=[]))

    # --------------------------------------------------
    # SceneDialog
    # --------------------------------------------------
    dialog = Mock()
    dialog.exec.return_value = True
    dialog.get_result.return_value = {}

    SceneDialog = Mock(return_value=dialog)
    monkeypatch.setattr(main, "SceneDialog", SceneDialog)

    # --------------------------------------------------
    # Qt minimal + Callback-Abgriff
    # --------------------------------------------------
    callbacks = {}

    create_button = Mock()
    clicked = Mock()

    def connect(cb):
        callbacks["on_create_scene"] = cb

    clicked.connect = connect
    create_button.clicked = clicked

    def fake_button(*args, **kwargs):
        return create_button

    qt_widgets = Mock()
    qt_widgets.QApplication.return_value = Mock()
    qt_widgets.QWidget.return_value = Mock()
    qt_widgets.QVBoxLayout.return_value = Mock()
    qt_widgets.QHBoxLayout.return_value = Mock()
    qt_widgets.QLabel.return_value = Mock()
    qt_widgets.QPushButton.side_effect = fake_button
    qt_widgets.QScrollArea.return_value = Mock()

    monkeypatch.setitem(sys.modules, "PySide6.QtWidgets", qt_widgets)
    monkeypatch.setattr(main.sys, "exit", Mock())

    return {
        "main": main,
        "dialog": dialog,
        "validate_scene_position": validate_scene_position,
        "create_scene": create_scene,
        "load_scenes": load_scenes,
        "build_scene_list": build_scene_list,
        "show_scene_error": show_scene_error,
        "callbacks": callbacks,
        "call_log": call_log,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_valid_position_scene_is_created(app_context, dialog_result):
    """
    1. Gültige Position → Szene wird angelegt
    """
    ctx = app_context
    ctx["dialog"].get_result.return_value = dialog_result

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    ctx["validate_scene_position"].assert_called_once()
    ctx["create_scene"].assert_called_once()
    ctx["show_scene_error"].assert_not_called()

    # 1x Initial-Load + 1x Reload nach Create
    assert ctx["load_scenes"].call_count == 2


def test_invalid_position_scene_not_created(app_context, dialog_result):
    """
    2. Ungültige Position → Szene wird NICHT angelegt
    """
    ctx = app_context
    ctx["dialog"].get_result.return_value = dialog_result
    ctx["validate_scene_position"].side_effect = ScenePositionError("Fehlertext")

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    ctx["create_scene"].assert_not_called()
    ctx["show_scene_error"].assert_called_once_with("Fehlertext")

    # nur Initial-Load
    assert ctx["load_scenes"].call_count == 1
    assert ctx["build_scene_list"].call_count == 1


def test_abort_is_hard_after_validation_error(app_context, dialog_result):
    """
    3. Abbruch ist hart – kein Code nach Validator läuft
    """
    ctx = app_context
    ctx["dialog"].get_result.return_value = dialog_result
    ctx["validate_scene_position"].side_effect = ScenePositionError("Boom")

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    assert ctx["create_scene"].call_count == 0
    assert ctx["load_scenes"].call_count == 1   # nur Initial-Load
    assert ctx["build_scene_list"].call_count == 1


def test_validation_happens_before_create_scene(app_context, dialog_result):
    """
    4. Reihenfolge: validate_scene_position vor create_scene
    """
    ctx = app_context
    ctx["dialog"].get_result.return_value = dialog_result

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    assert ctx["call_log"] == ["validate", "create"]
