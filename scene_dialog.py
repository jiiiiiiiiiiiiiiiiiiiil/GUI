from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QPushButton,
)
from PySide6.QtCore import Qt


class SceneDialog(QDialog):
    def __init__(
        self,
        *,
        existing_scene: dict | None,
        available_povs: list[str],
        default_pov: str | None,
        milestones: list[dict],
        max_scene_number: int,
        parent=None,
    ):
        super().__init__(parent)

        self.setWindowTitle("Edit Scene" if existing_scene else "Create Scene")
        self.resize(500, 600)

        self._milestones = milestones

        layout = QVBoxLayout(self)

        # -------- Title --------
        layout.addWidget(QLabel("Title"))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        # -------- Content --------
        layout.addWidget(QLabel("Content"))
        self.content_input = QTextEdit()
        layout.addWidget(self.content_input)

        # -------- POV --------
        layout.addWidget(QLabel("POV"))

        pov_layout = QHBoxLayout()
        self.pov_dropdown = QComboBox()
        self.pov_dropdown.addItem("")
        for pov in available_povs:
            self.pov_dropdown.addItem(pov)

        if default_pov:
            index = self.pov_dropdown.findText(default_pov)
            if index >= 0:
                self.pov_dropdown.setCurrentIndex(index)

        self.pov_free_text = QLineEdit()
        self.pov_free_text.setPlaceholderText("Override POV")

        pov_layout.addWidget(self.pov_dropdown)
        pov_layout.addWidget(self.pov_free_text)
        layout.addLayout(pov_layout)

        # -------- Status --------
        layout.addWidget(QLabel("Status"))
        self.status_dropdown = QComboBox()
        for status in ["raw", "solid", "very solid", "finalised"]:
            self.status_dropdown.addItem(status)
        layout.addWidget(self.status_dropdown)

        # -------- Milestones --------
        layout.addWidget(QLabel("Can't happen before"))
        self.cant_list = QListWidget()
        self.cant_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.cant_list)

        layout.addWidget(QLabel("Must happen before"))
        self.must_list = QListWidget()
        self.must_list.setSelectionMode(QListWidget.MultiSelection)
        layout.addWidget(self.must_list)

        for m in milestones:
            label = f'{m["id"]} – {m["name"]}'
            cant_item = QListWidgetItem(label)
            cant_item.setData(Qt.UserRole, m["id"])
            self.cant_list.addItem(cant_item)

            must_item = QListWidgetItem(label)
            must_item.setData(Qt.UserRole, m["id"])
            self.must_list.addItem(must_item)

        # -------- Attach after --------
        layout.addWidget(QLabel("Attach after scene #"))
        self.attach_spin = QSpinBox()
        self.attach_spin.setMinimum(0)
        self.attach_spin.setMaximum(max_scene_number)
        layout.addWidget(self.attach_spin)

        # -------- Buttons --------
        button_layout = QHBoxLayout()
        self.confirm_button = QPushButton("Confirm")
        self.confirm_button.setEnabled(False)
        cancel_button = QPushButton("Cancel")

        button_layout.addStretch()
        button_layout.addWidget(self.confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        cancel_button.clicked.connect(self.reject)
        self.confirm_button.clicked.connect(self.accept)

        # -------- Signals --------
        self.title_input.textChanged.connect(self._update_confirm_state)
        self.pov_dropdown.currentTextChanged.connect(self._update_confirm_state)
        self.pov_free_text.textChanged.connect(self._update_confirm_state)
        self.cant_list.itemSelectionChanged.connect(self._update_confirm_state)
        self.must_list.itemSelectionChanged.connect(self._update_confirm_state)

        # -------- Prefill (Edit) --------
        if existing_scene:
            self._prefill(existing_scene)

        self._update_confirm_state()

    # =========================
    # Internal helpers
    # =========================

    def _prefill(self, scene: dict):
        self.title_input.setText(scene.get("title", ""))
        self.content_input.setText(scene.get("content", ""))

        pov = scene.get("pov", "")
        if pov:
            index = self.pov_dropdown.findText(pov)
            if index >= 0:
                self.pov_dropdown.setCurrentIndex(index)
            else:
                self.pov_free_text.setText(pov)

        status = scene.get("status")
        if status:
            index = self.status_dropdown.findText(status)
            if index >= 0:
                self.status_dropdown.setCurrentIndex(index)

        self.attach_spin.setValue(scene.get("attach_after_number", 0))

    def _selected_ids(self, widget: QListWidget) -> set[int]:
        return {
            item.data(Qt.UserRole)
            for item in widget.selectedItems()
        }

    def _update_confirm_state(self):
        title_ok = bool(self.title_input.text().strip())

        pov_text = self.pov_free_text.text().strip()
        pov_ok = bool(pov_text or self.pov_dropdown.currentText().strip())

        cant_ids = self._selected_ids(self.cant_list)
        must_ids = self._selected_ids(self.must_list)
        no_overlap = cant_ids.isdisjoint(must_ids)

        self.confirm_button.setEnabled(title_ok and pov_ok and no_overlap)

    # =========================
    # Public API
    # =========================

    def get_result(self) -> dict:
        pov = (
            self.pov_free_text.text().strip()
            if self.pov_free_text.text().strip()
            else self.pov_dropdown.currentText().strip()
        )

        return {
            "title": self.title_input.text().strip(),
            "content": self.content_input.toPlainText(),
            "pov": pov,
            "status": self.status_dropdown.currentText(),
            "cant_happen_before": sorted(self._selected_ids(self.cant_list)),
            "must_happen_before": sorted(self._selected_ids(self.must_list)),
            "attach_after_number": self.attach_spin.value(),
        }
