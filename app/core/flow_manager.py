class FlowManager:
    def __init__(self, settings_manager, albums_manager):
        self.settings_manager = settings_manager
        self.albums_manager = albums_manager

    def run_flow(self, main_window):
        c = main_window.setup_flow_controller
        shared_directory = self.settings_manager.settings.get("shared_directory", None)
        if shared_directory:
            c.current_directory = shared_directory
            c.auto_verify_and_finish()
        else:
            main_window.show_directory_step()

