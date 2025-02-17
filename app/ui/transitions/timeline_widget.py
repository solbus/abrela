import random
from PyQt6.QtCore import pyqtSignal, QRect, Qt
from PyQt6.QtGui import QColor, QPainter
from PyQt6.QtWidgets import QWidget, QToolTip, QSizePolicy

from app.core.transitions_logic import (
    ms_to_mmss, 
    ms_diff_to_minsec,
    sum_segments_duration
)

def random_color():
    # Generate a moderately bright random color
    r = random.randint(80, 200)
    g = random.randint(80, 200)
    b = random.randint(80, 200)
    return (r, g, b)

def blend_color(c1, c2):
    # Blend two colors by averaging their components
    return ((c1[0] + c2[0]) // 2,
            (c1[1] + c2[1]) // 2,
            (c1[2] + c2[2]) // 2)

class TimelineWidget(QWidget):
    segment_clicked = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.segments = []
        self.track_colors = {}
        self.setMinimumHeight(60)
        self.setMaximumHeight(60)
        self.hovered_segment = -1
        self.setMouseTracking(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

    def set_segments(self, segments):
        self.segments = segments

        # Check how many tracks and transitions we have
        track_count = sum(1 for s in self.segments if s['segment_type'] == 'track')
        transition_count = sum(1 for s in self.segments if s['segment_type'] == 'transition')

        # If there's more than one track or at least one transition, we lock colors
        lock_colors = (track_count > 1 or transition_count > 0)

        # Assign colors to track segments
        for seg in self.segments:
            if seg['segment_type'] == 'track':
                key = (seg['album_title'], seg['track_title'])
                if lock_colors:
                    # Lock colors: use stored color if available, else assign new
                    if key in self.track_colors:
                        seg['color'] = self.track_colors[key]
                    else:
                        new_color = random_color()
                        self.track_colors[key] = new_color
                        seg['color'] = new_color
                else:
                    # Not locked yet: generate a new random color each time
                    # BUT still store it in track_colors so that once transitions appear,
                    # remember the last chosen color.
                    new_color = random_color()
                    seg['color'] = new_color
                    self.track_colors[key] = new_color

        # Call blender helper
        self._blend_transition_segments()

        self.update()
    
    def _blend_transition_segments(self):
        for i, seg in enumerate(self.segments):
            if seg['segment_type'] == 'transition':
                if i > 0 and i < len(self.segments) - 1:
                    prev_seg = self.segments[i - 1]
                    next_seg = self.segments[i + 1]
                    if prev_seg['segment_type'] == 'track' and next_seg['segment_type'] == 'track':
                        seg['color'] = blend_color(prev_seg['color'], next_seg['color'])
                    else:
                        seg['color'] = (200, 200, 100)
                else:
                    seg['color'] = (200, 200, 100)

    def paintEvent(self, event):
        painter = QPainter(self)
        rect = self.rect()
        painter.fillRect(rect, QColor(40, 40, 40))

        if not self.segments:
            return

        total_duration = sum_segments_duration(self.segments)
        if total_duration <= 0:
            return

        x = rect.x()
        y = rect.y()
        h = rect.height()

        for i, seg in enumerate(self.segments):
            if seg['segment_type'] == 'track':
                seg_duration = seg['end_ms'] - seg['start_ms']
            else:
                seg_duration = seg['duration']

            # If this is NOT the last segment, do the usual calculation:
            if i < len(self.segments) - 1:
                seg_width = int((seg_duration / total_duration) * rect.width())
            else:
                # Last segment: fill whatever space remains
                seg_width = rect.width() - (x - rect.x())

            # Paint the segment
            r, g, b = seg['color']
            color = QColor(r, g, b)
            painter.fillRect(QRect(x, y, seg_width, h), color)

            # Store for mouse hit detection
            seg['rect'] = QRect(x, y, seg_width, h)

            x += seg_width

    def total_duration_ms(self):
        total = 0
        for seg in self.segments:
            if seg['segment_type'] == 'track':
                total += (seg['end_ms'] - seg['start_ms'])
            else:
                total += seg['duration']
        return total

    def mouseMoveEvent(self, event):
        pos = event.pos()
        hovered = -1
        for i, seg in enumerate(self.segments):
            if 'rect' in seg and seg['rect'].contains(pos):
                hovered = i
                break

        if hovered != self.hovered_segment:
            self.hovered_segment = hovered
            if hovered >= 0:
                seg = self.segments[hovered]
                # Set cursor based on segment type
                if seg['segment_type'] == 'track':
                    self.setCursor(Qt.CursorShape.PointingHandCursor)
                else:
                    # Transition segment
                    self.setCursor(Qt.CursorShape.ArrowCursor)

                tooltip_text = self.get_tooltip_for_segment(hovered)
                if tooltip_text:
                    QToolTip.showText(self.mapToGlobal(pos), tooltip_text, self)
                else:
                    QToolTip.hideText()
            else:
                QToolTip.hideText()
                self.setCursor(Qt.CursorShape.ArrowCursor)  # No segment hovered
        super().mouseMoveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.hovered_segment >= 0:
            seg = self.segments[self.hovered_segment]
            if seg['segment_type'] == 'track':
                # Check if this is the last track segment
                if self.hovered_segment == len(self.segments) - 1:
                    # Last track segment clicked: re-randomize its color
                    key = (seg['album_title'], seg['track_title'])
                    new_color = random_color()
                    seg['color'] = new_color
                    self.track_colors[key] = new_color

                    # After re-randomizing track color, re-blend transitions
                    self._blend_transition_segments()
                    self.update()
                else:
                    # Not the last track segment: revert timeline
                    self.segment_clicked.emit(self.hovered_segment)
        super().mousePressEvent(event)

    def leaveEvent(self, event):
        self.hovered_segment = -1
        QToolTip.hideText()
        super().leaveEvent(event)

    def get_tooltip_for_segment(self, idx):
        seg = self.segments[idx]
        if seg['segment_type'] == 'track':
            start_offset = seg['start_ms']
            end_offset = seg['end_ms']
            from_str = ms_to_mmss(start_offset)
            to_str = ms_to_mmss(end_offset)
            diff_str = ms_diff_to_minsec(end_offset - start_offset)

            return (f"{from_str} to {to_str}\n"
                    f"{diff_str}\n"
                    f"{seg['track_title']} - {seg['album_title']}\n\n"
                    f"Click to start over from here")
        else:
            # For transition segments, show total transition time
            seg_duration = seg['duration']
            sec = seg_duration // 1000
            return f"Transition\n{sec}sec"
