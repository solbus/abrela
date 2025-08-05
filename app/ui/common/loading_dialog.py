from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QProgressBar


class LoadingDialog(QDialog):
    """Simple modal dialog showing a spinner and message."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog)
        self.setModal(True)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.label = QLabel("Processing...\nPlease wait, this might take a minute or two.")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Busy indicator
        layout.addWidget(self.progress)

        self.setLayout(layout)
