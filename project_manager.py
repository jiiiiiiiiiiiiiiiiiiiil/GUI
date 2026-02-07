from pathlib import Path

from project_initializer import ensure_project_structure


def load_project(project_path: str) -> None:
    """
    Initialisiert und validiert ein Projekt anhand des Projektpfads.
    Wird sowohl beim automatischen Laden als auch nach dem Project-Selection-Dialog verwendet.
    """
    project_dir = Path(project_path)

    if not project_dir.exists() or not project_dir.is_dir():
        raise RuntimeError("Projektpfad existiert nicht oder ist kein Ordner.")

    ensure_project_structure(project_dir)
