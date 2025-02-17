import os
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QVBoxLayout, QWidget)
from app.core.image_cache_manager import cache_image_if_needed

class SingleAlbumView(QWidget):
    back_clicked = pyqtSignal()
    track_clicked = pyqtSignal(int)  # emit the track index (1-based)

    def __init__(self, albums_manager, album_title, shared_or_separate, shared_directory, separate_directories):
        super().__init__()
        self.albums_manager = albums_manager
        self.album_title = album_title
        self.shared_or_separate = shared_or_separate
        self.shared_directory = shared_directory
        self.separate_directories = separate_directories
        self.last_track_list_scroll_pos = 0

        album = self.get_album_data(album_title)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        top_hlayout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_clicked)
        top_hlayout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        main_layout.addLayout(top_hlayout)

        # Attempt to cache and load a 500x500 image
        large_art_path = cache_image_if_needed(
            album,
            self.shared_or_separate,
            self.shared_directory,
            self.separate_directories,
            width=500,
            height=500,
            format="JPG",
            quality=95
        )

        art_label = QLabel()
        pix = QPixmap(large_art_path) if large_art_path and os.path.exists(large_art_path) else QPixmap()
        if pix.isNull():
            art_label.setText("[No Art]")
            art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            art_height = 500
        else:
            art_label.setPixmap(pix)
            art_height = pix.height()

        title_label = QLabel(album_title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        left_col = QVBoxLayout()
        left_col.setSpacing(0)
        left_col.addWidget(art_label, alignment=Qt.AlignmentFlag.AlignCenter)
        left_col.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)

        self.track_list_widget = QListWidget()
        tracks = album.get('tracks', [])
        font_metrics = self.track_list_widget.fontMetrics()
        max_width = 0
        for i, track in enumerate(tracks, start=1):
            item_text = f"{i}. {track['track_title']}"
            item = QListWidgetItem(item_text)
            self.track_list_widget.addItem(item)
            text_width = font_metrics.horizontalAdvance(item_text)
            if text_width > max_width:
                max_width = text_width

        max_width += 30
        title_height = title_label.sizeHint().height()
        desired_height = art_height + title_height
        self.track_list_widget.setFixedWidth(max_width)
        self.track_list_widget.setFixedHeight(desired_height)

        # Connect item click
        self.track_list_widget.itemClicked.connect(self.on_track_item_clicked)

        center_widget = QWidget()
        center_hlayout = QHBoxLayout(center_widget)
        center_hlayout.setContentsMargins(0, 0, 0, 0)
        center_hlayout.setSpacing(20)
        center_hlayout.addLayout(left_col)
        center_hlayout.addWidget(self.track_list_widget)

        wrapper_layout = QHBoxLayout()
        wrapper_layout.addStretch(1)
        wrapper_layout.addWidget(center_widget)
        wrapper_layout.addStretch(1)

        center_vertical_layout = QVBoxLayout()
        center_vertical_layout.addStretch(1)
        center_vertical_layout.addLayout(wrapper_layout)
        center_vertical_layout.addStretch(1)

        main_layout.addLayout(center_vertical_layout)
        self.setLayout(main_layout)

    def get_album_data(self, title):
        all_albums = self.albums_manager.get_albums()
        for album in all_albums:
            if album['title'] == title:
                return album
        return {}

    def get_scroll_position(self):
        # For now, QListWidget doesn't directly give scroll position easily,
        # but we can access the scrollbar value:
        return self.track_list_widget.verticalScrollBar().value()

    def set_scroll_position(self, value):
        self.track_list_widget.verticalScrollBar().setValue(value)

    def on_track_item_clicked(self, item):
        # Determine which track was clicked by index
        row = self.track_list_widget.row(item)
        track_index = row + 1  # Convert to 1-based index as per album.json indexing
        self.last_track_list_scroll_pos = self.get_scroll_position()
        self.track_clicked.emit(track_index)
