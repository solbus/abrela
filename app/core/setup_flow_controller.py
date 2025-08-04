from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import QThread

from app.core.caching_worker import CachingWorker
from app.ui.album_views.all_albums_view import AllAlbumsView
from app.ui.setup.welcome_dialog import WelcomeDialog


class SetupFlowController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.settings_manager = self.main_window.settings_manager
        self.albums_manager = self.main_window.albums_manager
        self.verifier = self.main_window.verifier

        self.current_directory = None
        self.available_albums = []

    def show_welcome_dialog_if_needed(self):
        if self.settings_manager.should_show_welcome():
            dialog = WelcomeDialog(self.main_window)
            geo = self.main_window.geometry()
            result = dialog.show_dialog(geo)
            if dialog.dont_show_again:
                self.settings_manager.set_show_welcome(False)
                self.settings_manager.save()

    def handle_directory_continue(self, directory, remember):
        self.current_directory = directory
        if remember:
            self.settings_manager.set_value("shared_directory", directory)
            self.settings_manager.save()

        missing = self.verifier.verify_existing_shared(directory)
        if missing:
            self.show_missing_files_dialog(missing)
        else:
            self.finish_setup()

    def handle_start_over(self):
        self.settings_manager.set_value("shared_directory", None)
        self.settings_manager.save()
        self.current_directory = None
        self.available_albums = []
        self.main_window.show_directory_step()

    def auto_verify_and_finish(self):
        directory = self.settings_manager.settings.get("shared_directory", None)
        if directory:
            missing = self.verifier.verify_existing_shared(directory)
            if missing:
                self.show_missing_files_dialog(missing)
            else:
                self.current_directory = directory
                self.finish_setup()
        else:
            self.main_window.show_directory_step()

    def finish_setup(self):
        self.main_window.stack.setCurrentWidget(self.main_window.loading_screen)

        import os
        self.available_albums = [
            a for a in self.albums_manager.get_albums()
            if os.path.isdir(os.path.join(self.current_directory, a.get("directory", "")))
        ]

        self.thread = QThread()
        self.worker = CachingWorker(
            albums=self.available_albums,
            shared_directory=self.current_directory,
        )
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.progress_updated.connect(self.main_window.loading_screen.set_progress)
        self.worker.finished.connect(self.on_caching_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_caching_finished(self):
        self.main_window.all_albums_view = AllAlbumsView(
            albums_manager=self.albums_manager,
            settings_manager=self.settings_manager,
            flow_controller=self,
            albums=self.available_albums,
            shared_directory=self.current_directory,
        )
        self.main_window.all_albums_view.album_clicked.connect(
            self.main_window.navigation_controller.show_single_album_view
        )
        self.main_window.stack.addWidget(self.main_window.all_albums_view)
        self.main_window.stack.setCurrentWidget(self.main_window.all_albums_view)

        self.main_window.last_all_albums_scroll_pos = 0

    def show_missing_files_dialog(self, missing):
        msg = QMessageBox(self.main_window)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("Missing Files")
        msg.setText("Some expected files or directories are missing:")
        msg.setInformativeText("\n".join(missing))
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

