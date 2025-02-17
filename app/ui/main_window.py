from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QApplication
from PyQt6.QtGui import QCloseEvent

from app.core.albums_manager import AlbumsManager
from app.core.file_verifier import FileVerifier
from app.core.setup_flow_controller import SetupFlowController
from app.core.navigation_controller import NavigationController

from app.ui.setup.initial_questions import InitialQuestionsStep
from app.ui.setup.select_albums import SelectAlbumsStep
from app.ui.setup.shared_directory import SharedDirectoryStep
from app.ui.setup.separate_directories import SeparateDirectoriesStep
from app.ui.setup.loading_screen import LoadingScreen

class MainWindow(QMainWindow):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings_manager = settings_manager
        self.setWindowTitle("Abrela")

        self.restore_geometry_from_settings()

        # QStackedWidget as the central widget
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Instantiate managers
        self.albums_manager = AlbumsManager()
        self.verifier = FileVerifier(self.albums_manager)

        # Controllers
        self.setup_flow_controller = SetupFlowController(self)
        self.navigation_controller = NavigationController(self)

        # UI Steps
        self.initial_step = InitialQuestionsStep(parent=self)
        self.select_albums_step = SelectAlbumsStep(
            albums_manager=self.albums_manager,
            flow_controller=self.setup_flow_controller,
            parent=self
        )
        self.shared_directory_step = SharedDirectoryStep(
            flow_controller=self.setup_flow_controller, 
            parent=self
        )
        self.separate_directories_step = SeparateDirectoriesStep(
            albums_manager=self.albums_manager,
            flow_controller=self.setup_flow_controller,
            parent=self
        )
        self.loading_screen = LoadingScreen(parent=self)

        # Add steps to the stack
        self.stack.addWidget(self.initial_step)
        self.stack.addWidget(self.select_albums_step)
        self.stack.addWidget(self.shared_directory_step)
        self.stack.addWidget(self.separate_directories_step)
        self.stack.addWidget(self.loading_screen)

        # Connect signals from steps to SetupFlowController methods
        self.initial_step.continue_clicked.connect(self.setup_flow_controller.handle_initial_questions_continue)
        self.select_albums_step.continue_clicked.connect(self.setup_flow_controller.handle_select_albums_continue)
        self.shared_directory_step.continue_clicked.connect(self.setup_flow_controller.handle_shared_directory_continue)
        self.separate_directories_step.continue_clicked.connect(self.setup_flow_controller.handle_separate_directories_continue)

        # Variables used by NavigationController
        self.last_all_albums_scroll_pos = 0

    def restore_geometry_from_settings(self):
        window_settings = self.settings_manager.get_window_settings()

        if window_settings.get("geometry") is None:
            default_width = 850
            default_height = 650
            self.resize(default_width, default_height)

            screen = QApplication.primaryScreen()
            screen_geometry = screen.availableGeometry()
            x = (screen_geometry.width() - default_width) // 2
            y = (screen_geometry.height() - default_height) // 2
            self.move(x, y)
        else:
            x, y, w, h = window_settings["geometry"]
            self.setGeometry(x, y, w, h)

        if window_settings.get("maximized", False):
            self.showMaximized()

    def show_initial_questions(self):
        self.stack.setCurrentWidget(self.initial_step)

    def show_select_albums_step(self):
        self.stack.setCurrentWidget(self.select_albums_step)

    def show_shared_directory_step(self, prefill=None):
        if prefill:
            self.shared_directory_step.dir_edit.setText(prefill)
        self.stack.setCurrentWidget(self.shared_directory_step)

    def show_separate_directories_step(self, albums, prefill=None):
        self.separate_directories_step.set_albums(albums)
        if prefill:
            for title, path in prefill.items():
                if title in self.separate_directories_step.album_lineedits:
                    self.separate_directories_step.album_lineedits[title].setText(path)
        self.stack.setCurrentWidget(self.separate_directories_step)

    def closeEvent(self, event: QCloseEvent):
        if self.isMaximized():
            self.settings_manager.set_window_maximized(True)
        else:
            self.settings_manager.set_window_maximized(False)
            geo = self.geometry()
            x, y, w, h = geo.x(), geo.y(), geo.width(), geo.height()
            self.settings_manager.set_window_geometry(x, y, w, h)
        self.settings_manager.save()
        super().closeEvent(event)
