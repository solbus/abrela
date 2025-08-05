from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
    QHBoxLayout,
)


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
        self.label.setWordWrap(True)
        self.label.setFixedWidth(200)
        layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Busy indicator
        self.progress.setFixedWidth(200)

        progress_row = QHBoxLayout()
        progress_row.addStretch()
        progress_row.addWidget(self.progress)
        progress_row.addStretch()
        layout.addLayout(progress_row)

        layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.setLayout(layout)
        self.adjustSize()
