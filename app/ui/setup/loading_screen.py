from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QProgressBar, QVBoxLayout, QWidget

class LoadingScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout()
        
        # Center everything in the layout
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Margins for the window edges
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Control vertical spacing between widgets
        layout.setSpacing(5)

        self.loading_label = QLabel("Loading...")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.percent_label = QLabel("0%")
        self.percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar()
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        
        # Give the progress bar a fixed width
        self.progress_bar.setFixedWidth(200)

        layout.addWidget(self.loading_label)
        layout.addWidget(self.percent_label)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)

    def set_progress(self, value):
        self.progress_bar.setValue(value)
        self.percent_label.setText(f"{value}%")
