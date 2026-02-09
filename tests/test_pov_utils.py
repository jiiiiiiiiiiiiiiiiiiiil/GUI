import pandas as pd
from pathlib import Path

from pov_utils import get_all_povs, get_most_common_pov


REQUIRED_COLUMNS = [
    "Number",
    "ID",
    "Title",
    "Content",
    "POV",
    "Can't happen before",
    "Must happen before",
    "Status",
]


def write_scenes_excel(path: Path, pov_values: list):
    rows = []
    for i, pov in enumerate(pov_values, start=1):
        rows.append(
            {
                "Number": i,
                "ID": i - 1,
                "Title": f"Scene {i}",
                "Content": "",
                "POV": pov,
                "Can't happen before": "",
                "Must happen before": "",
                "Status": "",
            }
        )

    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
    df.to_excel(path, index=False)


# -------------------------
# Test 1: leere Datei
# -------------------------

def test_get_povs_empty_file(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(scenes_path, [])

    assert get_all_povs(scenes_path) == []
    assert get_most_common_pov(scenes_path) is None


# -------------------------
# Test 2: einzelner POV
# -------------------------

def test_get_povs_single_value(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(scenes_path, ["Leni"])

    assert get_all_povs(scenes_path) == ["Leni"]
    assert get_most_common_pov(scenes_path) == "Leni"


# -------------------------
# Test 3: klare Mehrheit
# -------------------------

def test_get_povs_clear_majority(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(scenes_path, ["Leni", "Leni", "Mia"])

    assert get_all_povs(scenes_path) == ["Leni", "Leni", "Mia"]
    assert get_most_common_pov(scenes_path) == "Leni"


# -------------------------
# Test 4: Gleichstand → erster gewinnt
# -------------------------

def test_get_povs_tie_returns_first(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(scenes_path, ["Leni", "Mia", "Mia", "Leni"])

    assert get_all_povs(scenes_path) == ["Leni", "Mia", "Mia", "Leni"]
    assert get_most_common_pov(scenes_path) == "Leni"


# -------------------------
# Test 5: leere / ungültige Werte
# -------------------------

def test_get_povs_ignores_empty_and_invalid(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(scenes_path, ["Leni", "", " ", None, "Mia"])

    assert get_all_povs(scenes_path) == ["Leni", "Mia"]
    assert get_most_common_pov(scenes_path) == "Leni"
