import sys
import os

from PySide6.QtWidgets import QApplication, QFileDialog

from config import get_last_project_path, set_last_project_path
from project_manager import load_project
from paths import set_project_path
from main_window import MainWindow


def select_project_via_dialog() -> str | None:
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.Directory)
    dialog.setOption(QFileDialog.ShowDirsOnly, True)

    if dialog.exec():
        return dialog.selectedFiles()[0]

    return None


def main():
    app = QApplication(sys.argv)

    project_path = get_last_project_path()

    if not project_path or not os.path.exists(project_path):
        project_path = select_project_via_dialog()
        if not project_path:
            sys.exit(0)
        set_last_project_path(project_path)

    set_project_path(project_path)
    load_project(project_path)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
