import sys
import pytest
from unittest.mock import Mock

import main


# -------------------------
# Qt-Dummies (minimal & stabil)
# -------------------------

class DummyQtObject:
    def __init__(self, *args, **kwargs):
        pass

    def setWindowTitle(self, *a): pass
    def resize(self, *a): pass
    def setLayout(self, *a): pass
    def show(self): pass
    def addWidget(self, *a): pass
    def addLayout(self, *a): pass
    def addStretch(self, *a): pass
    def setEnabled(self, *a): pass
    def setWidget(self, *a): pass
    def setWidgetResizable(self, *a): pass


class DummyApp:
    def __init__(self, *args, **kwargs):
        pass

    def exec(self):
        return 0


@pytest.fixture(autouse=True)
def mock_qt(monkeypatch):
    qt_objects = {
        "QApplication": DummyApp,
        "QWidget": DummyQtObject,
        "QVBoxLayout": DummyQtObject,
        "QHBoxLayout": DummyQtObject,
        "QLabel": DummyQtObject,
        "QPushButton": DummyQtObject,
        "QScrollArea": DummyQtObject,
    }

    for name, obj in qt_objects.items():
        monkeypatch.setattr(
            f"PySide6.QtWidgets.{name}",
            obj,
            raising=False
        )


# -------------------------
# Szenario 1: Dialog abgebrochen
# -------------------------

def test_run_app_dialog_aborted(monkeypatch):
    pm = Mock()

    monkeypatch.setattr(main, "ProjectManager", lambda: pm)
    monkeypatch.setattr(main, "determine_start_state", lambda pm: False)
    monkeypatch.setattr(main, "open_project_selection_dialog", lambda: None)

    show_error = Mock()
    monkeypatch.setattr(main, "show_fatal_error", show_error)

    exit_mock = Mock()
    monkeypatch.setattr(sys, "exit", exit_mock)

    main.run_app()

    pm.set_project.assert_not_called()
    show_error.assert_not_called()
    exit_mock.assert_called_once_with(0)


# -------------------------
# Szenario 2: Projekt gewählt, Erfolg
# -------------------------

def test_run_app_project_selected_success(monkeypatch):
    pm = Mock()

    monkeypatch.setattr(main, "ProjectManager", lambda: pm)
    monkeypatch.setattr(main, "determine_start_state", lambda pm: False)
    monkeypatch.setattr(main, "open_project_selection_dialog", lambda: "valid/path")

    show_error = Mock()
    monkeypatch.setattr(main, "show_fatal_error", show_error)

    exit_mock = Mock()
    monkeypatch.setattr(sys, "exit", exit_mock)

    main.run_app()

    pm.set_project.assert_called_once_with("valid/path")
    show_error.assert_not_called()
    exit_mock.assert_called_once_with(0)


# -------------------------
# Szenario 3: Projekt gewählt, Fehler
# -------------------------

def test_run_app_project_selected_failure(monkeypatch):
    pm = Mock()
    pm.set_project.side_effect = Exception("boom")

    monkeypatch.setattr(main, "ProjectManager", lambda: pm)
    monkeypatch.setattr(main, "determine_start_state", lambda pm: False)
    monkeypatch.setattr(main, "open_project_selection_dialog", lambda: "invalid/path")

    show_error = Mock()
    monkeypatch.setattr(main, "show_fatal_error", show_error)

    def fake_exit(code=0):
        raise SystemExit(code)

    monkeypatch.setattr(sys, "exit", fake_exit)

    with pytest.raises(SystemExit) as exc:
        main.run_app()

    assert exc.value.code == 1
    show_error.assert_called_once_with("boom")
    pm.set_project.assert_called_once_with("invalid/path")


# -------------------------
# Szenario 4: Projekt bereits geladen
# -------------------------

def test_run_app_project_already_loaded(monkeypatch):
    pm = Mock()

    monkeypatch.setattr(main, "ProjectManager", lambda: pm)
    monkeypatch.setattr(main, "determine_start_state", lambda pm: True)

    open_dialog = Mock()
    monkeypatch.setattr(main, "open_project_selection_dialog", open_dialog)

    show_error = Mock()
    monkeypatch.setattr(main, "show_fatal_error", show_error)

    exit_mock = Mock()
    monkeypatch.setattr(sys, "exit", exit_mock)

    main.run_app()

    open_dialog.assert_not_called()
    pm.set_project.assert_not_called()
    show_error.assert_not_called()
    exit_mock.assert_called_once_with(0)
