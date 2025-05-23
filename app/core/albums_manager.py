import json
import os
import sys

def get_user_albums_path():
    """Return the path to the user's custom albums.json in APPDATA."""
    appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
    abrela_dir = os.path.join(appdata, "Abrela")
    os.makedirs(abrela_dir, exist_ok=True)
    return os.path.join(abrela_dir, "albums.json")


class AlbumsManager:
    def __init__(self, filepath=None):
        # If no explicit filepath, compute the correct path for the frozen or unfrozen case
        if filepath is None:
            user_path = get_user_albums_path()
            if os.path.exists(user_path):
                self.filepath = user_path
            else:
                if getattr(sys, 'frozen', False):
                    # We’re in the PyInstaller bundle => use _MEIPASS/app/albums.json
                    base_dir = sys._MEIPASS  # type: ignore
                    self.filepath = os.path.join(base_dir, "app", "albums.json")
                else:
                    # Normal dev environment => relative to this file’s directory
                    # e.g. /path/to/app/core/ => we step up one level => /path/to/app/
                    here = os.path.dirname(__file__)
                    self.filepath = os.path.join(here, "..", "albums.json")
                    self.filepath = os.path.normpath(self.filepath)
        else:
            self.filepath = filepath

        self.albums = []
        self.load_albums()

    def load_albums(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.albums = data.get("albums", [])
        else:
            self.albums = []

    def get_albums(self):
        return self.albums

    def reload_albums(self, filepath=None):
        """Reload albums from the provided filepath or existing one."""
        if filepath:
            self.filepath = filepath
        else:
            user_path = get_user_albums_path()
            if os.path.exists(user_path):
                self.filepath = user_path
        self.load_albums()
