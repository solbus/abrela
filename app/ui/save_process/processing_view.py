from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
)

class ProcessingView(QWidget):
    exit_requested = pyqtSignal()
    start_over_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(5)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # "Processing..."
        self.processing_label = QLabel("Processing...")
        self.processing_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.processing_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.main_layout.addWidget(self.processing_label)

        # Percentage label
        self.percent_label = QLabel("0%")
        self.percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.percent_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setFixedWidth(200)
        self.main_layout.addWidget(self.progress_bar, 0, Qt.AlignmentFlag.AlignCenter)

        # Initially hidden final message and buttons
        self.done_label = QLabel("All done!<br><br>Go to the location you selected on your computer to find the MP3<br>")
        self.done_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.done_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.done_label.hide()
        self.main_layout.addWidget(self.done_label)

        button_layout = QHBoxLayout()
        self.exit_button = QPushButton("Exit")
        self.exit_button.clicked.connect(self.exit_requested.emit)
        self.exit_button.hide()

        self.start_over_button = QPushButton("Start over")
        self.start_over_button.clicked.connect(self.start_over_requested.emit)
        self.start_over_button.hide()

        button_layout.addStretch()
        button_layout.addWidget(self.start_over_button)
        button_layout.addSpacing(20)
        button_layout.addWidget(self.exit_button)
        button_layout.addStretch()

        self.main_layout.addLayout(button_layout)

        self.setLayout(self.main_layout)

    def update_progress_external(self, pct: int):
        self.progress_bar.setValue(pct)
        self.percent_label.setText(f"{pct}%")
        if pct >= 100:
            self.show_done_message()

    def show_done_message(self):
        self.processing_label.hide()
        self.percent_label.hide()
        self.progress_bar.hide()
        self.done_label.show()
        self.exit_button.show()
        self.start_over_button.show()
