import sys
from pathlib import Path

from project_manager import ProjectManager
from scene_loader import load_scenes


def determine_start_state(project_manager) -> bool:
    project_path = project_manager.load_last_project()
    return project_path is not None


def open_project_selection_dialog():
    from PySide6.QtWidgets import QFileDialog

    path = QFileDialog.getExistingDirectory(
        None,
        "Select project folder",
        ""
    )

    if not path:
        return None

    return path


def show_fatal_error(message: str):
    from PySide6.QtWidgets import QMessageBox

    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("Project Error")
    msg.setText("The selected project could not be loaded.")
    msg.setInformativeText(message)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec()


def run_app():
    from PySide6.QtWidgets import (
        QApplication,
        QWidget,
        QVBoxLayout,
        QHBoxLayout,
        QLabel,
        QPushButton,
        QScrollArea,
        QFrame,
    )

    app = QApplication(sys.argv)

    project_manager = ProjectManager()
    project_loaded = determine_start_state(project_manager)

    # =========================
    # PROJECT SELECTION + INIT
    # =========================

    if not project_loaded:
        selected_path = open_project_selection_dialog()

        if selected_path is not None:
            try:
                project_manager.set_project(selected_path)
                project_loaded = True
            except Exception as e:
                show_fatal_error(str(e))
                sys.exit(1)

    # =========================
    # QT WINDOW
    # =========================

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
    # SCENE LIST (Phase D – old layout)
    # =========================

    scene_list_container = QWidget()
    scene_list_layout = QVBoxLayout(scene_list_container)
    scene_list_layout.addWidget(QLabel("Scenes"))

    if project_loaded:
        scenes_path = Path(project_manager.project_path) / "Scenes.xlsx"
        scenes = load_scenes(scenes_path)

        for scene in scenes:
            scene_box = QFrame()
            scene_box.setFrameShape(QFrame.Box)

            scene_layout = QVBoxLayout(scene_box)

            # --- Permanenter Bereich ---
            scene_layout.addWidget(
                QLabel(f'{scene["number"]}. {scene["title"]}')
            )
            scene_layout.addWidget(QLabel("—"))
            scene_layout.addWidget(QLabel(f'POV: {scene["pov"]}'))
            scene_layout.addWidget(QLabel("Word count: —"))
            scene_layout.addWidget(QLabel("Milestones: —"))

            # Toggle Button
            toggle_button = QPushButton("▶")
            toggle_button.setCheckable(True)
            toggle_button.setChecked(False)
            toggle_button.setFixedWidth(24)
            toggle_button.setFlat(True)
            scene_layout.addWidget(toggle_button)

            # --- Klappbarer Content ---
            content_container = QWidget()
            content_layout = QVBoxLayout(content_container)
            content_layout.setContentsMargins(0, 0, 0, 0)

            content_layout.addWidget(QLabel("Content:"))
            content_layout.addWidget(QLabel(scene["content"]))

            content_container.setVisible(False)
            scene_layout.addWidget(content_container)

            def toggle_content(checked, container=content_container, button=toggle_button):
                container.setVisible(checked)
                button.setText("▼" if checked else "▶")

            toggle_button.toggled.connect(toggle_content)

            scene_list_layout.addWidget(scene_box)

    else:
        scene_list_layout.addWidget(QLabel("No project loaded."))

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
