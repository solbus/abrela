from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QLabel, QPushButton, QHBoxLayout, QFileDialog
)

class UpdateDataDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Update Album Data")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        self.selected_file = None

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Paste new albums.json contents here")
        self.text_edit.setMinimumHeight(200)
        layout.addWidget(self.text_edit)

        or_label = QLabel("OR")
        or_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(or_label)

        file_button = QPushButton("Select new albums.json")
        file_button.clicked.connect(self.select_file)
        layout.addWidget(file_button, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        update_button = QPushButton("Update")
        update_button.clicked.connect(self.accept)
        button_layout.addStretch(1)
        button_layout.addWidget(cancel_button)
        button_layout.addWidget(update_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select albums.json", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.selected_file = file_path

    def get_data(self):
        if self.selected_file:
            try:
                with open(self.selected_file, 'r', encoding='utf-8') as f:
                    return f.read()
            except Exception:
                return ""
        return self.text_edit.toPlainText()
