import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from app.core.settings_manager import SettingsManager
from app.core.flow_manager import FlowManager
from app.ui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon_path = os.path.join(os.path.dirname(__file__), "app", "assets", "app_icon.ico")
    app.setWindowIcon(QIcon(icon_path))
    settings_manager = SettingsManager()
    main_window = MainWindow(settings_manager)
    main_window.show()

    # Show welcome dialog if needed
    main_window.setup_flow_controller.show_welcome_dialog_if_needed()

    # Run the flow
    flow_manager = FlowManager(settings_manager, main_window.albums_manager)
    flow_manager.run_flow(main_window)

    sys.exit(app.exec())