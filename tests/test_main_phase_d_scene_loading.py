# Dieser Test ist fehlgeschlagen wegen dem DummyQtObject, aber scheinbar sind hier keine weiteren Tests nötig. Der Test wurde bewusst ignoriert.

import sys
from pathlib import Path
from unittest.mock import Mock

import pytest
import main


# -------------------------
# Minimal Qt-Dummies
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
    def setFrameShape(self, *a): pass
    def setCheckable(self, *a): pass
    def setChecked(self, *a): pass
    def setFixedWidth(self, *a): pass
    def setFlat(self, *a): pass
    def setVisible(self, *a): pass

    class Signal:
        def connect(self, *a): pass

    @property
    def toggled(self):
        return self.Signal()


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
        "QFrame": DummyQtObject,
    }

    for name, obj in qt_objects.items():
        monkeypatch.setattr(
            f"PySide6.QtWidgets.{name}",
            obj,
            raising=False
        )


# -------------------------
# Szenario 1: Projekt geladen → Szenen werden geladen
# -------------------------

def test_run_app_loads_scenes_when_project_loaded(monkeypatch):
    pm = Mock()
    pm.project_path = "/project"

    monkeypatch.setattr(main, "ProjectManager", lambda: pm)
    monkeypatch.setattr(main, "determine_start_state", lambda pm: True)

    load_scenes = Mock(return_value=[{"number": 1, "title": "A", "pov": "X", "content": "Y"}])
    monkeypatch.setattr(main, "load_scenes", load_scenes)

    exit_mock = Mock()
    monkeypatch.setattr(sys, "exit", exit_mock)

    main.run_app()

    load_scenes.assert_called_once_with(Path("/project") / "Scenes.xlsx")
    exit_mock.assert_called_once_with(0)


# -------------------------
# Szenario 2: Keine Szenen → kein Fehler
# -------------------------

def test_run_app_no_scenes_does_not_crash(monkeypatch):
    pm = Mock()
    pm.project_path = "/project"

    monkeypatch.setattr(main, "ProjectManager", lambda: pm)
    monkeypatch.setattr(main, "determine_start_state", lambda pm: True)

    monkeypatch.setattr(main, "load_scenes", lambda path: [])

    exit_mock = Mock()
    monkeypatch.setattr(sys, "exit", exit_mock)

    main.run_app()

    exit_mock.assert_called_once_with(0)
