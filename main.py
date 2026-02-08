import sys

from project_manager import ProjectManager


def determine_start_state(project_manager) -> bool:
    project_path = project_manager.load_last_project()
    return project_path is not None


def run_app():
    from PySide6.QtWidgets import (
        QApplication,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QScrollArea,
    )

    # =========================
    # APP START / PROJECT FLOW
    # =========================

    project_manager = ProjectManager()
    project_loaded = determine_start_state(project_manager)

    # =========================
    # QT APP
    # =========================

    app = QApplication(sys.argv)

    window = QWidget()
    window.setWindowTitle("Scene Manager")
    window.resize(900, 600)

    # =========================
    # TOP BAR
    # =========================

    top_bar = QHBoxLayout()

    total_word_count_label = QLabel("Total words: —")
    refresh_wc_button = QPushButton("Refresh word count")
    reset_button = QPushButton("Reset")
    create_scene_button = QPushButton("Create scene")
    switch_project_button = QPushButton("Switch project")
    save_button = QPushButton("Save")

    top_bar.addWidget(total_word_count_label)
    top_bar.addWidget(refresh_wc_button)
    top_bar.addWidget(reset_button)
    top_bar.addStretch()
    top_bar.addWidget(create_scene_button)
    top_bar.addWidget(switch_project_button)
    top_bar.addWidget(save_button)

    if not project_loaded:
        refresh_wc_button.setEnabled(False)
        reset_button.setEnabled(False)
        create_scene_button.setEnabled(False)
        save_button.setEnabled(False)

    # =========================
    # SCENE LIST
    # =========================

    scene_list_container = QWidget()
    scene_list_layout = QVBoxLayout(scene_list_container)
    scene_list_layout.addWidget(QLabel("Scenes"))

    if project_loaded:
        scene_list_layout.addWidget(
            QLabel("Project loaded.\n(Scene list will be shown after initialization.)")
        )
    else:
        scene_list_layout.addWidget(
            QLabel("No project loaded.\nPlease select a project folder.")
        )

    scene_list_layout.addStretch()

    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)
    scroll_area.setWidget(scene_list_container)

    # =========================
    # ROOT LAYOUT
    # =========================

    root_layout = QVBoxLayout()
    root_layout.addLayout(top_bar)
    root_layout.addWidget(scroll_area)

    window.setLayout(root_layout)
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    run_app()
