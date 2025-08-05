from PyQt6.QtWidgets import QFileDialog, QMessageBox
from PyQt6.QtCore import QThread
from app.ui.transitions.transitions_view import TransitionsView
from app.ui.save_process.save_view import SaveView
from app.ui.save_process.processing_view import ProcessingView
from app.audio.mix_worker import MixWorker
import shutil
import os

class NavigationController:
    def __init__(self, main_window):
        self.main_window = main_window

    def show_single_album_view(self, album_title):
        # Store scroll position before leaving all albums view
        self.main_window.last_all_albums_scroll_pos = self.main_window.all_albums_view.get_scroll_position()

        from app.ui.album_views.single_album_view import SingleAlbumView
        c = self.main_window.setup_flow_controller
        directory = c.current_directory or c.settings_manager.settings.get("shared_directory")
        self.main_window.single_album_view = SingleAlbumView(
            albums_manager=c.albums_manager,
            album_title=album_title,
            shared_directory=directory,
        )
        self.main_window.single_album_view.back_clicked.connect(self.on_single_album_back)
        self.main_window.single_album_view.track_clicked.connect(self.on_track_clicked)

        self.main_window.stack.addWidget(self.main_window.single_album_view)
        self.main_window.stack.setCurrentWidget(self.main_window.single_album_view)

    def on_single_album_back(self):
        # Return to all albums view and restore scroll position
        self.main_window.stack.setCurrentWidget(self.main_window.all_albums_view)
        self.main_window.all_albums_view.set_scroll_position(self.main_window.last_all_albums_scroll_pos)

    def on_track_clicked(self, track_index):
        # Show Transitions view for this specific track
        c = self.main_window.setup_flow_controller
        current_album_title = self.main_window.single_album_view.album_title

        self.main_window.transitions_view = TransitionsView(
            albums_manager=c.albums_manager,
            settings_manager=c.settings_manager,
            current_album_title=current_album_title,
            current_track_index=track_index,
            available_albums=[a['title'] for a in c.available_albums],
        )
        self.main_window.transitions_view.back_clicked.connect(self.on_transitions_back)
        self.main_window.transitions_view.done_clicked.connect(self.on_transitions_done)

        # Save single album view track list scroll position before switching
        self.main_window.single_album_view.last_track_list_scroll_pos = self.main_window.single_album_view.get_scroll_position()

        self.main_window.stack.addWidget(self.main_window.transitions_view)
        self.main_window.stack.setCurrentWidget(self.main_window.transitions_view)

    def on_transitions_back(self):
        # Return to single album view and restore track list scroll position
        self.main_window.stack.setCurrentWidget(self.main_window.single_album_view)
        self.main_window.single_album_view.set_scroll_position(self.main_window.single_album_view.last_track_list_scroll_pos)

    def on_transitions_done(self):
        # Get the final timeline entries from transitions_view
        timeline_entries = self.main_window.transitions_view.timeline_entries

        # Add file_path to each track entry
        c = self.main_window.setup_flow_controller
        shared_directory = c.current_directory or c.settings_manager.settings.get("shared_directory")

        from app.core.transitions_logic import find_track
        import os

        for entry in timeline_entries:
            if entry['type'] == 'track':
                album_title = entry['album_title']
                track_title = entry['track_title']
                album, track_data = find_track(self.main_window.albums_manager, album_title, track_title)
                track_file = track_data['track_file']
                file_path = os.path.join(shared_directory, album['directory'], track_file)
                entry['file_path'] = file_path

        self.main_window.save_view = SaveView(timeline_entries=timeline_entries)
        self.main_window.save_view.back_clicked.connect(self.on_save_back)
        self.main_window.save_view.confirm_clicked.connect(self.on_save_confirm)
        self.main_window.stack.addWidget(self.main_window.save_view)
        self.main_window.stack.setCurrentWidget(self.main_window.save_view)

    def on_save_back(self):
        # Just switch back to the transitions_view
        self.main_window.stack.setCurrentWidget(self.main_window.transitions_view)

    def on_save_confirm(self, format_choice):
        # Ask user to select save location (directory)
        dialog = QFileDialog(self.main_window, "Select Save Location")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        if dialog.exec():
            save_dir = dialog.selectedFiles()[0]
            if save_dir:
                # Store the chosen format and save_dir if needed
                self.start_processing_view(format_choice, save_dir)
            else:
                QMessageBox.warning(self.main_window, "No Location Selected", "Please select a save location.")
        else:
            # User canceled, do nothing for now
            pass

    def start_processing_view(self, format_choice, save_dir):
         """
         Creates and shows the ProcessingView. If a cached mix exists that matches
         the current timeline, simply copy it to the selected directory. Otherwise,
         spawn a worker thread to build the mix.
         """
         # 1) Create a ProcessingView and show it
         self.main_window.processing_view = ProcessingView()
         self.main_window.processing_view.exit_requested.connect(self.on_processing_exit)
         self.main_window.processing_view.start_over_requested.connect(self.on_processing_start_over)

         self.main_window.stack.addWidget(self.main_window.processing_view)
         self.main_window.stack.setCurrentWidget(self.main_window.processing_view)

         cached_path = getattr(self.main_window, 'cached_mix_path', None)
         cached_timeline = getattr(self.main_window, 'cached_timeline_entries', None)
         current_timeline = self.main_window.save_view.get_timeline_entries()

         # If we already processed this timeline, reuse the cached file
         if (format_choice == 'long_mp3' and cached_path and
                 cached_timeline == current_timeline and os.path.isfile(cached_path)):
             os.makedirs(save_dir, exist_ok=True)
             dest = os.path.join(save_dir, 'final_mix.mp3')
             shutil.copyfile(cached_path, dest)
             self.main_window.processing_view.update_progress_external(100)
             self.main_window.processing_view.show_done_message()
             return

         # 2) Spin up a QThread + worker to do the export
         self.thread = QThread(self.main_window)
         self.worker = MixWorker(current_timeline, format_choice, save_dir)
         self.worker.moveToThread(self.thread)

         # Connect signals
         self.worker.progress_changed.connect(self.main_window.processing_view.update_progress_external)
         self.worker.finished.connect(self.on_processing_done)
         self.thread.started.connect(self.worker.run)

         self.thread.start()
    def on_processing_done(self):
         """
         Called when audio processing is finished.
         """
         self.thread.quit()
         self.thread.wait()
         # Show the "All done!" message and the Exit / Start Over buttons
         self.main_window.processing_view.show_done_message()

    def on_processing_exit(self):
        self.main_window.close()

    def on_processing_start_over(self):
        # Return to the all albums view
        # after starting over, we assume the user wants to pick a track again
        if hasattr(self.main_window, 'all_albums_view'):
            self.main_window.stack.setCurrentWidget(self.main_window.all_albums_view)
        else:
            # If not created yet, you can recreate or handle scenario accordingly
            pass
