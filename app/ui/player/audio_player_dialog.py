from PyQt6.QtCore import Qt, QUrl, QPoint
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QToolTip,
    QStyle, QStyleOptionSlider, QSlider
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from app.core.transitions_logic import ms_to_mmss


class SeekSlider(QSlider):
    """QSlider that shows time tooltip on hover."""
    def __init__(self, parent=None):
        super().__init__(Qt.Orientation.Horizontal, parent)
        self.setMouseTracking(True)

    def _pixel_pos_to_range_value(self, x):
        option = QStyleOptionSlider()
        self.initStyleOption(option)
        groove = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, option,
            QStyle.SubControl.SC_SliderGroove, self
        )
        handle = self.style().subControlRect(
            QStyle.ComplexControl.CC_Slider, option,
            QStyle.SubControl.SC_SliderHandle, self
        )
        slider_min = groove.x()
        slider_max = groove.right() - handle.width() + 1
        x = max(slider_min, min(x, slider_max))
        return QStyle.sliderValueFromPosition(
            self.minimum(), self.maximum(), x - slider_min,
            slider_max - slider_min, option.upsideDown
        )

    def mouseMoveEvent(self, event):  # type: ignore[override]
        if self.maximum() > 0:
            ms = self._pixel_pos_to_range_value(int(event.position().x()))
            QToolTip.showText(event.globalPosition().toPoint(), ms_to_mmss(ms), self)
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton and self.maximum() > 0:
            ms = self._pixel_pos_to_range_value(int(event.position().x()))
            self.setValue(int(ms))
            self.sliderMoved.emit(int(ms))
            event.accept()
        super().mousePressEvent(event)


class AudioPlayerDialog(QDialog):
    """Floating audio player dialog with basic playback controls."""

    def __init__(self, audio_path, parent=None):
        super().__init__(parent)
        self.audio_path = audio_path
        self.drag_pos: QPoint | None = None

        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Dialog
        )
        self.setModal(False)

        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput()
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.setSource(QUrl.fromLocalFile(audio_path))

        self.slider = SeekSlider()
        self.slider.sliderMoved.connect(self.media_player.setPosition)

        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_play)

        close_btn = QPushButton("x")
        close_btn.setFixedWidth(20)
        close_btn.clicked.connect(self.close)

        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.addWidget(close_btn)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.slider)
        layout.addWidget(self.time_label)
        layout.addWidget(self.play_button, alignment=Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.on_state_changed)

    # --- Playback controls -------------------------------------------------
    def toggle_play(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()

    def update_position(self, position):
        self.slider.blockSignals(True)
        self.slider.setValue(position)
        self.slider.blockSignals(False)
        self.update_time_label()

    def update_duration(self, duration):
        self.slider.setRange(0, duration)
        self.update_time_label()

    def update_time_label(self):
        cur = self.media_player.position()
        total = self.media_player.duration() or 1
        self.time_label.setText(f"{ms_to_mmss(cur)} / {ms_to_mmss(total)}")

    def on_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.play_button.setText("Pause")
        else:
            self.play_button.setText("Play")

    # --- Window behavior ---------------------------------------------------
    def showEvent(self, event):  # type: ignore[override]
        super().showEvent(event)
        parent = self.parent()
        if parent:
            pr = parent.geometry()
            self.move(pr.center() - self.rect().center())

    def mousePressEvent(self, event):  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):  # type: ignore[override]
        if self.drag_pos and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):  # type: ignore[override]
        self.drag_pos = None
        super().mouseReleaseEvent(event)

    def closeEvent(self, event):  # type: ignore[override]
        self.media_player.stop()
        super().closeEvent(event)
