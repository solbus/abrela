import json
import os

class SettingsManager:
    def __init__(self):
        # Where to store the settings file
        self.filepath = self._determine_settings_path()

        # Default settings
        self.settings = {
            "window": {
                "geometry": None,
                "maximized": False
            },
            "show_welcome": True
        }

        # Load (or create if missing/corrupt)
        self.load()

    def _determine_settings_path(self) -> str:
        """
        Decide where to place settings.json so it's writable and persists.
        On Windows, going with %APPDATA%/Abrela.
        """
        # On Windows, APPDATA is typically "C:\Users\<User>\AppData\Roaming"
        appdata = os.environ.get("APPDATA")  # None if not on Windows or not set
        if not appdata:
            # Fallback if for some reason APPDATA isn't set
            appdata = os.path.expanduser("~")  # e.g. "C:\Users\<User>"

        # We'll store in a subfolder named "Abrela"
        settings_dir = os.path.join(appdata, "Abrela")
        os.makedirs(settings_dir, exist_ok=True)

        # Return "C:\Users\<User>\AppData\Roaming\Abrela\settings.json"
        return os.path.join(settings_dir, "settings.json")

    def load(self):
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.settings.update(data)
            except (json.JSONDecodeError, OSError):
                # If corrupt or unreadable, ignore and use defaults
                pass

    def save(self):
        try:
            with open(self.filepath, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4)
        except OSError as e:
            # Handle write failures if needed
            print(f"Failed to save settings: {e}")

    def get_window_settings(self):
        return self.settings.get("window", {})

    def set_window_geometry(self, x, y, width, height):
        self.settings["window"]["geometry"] = (x, y, width, height)

    def set_window_maximized(self, maximized):
        self.settings["window"]["maximized"] = maximized

    def should_show_welcome(self):
        return self.settings.get("show_welcome", True)

    def set_show_welcome(self, value: bool):
        self.settings["show_welcome"] = value

    def set_value(self, key, value):
        # Store at the root level of self.settings
        self.settings[key] = value