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

        self.all_or_some = None
        self.shared_or_separate = None
        self.selected_albums = []
        self.current_shared_directory = None
        self.current_separate_directories = {}

    def show_welcome_dialog_if_needed(self):
        if self.settings_manager.should_show_welcome():
            dialog = WelcomeDialog(self.main_window)
            geo = self.main_window.geometry()
            result = dialog.show_dialog(geo)
            if dialog.dont_show_again:
                self.settings_manager.set_show_welcome(False)
                self.settings_manager.save()

    def handle_initial_questions_continue(self, all_or_some, shared_or_separate, remember):
        if remember:
            self.settings_manager.set_value("all_or_some", all_or_some)
            self.settings_manager.set_value("shared_or_separate", shared_or_separate)
            self.settings_manager.save()

        self.all_or_some = all_or_some
        self.shared_or_separate = shared_or_separate

        # Move to next step based on choices
        if self.all_or_some == "all":
            # For all albums
            if self.shared_or_separate == "shared":
                self.main_window.show_shared_directory_step()
            else:
                # separate
                all_album_titles = [a["title"] for a in self.albums_manager.get_albums()]
                self.main_window.show_separate_directories_step(albums=all_album_titles)
        else:
            # some
            self.main_window.show_select_albums_step()

    def handle_start_over(self):
        """
        Clears remembered setup values, resets local state,
        and returns the user to the initial questions step.
        """
        # Clear settings in the SettingsManager
        self.settings_manager.set_value("all_or_some", None)
        self.settings_manager.set_value("shared_or_separate", None)
        self.settings_manager.set_value("selected_albums", [])
        self.settings_manager.set_value("shared_directory", None)
        self.settings_manager.set_value("separate_directories", {})
        self.settings_manager.save()

        # Clear controller state
        self.all_or_some = None
        self.shared_or_separate = None
        self.selected_albums = []
        self.current_shared_directory = None
        self.current_separate_directories = {}

        # Show initial questions screen
        self.main_window.show_initial_questions()

    def handle_select_albums_continue(self, selected_albums, remember):
        self.selected_albums = selected_albums
        if remember:
            self.settings_manager.set_value("selected_albums", self.selected_albums)
            self.settings_manager.save()

        if self.shared_or_separate == "shared":
            self.main_window.show_shared_directory_step()
        else:
            # separate
            self.main_window.show_separate_directories_step(albums=self.selected_albums)

    def handle_shared_directory_continue(self, directory, remember):
        self.current_shared_directory = directory
        if remember:
            self.settings_manager.set_value("shared_directory", directory)
            self.settings_manager.save()

        # Verify files now
        missing = self.verifier.verify(
            all_or_some=self.all_or_some,
            shared_or_separate=self.shared_or_separate,
            selected_albums=self.selected_albums,
            shared_directory=directory
        )

        if missing:
            self.show_missing_files_dialog(missing)
        else:
            self.finish_setup()

    def handle_separate_directories_continue(self, directories, remember):
        self.current_separate_directories = directories
        if remember:
            self.settings_manager.set_value("separate_directories", directories)
            self.settings_manager.save()

        # Verify files now
        missing = self.verifier.verify(
            all_or_some=self.all_or_some,
            shared_or_separate=self.shared_or_separate,
            selected_albums=self.selected_albums,
            separate_directories=directories
        )

        if missing:
            self.show_missing_files_dialog(missing)
        else:
            self.finish_setup()

    def auto_verify_and_finish(self):
        directory = self.settings_manager.settings.get("shared_directory", None)
        directories = self.settings_manager.settings.get("separate_directories", {})
        selected_albums = self.settings_manager.settings.get("selected_albums", [])

        missing = self.verifier.verify(
            all_or_some=self.all_or_some,
            shared_or_separate=self.shared_or_separate,
            selected_albums=selected_albums,
            shared_directory=directory,
            separate_directories=directories
        )

        if missing:
            self.show_missing_files_dialog(missing)
        else:
            self.finish_setup()

    def finish_setup(self):
        self.main_window.stack.setCurrentWidget(self.main_window.loading_screen)

        all_albums = self.albums_manager.get_albums()
        selected_albums = self.selected_albums or self.settings_manager.settings.get("selected_albums", [])

        shared_directory = self.current_shared_directory or self.settings_manager.settings.get("shared_directory", None)
        separate_directories = self.current_separate_directories or self.settings_manager.settings.get("separate_directories", {})

        self.thread = QThread()
        self.worker = CachingWorker(
            albums=all_albums,
            all_or_some=self.all_or_some,
            selected_albums=selected_albums,
            shared_or_separate=self.shared_or_separate,
            shared_directory=shared_directory,
            separate_directories=separate_directories
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
        # After caching, show all albums view
        shared_directory = self.current_shared_directory or self.settings_manager.settings.get("shared_directory", None)
        separate_directories = self.current_separate_directories or self.settings_manager.settings.get("separate_directories", {})

        self.main_window.all_albums_view = AllAlbumsView(
            albums_manager=self.albums_manager,
            settings_manager=self.settings_manager,
            flow_controller=self,
            all_or_some=self.all_or_some,
            selected_albums=self.selected_albums,
            shared_or_separate=self.shared_or_separate,
            shared_directory=self.current_shared_directory,
            separate_directories=self.current_separate_directories
        )
        # Connect album_clicked to navigation
        self.main_window.all_albums_view.album_clicked.connect(self.main_window.navigation_controller.show_single_album_view)
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
        # User can go back and fix directories themselves
