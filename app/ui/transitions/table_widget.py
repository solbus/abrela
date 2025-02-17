from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem
from app.core.image_cache_manager import get_cached_image_path

class TransitionsTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(["#", "@", "", "Track", "Album", "Starting at"])
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

    def populate_table(self, album, track, current_track_index, default_exists, transitions):
        """
        :param album: The current album dict
        :param track: The current track dict
        :param current_track_index: int
        :param default_exists: bool (pre-determined by transitions_logic)
        :param transitions: list of custom transitions, already filtered
        """
        # The table will just trust these parameters
        # Determine total rows
        row_count = len(transitions) + (1 if default_exists else 0)
        self.setRowCount(row_count)

        # If 'default_exists' is True, fill row 0 with 'Default' info
        row = 0
        if default_exists:
            all_tracks = album['tracks']
            # Next track in this album
            next_track = all_tracks[current_track_index]
            self.set_table_row(
                row,
                index_label="Default",
                timestamp_label="End",
                art_album_title=album['title'],
                track_title=next_track['track_title'],
                album_title=album['title'],
                starting_at_label="Beginning"
            )
            row += 1

        # Fill the rest from 'transitions'
        for i, t in enumerate(transitions, start=1):
            from app.core.transitions_logic import ms_to_mmss
            timestamp_label = ms_to_mmss(t['timestamp'])
            starting_at_label = ms_to_mmss(t['target_fade_in_timestamp'])
            target_album_title = t.get('target_album', album['title']) or album['title']

            self.set_table_row(
                row,
                index_label=str(i), 
                timestamp_label=timestamp_label,
                art_album_title=target_album_title,
                track_title=t['target_track'],
                album_title=target_album_title,
                starting_at_label=starting_at_label
            )
            row += 1

        # Finally, adjust sizing
        self.adjust_table_size()

    def set_table_row(self, row, index_label, timestamp_label, art_album_title, track_title, album_title, starting_at_label):
        item_index = QTableWidgetItem(index_label)
        self.setItem(row, 0, item_index)

        item_timestamp = QTableWidgetItem(timestamp_label)
        self.setItem(row, 1, item_timestamp)

        art_label = QLabel()
        art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        art_path = get_cached_image_path(art_album_title, 175, 175)
        pix = QPixmap(art_path)
        if pix.isNull():
            art_label.setText("[No Art]")
            art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            pix = pix.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)
            art_label.setPixmap(pix)
        self.setCellWidget(row, 2, art_label)

        item_track = QTableWidgetItem(track_title)
        self.setItem(row, 3, item_track)

        item_album = QTableWidgetItem(album_title)
        self.setItem(row, 4, item_album)

        item_start = QTableWidgetItem(starting_at_label)
        self.setItem(row, 5, item_start)

    def adjust_table_size(self):
        self.resizeRowsToContents()
        self.resizeColumnsToContents()

        # Calculate how wide the columns need to be
        total_width = 0
        for col in range(self.columnCount()):
            total_width += self.columnWidth(col)
        total_width += 20  # some padding

        self.setMinimumWidth(total_width)
        self.resizeRowsToContents()
