from pathlib import Path
import pandas as pd


def load_scenes(scenes_path: Path) -> list[dict]:
    df = pd.read_excel(scenes_path)

    df = df.sort_values("Number")

    scenes = []
    for _, row in df.iterrows():
        scenes.append({
            "number": int(row["Number"]),
            "id": int(row["ID"]),
            "title": row["Title"],
            "content": row["Content"] or "",
            "pov": row["POV"] or "—",
            "status": row.get("Status", "raw"),
        })

    return scenes
