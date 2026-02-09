from pathlib import Path
from collections import Counter
import pandas as pd


def get_all_povs(scenes_path: Path) -> list[str]:
    """
    Returns all POV values from Scenes.xlsx.
    Empty, NaN or whitespace-only values are ignored.
    Duplicates are preserved.
    """
    df = pd.read_excel(scenes_path)

    if "POV" not in df.columns:
        return []

    povs: list[str] = []

    for value in df["POV"]:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned:
                povs.append(cleaned)

    return povs


def get_most_common_pov(scenes_path: Path) -> str | None:
    """
    Returns the most common POV.
    If multiple POVs share the highest count,
    the first one in appearance order is returned.
    Returns None if no POV exists.
    """
    povs = get_all_povs(scenes_path)

    if not povs:
        return None

    counts = Counter(povs)
    max_count = max(counts.values())

    for pov in povs:
        if counts[pov] == max_count:
            return pov

    return None
