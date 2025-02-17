from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QWidget
from app.core.image_cache_manager import get_cached_image_path

class TransitionsCurrentTrackInfoWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(10)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(self.layout)

        self.art_label = QLabel()
        self.layout.addWidget(self.art_label)

        self.track_label = QLabel()
        self.track_label.setTextFormat(Qt.TextFormat.RichText)
        self.layout.addWidget(self.track_label)

    def update_info(self, album, track):
        # Load art
        art_path = get_cached_image_path(album['title'], 175, 175)
        pix = QPixmap(art_path)
        if not pix.isNull():
            pix = pix.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)
            self.art_label.setPixmap(pix)
            self.art_label.setText("")
        else:
            self.art_label.setText("[No Art]")
            self.art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.track_label.setText(f"<b>{track['track_title']}</b> - {album['title']}")
