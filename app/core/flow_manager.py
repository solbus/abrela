class FlowManager:
    def __init__(self, settings_manager, albums_manager):
        self.settings_manager = settings_manager
        self.albums_manager = albums_manager

    def run_flow(self, main_window):
        c = main_window.setup_flow_controller

        all_or_some = self.settings_manager.settings.get("all_or_some", None)
        shared_or_separate = self.settings_manager.settings.get("shared_or_separate", None)
        selected_albums = self.settings_manager.settings.get("selected_albums", [])
        shared_directory = self.settings_manager.settings.get("shared_directory", None)
        separate_directories = self.settings_manager.settings.get("separate_directories", {})

        albums_manager = self.albums_manager
        all_album_titles = [a["title"] for a in albums_manager.get_albums()]

        def have_all_separate_dirs():
            if not separate_directories:
                return False
            for title in all_album_titles:
                if title not in separate_directories or not separate_directories[title]:
                    return False
            return True

        def have_some_separate_dirs():
            if not separate_directories or not selected_albums:
                return False
            for title in selected_albums:
                if title not in separate_directories or not separate_directories[title]:
                    return False
            return True

        if all_or_some and shared_or_separate:
            # Assign states to the setup_flow_controller
            c.all_or_some = all_or_some
            c.shared_or_separate = shared_or_separate
            c.selected_albums = selected_albums or []

            # "All & Shared"
            if all_or_some == "all" and shared_or_separate == "shared":
                if shared_directory:
                    # Everything is known, skip showing directory step and verify immediately
                    c.current_shared_directory = shared_directory
                    c.auto_verify_and_finish()
                else:
                    # Need directory
                    main_window.show_shared_directory_step()

            # "All & Separate"
            elif all_or_some == "all" and shared_or_separate == "separate":
                if have_all_separate_dirs():
                    # Directories known, verify immediately
                    c.current_separate_directories = separate_directories
                    c.auto_verify_and_finish()
                else:
                    main_window.show_separate_directories_step(albums=all_album_titles, prefill=separate_directories)

            # "Some & Shared"
            elif all_or_some == "some" and shared_or_separate == "shared":
                if selected_albums and shared_directory:
                    # Everything known, verify immediately
                    c.current_shared_directory = shared_directory
                    c.auto_verify_and_finish()
                else:
                    if not selected_albums:
                        main_window.show_select_albums_step()
                    else:
                        main_window.show_shared_directory_step(prefill=shared_directory)

            # "Some & Separate"
            elif all_or_some == "some" and shared_or_separate == "separate":
                if selected_albums and have_some_separate_dirs():
                    # Everything known, verify immediately
                    c.current_separate_directories = separate_directories
                    c.auto_verify_and_finish()
                else:
                    if not selected_albums:
                        main_window.show_select_albums_step()
                    else:
                        main_window.show_separate_directories_step(albums=selected_albums, prefill=separate_directories)

        else:
            # No initial answers remembered, show initial questions
            main_window.show_initial_questions()
