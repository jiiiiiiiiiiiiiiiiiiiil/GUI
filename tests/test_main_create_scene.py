import sys
from pathlib import Path
from unittest.mock import Mock

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def existing_scenes():
    return [
        {
            "number": 1,
            "title": "Scene 1",
            "content": "Content 1",
            "pov": "Alice",
        },
        {
            "number": 2,
            "title": "Scene 2",
            "content": "Content 2",
            "pov": "Bob",
        },
    ]


@pytest.fixture
def dialog_result():
    return {
        "title": "New Scene",
        "content": "New Content",
        "pov": "Alice",
        "status": "draft",
        "cant_happen_before": [1],
        "must_happen_before": [3, 4],
        "attach_after_number": 2,
    }


@pytest.fixture
def app_context(monkeypatch, existing_scenes):
    """
    Kontrollierte Umgebung für main.run_app():
    - Projekt gilt als geladen
    - Create-Button-Callback wird abgegriffen
    - kein echtes Qt
    - kein Eventloop
    """

    import main

    # ------------------------------------------------------------------
    # ProjectManager
    # ------------------------------------------------------------------
    project_manager = Mock()
    project_manager.load_last_project.return_value = "/project"
    project_manager.project_path = "/project"

    monkeypatch.setattr(main, "ProjectManager", lambda: project_manager)

    # ------------------------------------------------------------------
    # Scene loading / building
    # ------------------------------------------------------------------
    load_scenes = Mock(return_value=existing_scenes)
    build_scene_list = Mock()

    monkeypatch.setattr(main, "load_scenes", load_scenes)
    monkeypatch.setattr(main, "build_scene_list", build_scene_list)

    # ------------------------------------------------------------------
    # Create scene
    # ------------------------------------------------------------------
    create_scene = Mock()
    monkeypatch.setattr(main, "create_scene", create_scene)

    # ------------------------------------------------------------------
    # Helper functions
    # ------------------------------------------------------------------
    monkeypatch.setattr(main, "get_all_povs", Mock(return_value=["Alice", "Bob"]))
    monkeypatch.setattr(main, "get_most_common_pov", Mock(return_value="Alice"))
    monkeypatch.setattr(main, "load_milestones", Mock(return_value=["m1", "m2"]))

    # ------------------------------------------------------------------
    # SceneDialog
    # ------------------------------------------------------------------
    dialog = Mock()
    SceneDialog = Mock(return_value=dialog)
    monkeypatch.setattr(main, "SceneDialog", SceneDialog)

    # ------------------------------------------------------------------
    # Qt minimal mocks + Callback-Abgriff
    # ------------------------------------------------------------------
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

    # prevent sys.exit / event loop
    monkeypatch.setattr(main.sys, "exit", Mock())

    return {
        "main": main,
        "dialog": dialog,
        "SceneDialog": SceneDialog,
        "create_scene": create_scene,
        "load_scenes": load_scenes,
        "build_scene_list": build_scene_list,
        "callbacks": callbacks,
    }


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_create_button_opens_dialog(app_context):
    """
    Test 1:
    Create-Button → SceneDialog wird instanziiert
    """
    ctx = app_context
    ctx["dialog"].exec.return_value = False  # ← WICHTIGER FIX

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    ctx["SceneDialog"].assert_called_once()

    _, kwargs = ctx["SceneDialog"].call_args
    assert kwargs["existing_scene"] is None
    assert kwargs["available_povs"] == ["Alice", "Bob"]
    assert kwargs["default_pov"] == "Alice"
    assert kwargs["milestones"] == ["m1", "m2"]
    assert kwargs["max_scene_number"] == 2


def test_cancel_dialog_does_nothing(app_context):
    """
    Test 2:
    Cancel im Dialog → keine Folgeaktionen
    """
    ctx = app_context
    ctx["dialog"].exec.return_value = False

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    ctx["create_scene"].assert_not_called()
    assert ctx["load_scenes"].call_count == 1
    assert ctx["build_scene_list"].call_count == 1


def test_confirm_creates_scene(app_context, dialog_result):
    """
    Test 3:
    Confirm → create_scene mit exakten Daten
    """
    ctx = app_context
    ctx["dialog"].exec.return_value = True
    ctx["dialog"].get_result.return_value = dialog_result

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    ctx["create_scene"].assert_called_once_with(
        scenes_path=Path("/project") / "Scenes.xlsx",
        title="New Scene",
        content="New Content",
        pov="Alice",
        status="draft",
        cant_happen_before="1",
        must_happen_before="3\n4",
        attach_after_number=2,
    )


def test_scenes_reloaded_after_create(app_context, dialog_result):
    """
    Test 4:
    Nach Create → Szenen werden neu geladen
    """
    ctx = app_context
    ctx["dialog"].exec.return_value = True
    ctx["dialog"].get_result.return_value = dialog_result

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    assert ctx["load_scenes"].call_count == 2


def test_scene_list_rebuilt_after_create(app_context, dialog_result):
    """
    Test 5:
    Nach Reload → GUI-Liste wird neu aufgebaut
    """
    ctx = app_context
    ctx["dialog"].exec.return_value = True
    ctx["dialog"].get_result.return_value = dialog_result

    main = ctx["main"]
    main.run_app()
    ctx["callbacks"]["on_create_scene"]()

    assert ctx["build_scene_list"].call_count == 2
