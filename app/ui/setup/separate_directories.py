from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QCheckBox, QFileDialog, QHBoxLayout, QLabel, QLineEdit, QPushButton, QScrollArea, QWidget, QVBoxLayout
)

from app.ui.setup.start_over_button import StartOverButton

class SeparateDirectoriesStep(QWidget):
    continue_clicked = pyqtSignal(dict, bool)  # directories, remember

    def __init__(self, albums_manager, flow_controller, parent=None):
        super().__init__(parent)
        self.albums_manager = albums_manager
        self.flow_controller = flow_controller
        self.current_albums = []  # Holds the subset of albums if "some" scenario
        self.album_lineedits = {}

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        top_button_layout = QHBoxLayout()
        start_over_button = StartOverButton(self.flow_controller)
        top_button_layout.addWidget(start_over_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(top_button_layout)

        # Instruction label, centered
        self.instruction_label = QLabel("Specify folders for each album:")
        self.instruction_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.instruction_label)

        # Create a scroll area for the album list
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        # Container widget inside the scroll area
        self.albums_container = QWidget()
        self.albums_layout = QVBoxLayout(self.albums_container)
        self.albums_layout.setContentsMargins(0, 0, 0, 0)
        self.albums_layout.setSpacing(10)

        self.scroll_area.setWidget(self.albums_container)

        # Wrap scroll area in a container with fixed width and center it
        scroll_area_container = QWidget()
        scroll_area_layout = QHBoxLayout(scroll_area_container)
        scroll_area_layout.setContentsMargins(0,0,0,0)
        scroll_area_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Set a fixed width for the scroll area to avoid too much horizontal spacing.
        fixed_width = 700
        self.scroll_area.setFixedWidth(fixed_width)
        scroll_area_layout.addWidget(self.scroll_area)

        main_layout.addWidget(scroll_area_container)

        self.remember_checkbox = QCheckBox("Remember folders")
        main_layout.addWidget(self.remember_checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.on_continue_clicked)
        button_layout.addWidget(continue_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def set_albums(self, albums_titles):
        # Clear previous entries
        for i in reversed(range(self.albums_layout.count())):
            item = self.albums_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)

        self.album_lineedits.clear()

        # If empty list is provided, use all albums
        if not albums_titles:
            albums_titles = [a["title"] for a in self.albums_manager.get_albums()]

        self.current_albums = albums_titles

        # Add an entry row for each album
        for title in self.current_albums:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            lbl = QLabel(f"{title}")
            edit = QLineEdit()
            edit.setFixedWidth(400)
            browse_button = QPushButton("Browse...")
            browse_button.setFixedWidth(80)
            browse_button.clicked.connect(lambda checked, e=edit: self.browse_directory(e))

            row_layout.addWidget(lbl)
            row_layout.addWidget(edit)
            row_layout.addWidget(browse_button)

            self.albums_layout.addWidget(row_widget)
            self.album_lineedits[title] = edit

        # Add a stretch to push everything up if there's space
        self.albums_layout.addStretch(1)

    def browse_directory(self, line_edit):
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        if directory:
            line_edit.setText(directory)

    def on_continue_clicked(self):
        directories = {title: edit.text().strip() for title, edit in self.album_lineedits.items()}
        remember = self.remember_checkbox.isChecked()
        self.continue_clicked.emit(directories, remember)
