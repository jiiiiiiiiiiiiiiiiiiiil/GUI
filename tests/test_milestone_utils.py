import pandas as pd
from pathlib import Path

from milestone_utils import load_milestones


REQUIRED_COLUMNS = [
    "Milestone",
    "Scene Title",
    "Milestone ID",
    "Scene ID",
]


def write_milestones_excel(path: Path, rows: list[dict], columns=None):
    if columns is None:
        columns = REQUIRED_COLUMNS
    df = pd.DataFrame(rows, columns=columns)
    df.to_excel(path, index=False)


# -------------------------
# Test 1: leere Datei
# -------------------------

def test_load_milestones_empty_file(tmp_path):
    milestones_path = tmp_path / "Milestones.xlsx"
    write_milestones_excel(milestones_path, [])

    result = load_milestones(milestones_path)

    assert result == []


# -------------------------
# Test 2: einzelner Milestone
# -------------------------

def test_load_milestones_single_entry(tmp_path):
    milestones_path = tmp_path / "Milestones.xlsx"
    write_milestones_excel(
        milestones_path,
        [
            {
                "Milestone": "Leni wird volljährig",
                "Scene Title": "Lenis Geburtstag",
                "Milestone ID": 0,
                "Scene ID": 2,
            }
        ],
    )

    result = load_milestones(milestones_path)

    assert result == [
        {
            "id": 0,
            "name": "Leni wird volljährig",
            "scene_id": 2,
            "scene_title": "Lenis Geburtstag",
        }
    ]


# -------------------------
# Test 3: mehrere Milestones, unsortierte IDs
# -------------------------

def test_load_milestones_sorted_by_id(tmp_path):
    milestones_path = tmp_path / "Milestones.xlsx"
    write_milestones_excel(
        milestones_path,
        [
            {
                "Milestone": "C",
                "Scene Title": "Scene C",
                "Milestone ID": 3,
                "Scene ID": 3,
            },
            {
                "Milestone": "A",
                "Scene Title": "Scene A",
                "Milestone ID": 1,
                "Scene ID": 1,
            },
            {
                "Milestone": "B",
                "Scene Title": "Scene B",
                "Milestone ID": 2,
                "Scene ID": 2,
            },
        ],
    )

    result = load_milestones(milestones_path)

    assert [m["id"] for m in result] == [1, 2, 3]


# -------------------------
# Test 4: ungültige Milestones werden ignoriert
# -------------------------

def test_load_milestones_ignores_invalid_names(tmp_path):
    milestones_path = tmp_path / "Milestones.xlsx"
    write_milestones_excel(
        milestones_path,
        [
            {
                "Milestone": "Leni wird volljährig",
                "Scene Title": "Scene A",
                "Milestone ID": 0,
                "Scene ID": 1,
            },
            {
                "Milestone": "",
                "Scene Title": "Scene B",
                "Milestone ID": 1,
                "Scene ID": 2,
            },
            {
                "Milestone": "   ",
                "Scene Title": "Scene C",
                "Milestone ID": 2,
                "Scene ID": 3,
            },
            {
                "Milestone": None,
                "Scene Title": "Scene D",
                "Milestone ID": 3,
                "Scene ID": 4,
            },
        ],
    )

    result = load_milestones(milestones_path)

    assert result == [
        {
            "id": 0,
            "name": "Leni wird volljährig",
            "scene_id": 1,
            "scene_title": "Scene A",
        }
    ]


# -------------------------
# Test 5: fehlende Spalte → leere Rückgabe
# -------------------------

def test_load_milestones_missing_required_column_returns_empty(tmp_path):
    milestones_path = tmp_path / "Milestones.xlsx"

    write_milestones_excel(
        milestones_path,
        [
            {
                "Milestone": "Something happens",
                "Scene Title": "Some Scene",
                "Milestone ID": 0,
                "Scene ID": 1,
            }
        ],
        columns=[
            "Milestone",
            "Scene Title",
            "Milestone ID",
            # "Scene ID" fehlt absichtlich
        ],
    )

    result = load_milestones(milestones_path)

    assert result == []
