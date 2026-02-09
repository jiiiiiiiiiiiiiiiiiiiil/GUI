import pytest
from PySide6.QtCore import Qt

from scene_dialog import SceneDialog


@pytest.fixture
def milestones():
    return [
        {"id": 1, "name": "Inciting Incident"},
        {"id": 2, "name": "Midpoint"},
        {"id": 3, "name": "Climax"},
    ]


@pytest.fixture
def dialog(qtbot, milestones):
    dlg = SceneDialog(
        existing_scene=None,
        available_povs=["Leni", "Mia"],
        default_pov=None,
        milestones=milestones,
        max_scene_number=10,
    )
    qtbot.addWidget(dlg)
    return dlg


# -------------------------
# Test 1: Initialzustand
# -------------------------

def test_initial_state_confirm_disabled(dialog):
    assert not dialog.confirm_button.isEnabled()


# -------------------------
# Test 2: Title ist Pflichtfeld
# -------------------------

def test_title_required(dialog):
    dialog.pov_dropdown.setCurrentText("Leni")
    dialog.title_input.setText("   ")

    assert not dialog.confirm_button.isEnabled()


# -------------------------
# Test 3: POV-Prioritätslogik
# -------------------------

def test_pov_free_text_overrides_dropdown(dialog):
    dialog.title_input.setText("Scene title")
    dialog.pov_dropdown.setCurrentText("Leni")
    dialog.pov_free_text.setText("Mia")

    assert dialog.confirm_button.isEnabled()

    result = dialog.get_result()
    assert result["pov"] == "Mia"


# -------------------------
# Test 4: POV ist Pflichtfeld
# -------------------------

def test_pov_required(dialog):
    dialog.title_input.setText("Scene title")
    dialog.pov_dropdown.setCurrentIndex(0)  # leer
    dialog.pov_free_text.setText("")

    assert not dialog.confirm_button.isEnabled()


# -------------------------
# Test 5: Milestone-Doppelauswahl
# -------------------------

def test_milestone_overlap_disables_confirm(dialog):
    dialog.title_input.setText("Scene title")
    dialog.pov_dropdown.setCurrentText("Leni")

    dialog.cant_list.item(0).setSelected(True)
    dialog.must_list.item(0).setSelected(True)

    assert not dialog.confirm_button.isEnabled()


# -------------------------
# Test 6: Gültiger Zustand
# -------------------------

def test_valid_state_enables_confirm(dialog):
    dialog.title_input.setText("Scene title")
    dialog.pov_dropdown.setCurrentText("Leni")

    dialog.cant_list.item(0).setSelected(True)
    dialog.must_list.item(1).setSelected(True)

    assert dialog.confirm_button.isEnabled()


# -------------------------
# Test 7: get_result Datenvertrag
# -------------------------

def test_get_result_returns_expected_structure(dialog):
    dialog.title_input.setText("Final Scene")
    dialog.content_input.setPlainText("Some content")
    dialog.pov_free_text.setText("Mia")
    dialog.status_dropdown.setCurrentText("solid")
    dialog.attach_spin.setValue(3)

    dialog.cant_list.item(0).setSelected(True)
    dialog.must_list.item(2).setSelected(True)

    result = dialog.get_result()

    assert result == {
        "title": "Final Scene",
        "content": "Some content",
        "pov": "Mia",
        "status": "solid",
        "cant_happen_before": [1],
        "must_happen_before": [3],
        "attach_after_number": 3,
    }
