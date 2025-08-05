from PyQt6.QtCore import pyqtSignal, Qt, QThread
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget
)

from app.ui.player.audio_player_dialog import AudioPlayerDialog
from app.ui.common.loading_dialog import LoadingDialog
from app.audio.mix_worker import MixWorker
import os
from copy import deepcopy

from app.core.transitions_logic import (
    ms_to_mmss, find_track, get_current_track_data, add_track_to_timeline,
    load_initial_timeline, compute_segments_from_timeline, get_filtered_transitions,
    sum_segments_duration
)
from app.ui.transitions.timeline_widget import TimelineWidget
from app.ui.transitions.current_track_widget import TransitionsCurrentTrackInfoWidget
from app.ui.transitions.table_widget import TransitionsTableWidget

class TransitionsView(QWidget):
    back_clicked = pyqtSignal()
    done_clicked = pyqtSignal()

    def __init__(self, albums_manager, settings_manager, current_album_title,
                 current_track_index, available_albums):
        super().__init__()
        self.albums_manager = albums_manager
        self.settings_manager = settings_manager
        self.current_album_title = current_album_title
        self.current_track_index = current_track_index
        self.available_albums = available_albums

        self.timeline_entries = load_initial_timeline(self.albums_manager, self.current_album_title, self.current_track_index)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Back button row
        top_back_layout = QHBoxLayout()
        back_button = QPushButton("Back")
        back_button.clicked.connect(self.on_back_clicked)
        top_back_layout.addWidget(back_button, alignment=Qt.AlignmentFlag.AlignLeft)
        top_back_layout.addStretch()
        main_layout.addLayout(top_back_layout)

        # Title row
        self.title_label = QLabel("Transitions")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        title_layout = QHBoxLayout()
        title_layout.addStretch()
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        main_layout.addLayout(title_layout)

        # Current track info row
        self.current_track_info_widget = TransitionsCurrentTrackInfoWidget()
        self.update_current_track_info()
        track_info_layout = QHBoxLayout()
        track_info_layout.addStretch()
        track_info_layout.addWidget(self.current_track_info_widget)
        track_info_layout.addStretch()
        main_layout.addLayout(track_info_layout)

        # Transitions table row
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        self.table_widget = TransitionsTableWidget()
        self.table_widget.cellClicked.connect(self.on_table_cell_clicked)

        self.scroll_area.setWidget(self.table_widget)

        table_layout = QHBoxLayout()
        # table_layout.addStretch()
        table_layout.addWidget(self.scroll_area)
        # table_layout.addStretch()
        main_layout.addLayout(table_layout)

        # Timeline box
        timeline_frame = QFrame()
        timeline_frame.setFrameShape(QFrame.Shape.StyledPanel)
        timeline_layout = QVBoxLayout(timeline_frame)
        timeline_layout.setContentsMargins(10,10,10,10)
        timeline_layout.setSpacing(5)

        timeline_label = QLabel("Timeline")
        timeline_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timeline_label.setStyleSheet("font-weight: bold;")
        timeline_layout.addWidget(timeline_label)

        self.timeline_widget = TimelineWidget()
        self.timeline_widget.segment_clicked.connect(self.on_timeline_segment_clicked)
        timeline_layout.addWidget(self.timeline_widget)

        self.total_label = QLabel("Total: 00:00:00")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setPointSize(10)
        self.total_label.setFont(font)
        timeline_layout.addWidget(self.total_label)

        bottom_hlayout = QHBoxLayout()
        bottom_hlayout.addStretch(1)
        process_button = QPushButton("Process and Play")
        process_button.clicked.connect(self.on_process_play_clicked)
        bottom_hlayout.addWidget(process_button)
        bottom_hlayout.addSpacing(20)
        done_button = QPushButton("Done")
        done_button.clicked.connect(self.done_clicked.emit)
        bottom_hlayout.addWidget(done_button)
        timeline_layout.addLayout(bottom_hlayout)

        main_layout.addWidget(timeline_frame)

        self.setLayout(main_layout)

        self.populate_table()
        self.update_timeline()

    def update_current_track_info(self):
        album, track = get_current_track_data(self.albums_manager, self.current_album_title, self.current_track_index)
        self.current_track_info_widget.update_info(album, track)

    def on_back_clicked(self):
        from PyQt6.QtWidgets import QMessageBox
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Warning")
        msg.setText("Going back will clear the timeline. Are you sure you want to go back?<br><br>"
                    "<b>Hint:</b> Click on a track segment on the timeline to start over from there")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        result = msg.exec()
        if result == QMessageBox.StandardButton.Yes:
            self.back_clicked.emit()

    def on_table_cell_clicked(self, row, column):
        self.select_transition(row)

    def select_transition(self, row):
        index_item = self.table_widget.item(row, 0)
        if not index_item:
            return
        index_label = index_item.text()

        album, track = get_current_track_data(
            self.albums_manager,
            self.current_album_title,
            self.current_track_index
        )
        tracks = album['tracks']
        transitions = track.get('transitions', [])
        default_exists = (self.current_track_index < len(tracks))

        chosen_transition = None

        if default_exists and index_label == "Default":
            # The user picked the "Default" row
            next_track = tracks[self.current_track_index]
            chosen_transition = {
                'type': 'default',
                'next_album': album['title'],
                'next_track': next_track['track_title']
            }
        else:
            # The user clicked a numeric row => custom transition
            if index_label.isdigit():
                i = int(index_label) - 1
                if 0 <= i < len(transitions):
                    t = transitions[i]
                    chosen_transition = {
                        'type': 'custom',
                        'data': t
                    }

        if not chosen_transition:
            return

        if chosen_transition['type'] == 'default':
            #
            # 1) DEFAULT transition => Just add next track with default_transition=True
            #
            target_album_title = chosen_transition['next_album']
            target_track_title = chosen_transition['next_track']
            target_album, target_track = find_track(
                self.albums_manager,
                target_album_title,
                target_track_title
            )

            add_track_to_timeline(
                self.timeline_entries,
                self.current_album_title,
                self.current_track_index,
                target_album_title,
                target_track,
                default_transition=True
            )

        else:
            #
            # 2) CUSTOM transition => Attach fade-out / slice info to the LAST track
            #    in timeline_entries, then add the new track normally.
            #
            t = chosen_transition['data']
            # This is the album/track we're transitioning *into*
            target_album_title = t.get('target_album', album['title']) or album['title']
            target_track_title = t['target_track']
            target_album, target_track = find_track(
                self.albums_manager,
                target_album_title,
                target_track_title
            )

            # A) Patch the *existing* (source) track in the timeline
            if self.timeline_entries:
                source_entry = self.timeline_entries[-1]
                # Store all needed partial-slice, fade-out, etc. data
                source_entry['transition_data'] = t
                source_entry['default_transition'] = False

            # B) Now add the new (destination) track with no custom transition
            add_track_to_timeline(
                self.timeline_entries,
                self.current_album_title,
                self.current_track_index,
                target_album_title,
                target_track,
                default_transition=False,
                transition_data=None
            )

        #
        # 3) Update current_album_title / current_track_index to the newly added track
        #
        self.current_album_title = target_album_title
        target_album, _ = find_track(
            self.albums_manager,
            target_album_title,
            target_track_title
        )
        for idx, trk in enumerate(target_album['tracks'], start=1):
            if trk['track_title'] == target_track_title:
                self.current_track_index = idx
                break

        #
        # 4) Refresh UI
        #
        self.update_current_track_info()
        self.populate_table()
        self.update_timeline()
        self.table_widget.adjust_table_size()

    def populate_table(self):
        # Retrieve the 'default_exists' flag and the filtered transitions
        default_exists, valid_transitions = get_filtered_transitions(
            self.albums_manager,
            self.current_album_title,
            self.current_track_index,
            self.get_user_selected_albums()
        )

        # Retrieve the album & track objects for some UI data (cover art, etc.)
        album, track = get_current_track_data(
            self.albums_manager,
            self.current_album_title,
            self.current_track_index
        )

        # Pass the final data to the table
        self.table_widget.populate_table(
            album=album,
            track=track,
            current_track_index=self.current_track_index,
            default_exists=default_exists,
            transitions=valid_transitions
        )

    def get_user_selected_albums(self):
        """
        Returns a list of album titles the user actually selected if in 'some' mode;
        or returns [] if the user chose 'all' (to indicate no filtering).
        """
        return self.available_albums

    def update_timeline(self):
        segs = compute_segments_from_timeline(self.timeline_entries)
        self.timeline_widget.set_segments(segs)

        total_ms = sum_segments_duration(segs)
        self.total_label.setText(f"Total: {ms_to_mmss(total_ms)}")

    def on_timeline_segment_clicked(self, segment_index):
        segs = self.timeline_widget.segments
        seg = segs[segment_index]

        if seg['segment_type'] == 'track':
            # Revert timeline to this point
            reverted_timeline = []
            for entry in self.timeline_entries:
                reverted_timeline.append(entry)
                if entry['track_title'] == seg['track_title'] and entry['album_title'] == seg['album_title']:
                    break
            self.timeline_entries = reverted_timeline
            last_track = self.timeline_entries[-1]
            self.current_album_title = last_track['album_title']
            album, _ = find_track(self.albums_manager, last_track['album_title'], last_track['track_title'])

            # 1) Clear out leftover transition data on the newly-last track
            last_track['transition_data'] = None
            last_track['default_transition'] = False
            if 'starting_offset' in last_track:
                del last_track['starting_offset']

            # 2) **FIRST**, update self.current_track_index to match last_track
            for idx, trk in enumerate(album['tracks'], start=1):
                if trk['track_title'] == last_track['track_title']:
                    self.current_track_index = idx
                    break

            # 3) **THEN** call self.update_current_track_info() and the rest
            self.update_current_track_info()
            self.populate_table()
            self.update_timeline()
            self.table_widget.adjust_table_size()

    # ------------------------------------------------------------------
    def on_process_play_clicked(self):
        """Generate the final mix to the cache directory and play it."""
        # Prepare timeline entries with file paths
        timeline_copy = deepcopy(self.timeline_entries)
        shared_directory = self.settings_manager.settings.get("shared_directory")

        for entry in timeline_copy:
            if entry['type'] == 'track':
                album_title = entry['album_title']
                track_title = entry['track_title']
                album, track_data = find_track(self.albums_manager, album_title, track_title)
                track_file = track_data['track_file']
                entry['file_path'] = os.path.join(shared_directory, album['directory'], track_file)

        appdata = os.getenv('APPDATA') or os.path.expanduser('~')
        cache_dir = os.path.join(appdata, 'Abrela')
        os.makedirs(cache_dir, exist_ok=True)

        self.loading_dialog = LoadingDialog(self)
        self.loading_dialog.show()

        self.thread = QThread(self)
        self.worker = MixWorker(timeline_copy, 'long_mp3', cache_dir)
        self.worker.moveToThread(self.thread)
        self.worker.finished.connect(lambda: self.on_process_play_finished(cache_dir))
        self.thread.started.connect(self.worker.run)
        self.thread.start()

    def on_process_play_finished(self, cache_dir):
        self.thread.quit()
        self.thread.wait()
        self.loading_dialog.close()

        out_path = os.path.join(cache_dir, 'final_mix.mp3')

        main_window = self.window()
        if main_window:
            main_window.cached_mix_path = out_path
            main_window.cached_timeline_entries = deepcopy(self.timeline_entries)

        self.player_dialog = AudioPlayerDialog(out_path, parent=main_window)
        self.player_dialog.show()

