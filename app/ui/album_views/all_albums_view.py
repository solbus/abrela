from PyQt6.QtCore import pyqtSignal, QSize, Qt
from PyQt6.QtGui import QMouseEvent, QPixmap
from PyQt6.QtWidgets import (
    QVBoxLayout, QLabel, QScrollArea, QSizePolicy, QWidget, QHBoxLayout
)

from app.core.image_cache_manager import get_cached_image_path
from app.ui.album_views.flow_layout import FlowLayout
from app.ui.setup.start_over_button import StartOverButton

class AlbumItemWidget(QWidget):
    clicked = pyqtSignal(str)

    def __init__(self, album_title, cached_art_path):
        super().__init__()
        self.album_title = album_title
        self.album_art_path = cached_art_path
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout()
        layout.setContentsMargins(0,0,0,0)
        layout.setSpacing(5)

        self.art_label = QLabel()
        self.art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pixmap = QPixmap(self.album_art_path)
        if pixmap.isNull():
            self.art_label.setText("[No Art]")
            self.art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.art_label.setPixmap(pixmap)

        self.title_label = QLabel(self.album_title)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setWordWrap(True)

        layout.addWidget(self.art_label)
        layout.addWidget(self.title_label)

        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.album_title)

    def sizeHint(self):
        return QSize(175, 200)


class AllAlbumsView(QWidget):
    album_clicked = pyqtSignal(str)

    def __init__(self, albums_manager, settings_manager, flow_controller, all_or_some, selected_albums, shared_or_separate, shared_directory=None, separate_directories=None):
        super().__init__()
        self.albums_manager = albums_manager
        self.settings_manager = settings_manager
        self.flow_controller = flow_controller
        self.all_or_some = all_or_some
        self.selected_albums = selected_albums
        self.shared_or_separate = shared_or_separate

        self.shared_directory = shared_directory if shared_directory is not None else self.settings_manager.settings.get("shared_directory", None)
        self.separate_directories = separate_directories if separate_directories else self.settings_manager.settings.get("separate_directories", {})

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(5)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0,0,0,0)
        container_layout.setSpacing(30)

        all_albums = self.albums_manager.get_albums()

        if self.all_or_some == "all":
            display_albums = all_albums
        else:
            display_albums = [a for a in all_albums if a['title'] in self.selected_albums]

        categories = {
            "Live": [],
            "Compilation": [],
            "Studio": []
        }

        for album in display_albums:
            album_type = album.get('type', '')
            if album_type in categories:
                categories[album_type].append(album)

        for cat_name in ["Live", "Compilation", "Studio"]:
            if categories[cat_name]:
                cat_label = QLabel(cat_name)
                cat_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                cat_label.setStyleSheet("font-weight: bold; font-size: 22px;")
                container_layout.addWidget(cat_label, alignment=Qt.AlignmentFlag.AlignHCenter)

                flow_widget = QWidget()
                flow_layout = FlowLayout(margin=0, hSpacing=20, vSpacing=20)
                flow_widget.setLayout(flow_layout)
                flow_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

                for album in categories[cat_name]:
                    cached_art_path = get_cached_image_path(album['title'], 175, 175)
                    item_widget = AlbumItemWidget(album['title'], cached_art_path)
                    item_widget.clicked.connect(self.album_clicked)
                    flow_layout.addWidget(item_widget)

                container_layout.addWidget(flow_widget)

        container_layout.addStretch(1)

        scroll_area.setWidget(container)
        main_layout.addWidget(scroll_area)

        # Start Over button
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        start_over_button = StartOverButton(self.flow_controller)
        button_layout.addWidget(start_over_button)
        main_layout.addLayout(button_layout)

        # Version label right underneath
        version_label = QLabel("1.0.1")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(version_label)

        self.setLayout(main_layout)

    def get_scroll_position(self):
        scroll_area = self.findChild(QScrollArea)
        if scroll_area:
            return scroll_area.verticalScrollBar().value()
        return 0

    def set_scroll_position(self, value):
        scroll_area = self.findChild(QScrollArea)
        if scroll_area:
            scroll_area.verticalScrollBar().setValue(value)
