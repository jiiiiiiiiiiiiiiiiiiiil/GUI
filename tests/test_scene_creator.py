import pandas as pd
from pathlib import Path

from scene_creator import create_scene


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


def write_scenes_excel(path: Path, rows: list[dict]):
    df = pd.DataFrame(rows, columns=REQUIRED_COLUMNS)
    df.to_excel(path, index=False)


def read_scenes_excel(path: Path) -> pd.DataFrame:
    return pd.read_excel(path)


# -------------------------
# Test 1: erste Szene in leere Datei
# -------------------------

def test_create_scene_first_scene(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(scenes_path, [])

    create_scene(
        scenes_path=scenes_path,
        title="Scene 1",
        content="Content",
        pov="Alice",
        status="Draft",
        cant_happen_before="",
        must_happen_before="",
        attach_after_number=0,
    )

    df = read_scenes_excel(scenes_path)

    assert len(df) == 1
    assert df.loc[0, "ID"] == 0
    assert df.loc[0, "Number"] == 1
    assert df.loc[0, "Title"] == "Scene 1"
    assert df.loc[0, "Content"] == "Content"
    assert df.loc[0, "POV"] == "Alice"
    assert df.loc[0, "Status"] == "Draft"


# -------------------------
# Test 2: Szene ans Ende anhängen
# -------------------------

def test_create_scene_append_to_end(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(
        scenes_path,
        [
            {"Number": 1, "ID": 0, "Title": "A", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
            {"Number": 2, "ID": 1, "Title": "B", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
            {"Number": 3, "ID": 2, "Title": "C", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
        ],
    )

    create_scene(
        scenes_path,
        "D",
        "Content",
        "Bob",
        "Draft",
        "",
        "",
        attach_after_number=3,
    )

    df = read_scenes_excel(scenes_path)

    assert list(df["Number"]) == [1, 2, 3, 4]
    assert list(df["ID"]) == [0, 1, 2, 3]


# -------------------------
# Test 3: Szene in der Mitte einfügen
# -------------------------

def test_create_scene_insert_in_middle(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(
        scenes_path,
        [
            {"Number": 1, "ID": 0, "Title": "A", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
            {"Number": 2, "ID": 1, "Title": "B", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
            {"Number": 3, "ID": 2, "Title": "C", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
        ],
    )

    create_scene(
        scenes_path,
        "New",
        "Content",
        "Carol",
        "Draft",
        "",
        "",
        attach_after_number=1,
    )

    df = read_scenes_excel(scenes_path)

    assert list(df["Number"]) == [1, 2, 3, 4]
    assert df.loc[df["Title"] == "New", "Number"].item() == 2
    assert df.loc[df["Title"] == "B", "Number"].item() == 3
    assert df.loc[df["Title"] == "C", "Number"].item() == 4


# -------------------------
# Test 4: IDs bleiben stabil
# -------------------------

def test_create_scene_ids_are_stable(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(
        scenes_path,
        [
            {"Number": 1, "ID": 10, "Title": "A", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
            {"Number": 2, "ID": 42, "Title": "B", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
        ],
    )

    create_scene(
        scenes_path,
        "New",
        "Content",
        "Dana",
        "Draft",
        "",
        "",
        attach_after_number=1,
    )

    df = read_scenes_excel(scenes_path)

    existing_ids = set(df[df["Title"].isin(["A", "B"])]["ID"])
    assert existing_ids == {10, 42}

    new_id = df.loc[df["Title"] == "New", "ID"].item()
    assert new_id == 43


# -------------------------
# Test 5: Sortierung nach Schreiben
# -------------------------

def test_create_scene_results_sorted_by_number(tmp_path):
    scenes_path = tmp_path / "Scenes.xlsx"
    write_scenes_excel(
        scenes_path,
        [
            {"Number": 2, "ID": 1, "Title": "B", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
            {"Number": 1, "ID": 0, "Title": "A", "Content": "", "POV": "X",
             "Can't happen before": "", "Must happen before": "", "Status": ""},
        ],
    )

    create_scene(
        scenes_path,
        "New",
        "Content",
        "Eve",
        "Draft",
        "",
        "",
        attach_after_number=0,
    )

    df = read_scenes_excel(scenes_path)

    assert list(df["Number"]) == sorted(df["Number"])
