from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QCheckBox, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget
)

from app.ui.setup.start_over_button import StartOverButton

class SelectAlbumsStep(QWidget):
    continue_clicked = pyqtSignal(list, bool)  # selected_albums, remember

    def __init__(self, albums_manager, flow_controller, parent=None):
        super().__init__(parent)
        self.albums_manager = albums_manager
        self.flow_controller = flow_controller
        self.album_checkboxes = []
        self.all_checked = False  # Track current state for toggle button

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        top_button_layout = QHBoxLayout()
        start_over_button = StartOverButton(self.flow_controller)
        top_button_layout.addWidget(start_over_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(top_button_layout)

        # Top row: label + toggle button centered
        top_row = QHBoxLayout()
        top_row.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Which albums do you have?")
        self.toggle_button = QPushButton("Check All")
        self.toggle_button.clicked.connect(self.toggle_all_checkboxes)

        # Add the label and toggle button side by side, centered
        top_row.addWidget(title_label)
        top_row.addSpacing(10)  # Small spacing between label and button
        top_row.addWidget(self.toggle_button)

        main_layout.addLayout(top_row)

        # Scroll area for albums
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0,0,0,0)
        container_layout.setSpacing(5)

        # Add album checkboxes
        albums = self.albums_manager.get_albums()

        for album in albums:
            cb = QCheckBox(album.get('title', 'Unknown Album'))
            self.album_checkboxes.append(cb)
            container_layout.addWidget(cb, alignment=Qt.AlignmentFlag.AlignLeft)

        container_layout.addStretch(1)

        scroll_area.setWidget(container)

        # Center the scroll_area horizontally with a fixed width
        scroll_area_container = QWidget()
        scroll_area_layout = QHBoxLayout(scroll_area_container)
        scroll_area_layout.setContentsMargins(0,0,0,0)
        scroll_area_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Fixed width for scroll area, 200 pixels
        fixed_width = 200
        scroll_area.setFixedWidth(fixed_width)

        scroll_area_layout.addWidget(scroll_area)

        main_layout.addWidget(scroll_area_container)

        # Remember selections checkbox, centered
        self.remember_checkbox = QCheckBox("Remember selections")
        main_layout.addWidget(self.remember_checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

        # Continue button, right-aligned
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        continue_button = QPushButton("Continue")
        continue_button.clicked.connect(self.on_continue_clicked)
        button_layout.addWidget(continue_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

    def toggle_all_checkboxes(self):
        if self.all_checked:
            for cb in self.album_checkboxes:
                cb.setChecked(False)
            self.toggle_button.setText("Check All")
            self.all_checked = False
        else:
            for cb in self.album_checkboxes:
                cb.setChecked(True)
            self.toggle_button.setText("Uncheck All")
            self.all_checked = True

    def on_continue_clicked(self):
        selected = [cb.text() for cb in self.album_checkboxes if cb.isChecked()]
        remember = self.remember_checkbox.isChecked()
        self.continue_clicked.emit(selected, remember)
