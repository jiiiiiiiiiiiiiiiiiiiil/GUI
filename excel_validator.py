from pathlib import Path
import pandas as pd


class ValidationError(Exception):
    pass


SCENES_REQUIRED_COLUMNS = [
    "Number",
    "ID",
    "Title",
    "Content",
    "POV",
    "Can't happen before",
    "Must happen before",
    "Status",
]

MILESTONES_REQUIRED_COLUMNS = [
    "Milestone",
    "Scene Title",
    "Milestone ID",
    "Scene ID",
]


def validate_excel_file(path: Path, required_columns: list[str]) -> None:
    if not path.exists():
        raise ValidationError(f"File not found: {path.name}")

    if not path.is_file():
        raise ValidationError(f"Path is not a file: {path.name}")

    if path.suffix.lower() not in [".xlsx", ".xls"]:
        raise ValidationError(f"{path.name} is not an Excel file")

    try:
        df = pd.read_excel(path)
    except Exception as e:
        raise ValidationError(f"{path.name} is not readable: {e}")

    missing_columns = [c for c in required_columns if c not in df.columns]
    if missing_columns:
        raise ValidationError(
            f"{path.name}: missing required columns: {', '.join(missing_columns)}"
        )
