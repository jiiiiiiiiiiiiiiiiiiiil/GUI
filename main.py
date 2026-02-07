import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QFrame,
    QScrollArea,
    QMessageBox,
)

from excel_validator import (
    validate_excel_file,
    ValidationError,
    SCENES_REQUIRED_COLUMNS,
    MILESTONES_REQUIRED_COLUMNS,
)


# =========================
# PROJECT SETUP
# =========================

# TEMPORARY project path (replace later with config / dialog)
PROJECT_PATH = Path("C:/Users/jilra/Documents/Sonstiges/Bücher/GUI")  # <-- anpassen

project_valid = True
project_error_message = None

try:
    validate_excel_file(PROJECT_PATH / "Scenes.xlsx", SCENES_REQUIRED_COLUMNS)
    validate_excel_file(PROJECT_PATH / "Milestones.xlsx", MILESTONES_REQUIRED_COLUMNS)
except ValidationError as e:
    project_valid = False
    project_error_message = str(e)


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


# Disable project-related actions if project is invalid
if not project_valid:
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

if project_valid:
    from scene_loader import load_scenes

    scenes = load_scenes(PROJECT_PATH / "Scenes.xlsx")

    for scene in scenes:
        scene_box = QFrame()
        scene_box.setFrameShape(QFrame.Box)

        scene_layout = QVBoxLayout(scene_box)

        scene_layout.addWidget(
            QLabel(f'{scene["number"]}. {scene["title"]}')
        )
        scene_layout.addWidget(QLabel("—"))  # Milestones placeholder
        scene_layout.addWidget(QLabel(f'POV: {scene["pov"]}'))
        scene_layout.addWidget(QLabel("Word count: —"))

        toggle_button = QPushButton("▶")
        toggle_button.setCheckable(True)
        toggle_button.setChecked(False)
        toggle_button.setFixedWidth(24)
        toggle_button.setFlat(True)
        scene_layout.addWidget(toggle_button)

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
    # Placeholder when project is invalid
    scene_list_layout.addWidget(
        QLabel("No valid project loaded.\nPlease fix the project files or switch project.")
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


# =========================
# ERROR DIALOG (AFTER SHOW)
# =========================

if not project_valid:
    QMessageBox.critical(
        window,
        "Project load failed",
        f"The project could not be loaded:\n\n{project_error_message}\n\n"
        "Please fix the files or switch to another project.",
    )


sys.exit(app.exec())
