from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea,
    QRadioButton, QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)

from app.core.transitions_logic import compute_segments_from_timeline, ms_to_mmss
from app.core.image_cache_manager import get_cached_image_path

class SaveView(QWidget):
    back_clicked = pyqtSignal()
    confirm_clicked = pyqtSignal(str)  # Emit "long_mp3" or "separate_mp3s"

    def __init__(self, timeline_entries, parent=None):
        super().__init__(parent)
        self.timeline_entries = timeline_entries

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Top row with back button
        top_hlayout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.back_clicked.emit)
        top_hlayout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_hlayout.addStretch()
        main_layout.addLayout(top_hlayout)

        # Title
        title_label = QLabel("Save")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Compute segments
        segments = compute_segments_from_timeline(self.timeline_entries)

        # Create a table to display the final segments
        table = QTableWidget()
        table.setColumnCount(6)
        # The columns: 0:"Track / Transition", 1:"" (art), 2:"Track", 3:"Album",  4:"Start", 5:"End"
        table.setHorizontalHeaderLabels(["Track / Transition", "", "Track", "Album", "Start", "End"])
        table.verticalHeader().setVisible(False)
        table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.NoSelection)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)

        # Populate the table
        table_data = []
        total_duration_ms = 0
        for seg in segments:
            if seg['segment_type'] == 'track':
                seg_duration = seg['end_ms'] - seg['start_ms']
                total_duration_ms += seg_duration
                start_str = ms_to_mmss(seg['start_ms'])
                end_str = ms_to_mmss(seg['end_ms'])
                row_data = [
                    "Track",
                    seg.get('album_title', ''),  # for art lookup
                    seg.get('album_title', ''),
                    seg.get('track_title', ''),
                    start_str,
                    end_str
                ]
                table_data.append(row_data)
            else:
                # Transition
                seg_duration = seg['duration']
                total_duration_ms += seg_duration
                start_str = "-"
                end_str = f"{seg_duration//1000} sec"
                # For transitions, no album/track
                row_data = [
                    "Transition",
                    "",  # no art album_title for transitions
                    "",
                    "",
                    start_str,
                    end_str
                ]
                table_data.append(row_data)

        table.setRowCount(len(table_data))
        for r, row_data in enumerate(table_data):
            # row_data: [type, art_album_title, album_title, track_title, start_str, end_str]
            seg_type = row_data[0]
            art_album_title = row_data[1]  # only valid if seg_type == "Track"
            album_title = row_data[2]
            track_title = row_data[3]
            start_str = row_data[4]
            end_str = row_data[5]

            # Column 0: Track/Transition label
            item_type = QTableWidgetItem(seg_type)
            table.setItem(r, 0, item_type)

            # Column 1: Art
            art_label = QLabel()
            art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if seg_type == "Track" and art_album_title:
                art_path = get_cached_image_path(art_album_title, 175, 175)
                pix = QPixmap(art_path)
                if pix.isNull():
                    art_label.setText("[No Art]")
                    art_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    pix = pix.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)
                    art_label.setPixmap(pix)
            else:
                # Transition or no album art
                art_label.setText("")
            table.setCellWidget(r, 1, art_label)

            # Column 2: Track
            item_track = QTableWidgetItem(track_title)
            table.setItem(r, 2, item_track)

            # Column 3: Album
            item_album = QTableWidgetItem(album_title)
            table.setItem(r, 3, item_album)

            # Column 4: Start
            item_start = QTableWidgetItem(start_str)
            table.setItem(r, 4, item_start)

            # Column 5: End/Duration
            item_end = QTableWidgetItem(end_str)
            table.setItem(r, 5, item_end)

        # Now adjust the table size similar to transitions table
        table.resizeRowsToContents()
        table.resizeColumnsToContents()

        total_width = 0
        for col in range(table.columnCount()):
            total_width += table.columnWidth(col)
        total_width += 20  # scrollbar padding

        table.resizeRowsToContents()
        content_height = table.horizontalHeader().height()
        for row in range(table.rowCount()):
            content_height += table.rowHeight(row)
        content_height += 5
        table.setFixedWidth(total_width)
        table.setFixedHeight(content_height)

        # Put the table in a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(table)

        # Center the scroll area horizontally
        table_hlayout = QHBoxLayout()
        table_hlayout.addStretch()
        table_hlayout.addWidget(scroll_area)
        table_hlayout.addStretch()

        main_layout.addLayout(table_hlayout)

        # Radio buttons for choosing output format
        output_label = QLabel("Currently, the only option is to save the output as one long MP3<br>"
                              "The option to split this into separate MP3s will be added in a future version")
        output_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(output_label)

        radio_layout = QHBoxLayout()
        radio_layout.addStretch()
        self.long_mp3_radio = QRadioButton("One Long MP3")
        self.long_mp3_radio.setChecked(True)
        self.separate_mp3s_radio = QRadioButton("Separate MP3s")
        self.separate_mp3s_radio.setEnabled(False)
        radio_layout.addWidget(self.long_mp3_radio)
        radio_layout.addSpacing(20)
        radio_layout.addWidget(self.separate_mp3s_radio)
        radio_layout.addStretch()

        main_layout.addLayout(radio_layout)

        # Confirm & select save location button
        confirm_button = QPushButton("Confirm and Select Save Location")
        confirm_button.clicked.connect(self.on_confirm_clicked)
        main_layout.addWidget(confirm_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def on_confirm_clicked(self):
        format_choice = "long_mp3" if self.long_mp3_radio.isChecked() else "separate_mp3s"
        self.confirm_clicked.emit(format_choice)

    def get_timeline_entries(self):
        return self.timeline_entries
