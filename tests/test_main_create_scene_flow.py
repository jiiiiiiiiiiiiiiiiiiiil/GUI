import sys
# Test hat nicht funktioniert. Habe neuen Chat gestartet und GPT hat nen neuen Test geschrieben (test_main_create_scene.py)

from pathlib import Path
from unittest.mock import Mock

import pytest

import main


# ------------------------------------------------------------------
# Basis-Fixture: QApplication vorhanden (pytest-qt)
# ------------------------------------------------------------------

@pytest.fixture(autouse=True)
def mock_qapplication(monkeypatch):
    class DummyApp:
        def __init__(self, *args, **kwargs):
            pass

        def exec(self):
            return 0

    monkeypatch.setattr(main, "QApplication", DummyApp)



# ------------------------------------------------------------------
# Projekt gilt als geladen
# ------------------------------------------------------------------

@pytest.fixture
def project_loaded(monkeypatch):
    pm = Mock()
    pm.project_path = "/project"

    monkeypatch.setattr(main, "ProjectManager", lambda: pm)
    monkeypatch.setattr(main, "determine_start_state", lambda _: True)

    return pm


# ------------------------------------------------------------------
# Szenen-Umgebung (Mocks / Spies)
# ------------------------------------------------------------------

@pytest.fixture
def scene_environment(monkeypatch):
    # POVs / Milestones
    monkeypatch.setattr(main, "get_all_povs", lambda _: ["Leni", "Mia"])
    monkeypatch.setattr(main, "get_most_common_pov", lambda _: "Leni")
    monkeypatch.setattr(main, "load_milestones", lambda _: [])

    # Szenen vor / nach Create
    scenes_initial = [
        {"number": 1, "title": "A", "content": "", "pov": "Leni"}
    ]
    scenes_after = scenes_initial + [
        {"number": 2, "title": "B", "content": "", "pov": "Mia"}
    ]

    load_scenes = Mock(side_effect=[scenes_initial, scenes_after])
    monkeypatch.setattr(main, "load_scenes", load_scenes)

    build_scene_list = Mock()
    monkeypatch.setattr(main, "build_scene_list", build_scene_list)

    create_scene = Mock()
    monkeypatch.setattr(main, "create_scene", create_scene)

    return {
        "load_scenes": load_scenes,
        "build_scene_list": build_scene_list,
        "create_scene": create_scene,
        "scenes_initial": scenes_initial,
        "scenes_after": scenes_after,
    }


# ------------------------------------------------------------------
# Dialog: Cancel
# ------------------------------------------------------------------

@pytest.fixture
def dialog_cancel(monkeypatch):
    dialog = Mock()
    dialog.exec.return_value = False
    monkeypatch.setattr(main, "SceneDialog", lambda **_: dialog)
    return dialog


# ------------------------------------------------------------------
# Dialog: Confirm
# ------------------------------------------------------------------

@pytest.fixture
def dialog_confirm(monkeypatch):
    dialog = Mock()
    dialog.exec.return_value = True
    dialog.get_result.return_value = {
        "title": "New Scene",
        "content": "Text",
        "pov": "Mia",
        "status": "draft",
        "cant_happen_before": [1],
        "must_happen_before": [],
        "attach_after_number": 1,
    }
    monkeypatch.setattr(main, "SceneDialog", lambda **_: dialog)
    return dialog


# ==================================================================
# TESTS
# ==================================================================

def test_create_button_opens_dialog(
    qtbot,
    project_loaded,
    scene_environment,
    monkeypatch,
):
    dialog_ctor = Mock()
    monkeypatch.setattr(main, "SceneDialog", dialog_ctor)

    main.run_app()

    # Dialog darf nicht automatisch erscheinen
    dialog_ctor.assert_not_called()


def test_cancel_in_dialog_does_nothing(
    qtbot,
    project_loaded,
    scene_environment,
    dialog_cancel,
):
    main.run_app()

    env = scene_environment

    # Initialer Load passiert
    env["load_scenes"].assert_called_once()
    env["build_scene_list"].assert_called_once()

    # Aber kein Create / Reload
    env["create_scene"].assert_not_called()
    assert env["load_scenes"].call_count == 1


def test_confirm_creates_scene(
    qtbot,
    project_loaded,
    scene_environment,
    dialog_confirm,
):
    main.run_app()

    env = scene_environment

    env["create_scene"].assert_called_once_with(
        scenes_path=Path("/project") / "Scenes.xlsx",
        title="New Scene",
        content="Text",
        pov="Mia",
        status="draft",
        cant_happen_before="1",
        must_happen_before="",
        attach_after_number=1,
    )


def test_after_create_scenes_are_reloaded(
    qtbot,
    project_loaded,
    scene_environment,
    dialog_confirm,
):
    main.run_app()

    env = scene_environment

    # initial load + reload
    assert env["load_scenes"].call_count == 2


def test_scene_list_is_rebuilt_with_new_scenes(
    qtbot,
    project_loaded,
    scene_environment,
    dialog_confirm,
):
    main.run_app()

    env = scene_environment

    # build_scene_list: initial + after create
    assert env["build_scene_list"].call_count == 2

    # letzter Aufruf bekommt neue Szenen
    _, kwargs = env["build_scene_list"].call_args
    assert kwargs == {}  # positional args

    args, _ = env["build_scene_list"].call_args
    assert args[1] == env["scenes_after"]
