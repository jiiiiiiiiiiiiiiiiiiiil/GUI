import importlib
import sys
import types

import pytest


class DummyApp:
    def __init__(self, *args, **kwargs):
        pass

    def exec(self):
        return 0


@pytest.fixture
def mock_qt(monkeypatch):
    monkeypatch.setattr(
        "PySide6.QtWidgets.QApplication",
        DummyApp
    )

    monkeypatch.setattr(
        "PySide6.QtWidgets.QWidget.show",
        lambda self: None
    )

    monkeypatch.setattr(
        sys,
        "exit",
        lambda *args, **kwargs: None
    )


def import_main_with_project(monkeypatch, project_path):
    class DummyProjectManager:
        def load_last_project(self):
            return project_path

    monkeypatch.setattr(
        "project_manager.ProjectManager",
        DummyProjectManager
    )

    if "main" in sys.modules:
        del sys.modules["main"]

    return importlib.import_module("main")


def test_startup_without_project(mock_qt, monkeypatch):
    main = import_main_with_project(monkeypatch, None)

    assert main.project_loaded is False

    assert not main.refresh_wc_button.isEnabled()
    assert not main.reset_button.isEnabled()
    assert not main.create_scene_button.isEnabled()
    assert not main.save_button.isEnabled()

    labels = [
        w.text()
        for w in main.scene_list_container.findChildren(type(main.total_word_count_label))
    ]

    assert any("No project loaded" in text for text in labels)


def test_startup_with_project(mock_qt, monkeypatch):
    main = import_main_with_project(monkeypatch, "/valid/project")

    assert main.project_loaded is True

    assert main.refresh_wc_button.isEnabled()
    assert main.reset_button.isEnabled()
    assert main.create_scene_button.isEnabled()
    assert main.save_button.isEnabled()

    labels = [
        w.text()
        for w in main.scene_list_container.findChildren(type(main.total_word_count_label))
    ]

    assert any("Project loaded" in text for text in labels)
