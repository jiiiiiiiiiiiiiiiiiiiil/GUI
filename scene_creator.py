from pathlib import Path
import pandas as pd


def create_scene(
    scenes_path: Path,
    title: str,
    content: str,
    pov: str,
    status: str,
    cant_happen_before: str,
    must_happen_before: str,
    attach_after_number: int,
) -> None:
    """
    Inserts a new scene into Scenes.xlsx.

    - assigns new Scene ID = max(ID) + 1
    - inserts scene after given scene number
    - shifts following scene numbers
    - writes result back to Excel

    No GUI logic. No validation logic.
    """

    df = pd.read_excel(scenes_path)

    # ---------- ID ----------
    if df.empty:
        new_scene_id = 0
    else:
        new_scene_id = int(df["ID"].max()) + 1

    # ---------- Scene Number ----------
    new_scene_number = attach_after_number + 1

    # shift following scenes
    df.loc[df["Number"] >= new_scene_number, "Number"] += 1

    # ---------- New Row ----------
    new_row = {
        "Number": new_scene_number,
        "ID": new_scene_id,
        "Title": title,
        "Content": content,
        "POV": pov,
        "Can't happen before": cant_happen_before,
        "Must happen before": must_happen_before,
        "Status": status,
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # keep correct order
    df = df.sort_values("Number").reset_index(drop=True)

    # ---------- Write back ----------
    df.to_excel(scenes_path, index=False)
