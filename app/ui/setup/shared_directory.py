from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

class SharedDirectoryStep(QWidget):
    continue_clicked = pyqtSignal(str, bool)  # directory, remember

    def __init__(self, flow_controller, parent=None):
        super().__init__(parent)
        self.flow_controller = flow_controller

        # Main vertical layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Instruction label, centered
        label = QLabel("What folder do you have all the album folders in?<br><b>Important:</b> All ZIPs must be extracted first!")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        # Directory input layout
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(10)
        dir_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.dir_edit = QLineEdit()
        self.dir_edit.setFixedWidth(400)  # Text entry box width

        browse_button = QPushButton("Browse...")
        browse_button.setFixedWidth(80)  # Browse button width
        browse_button.clicked.connect(self.browse_directory)

        dir_layout.addWidget(self.dir_edit)
        dir_layout.addWidget(browse_button)
        layout.addLayout(dir_layout)

        # Remember directory checkbox, centered
        self.remember_checkbox = QCheckBox("Remember folder")
        layout.addWidget(self.remember_checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

        # Bottom button layout
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.on_continue_clicked)
        button_layout.addWidget(continue_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def browse_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        if directory:
            self.dir_edit.setText(directory)

    def on_continue_clicked(self):
        directory = self.dir_edit.text().strip()
        remember = self.remember_checkbox.isChecked()
        self.continue_clicked.emit(directory, remember)
