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
        def _read_version(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("version", 0)
            except Exception:
                return 0

        # If no explicit filepath, compute the correct path for the frozen or unfrozen case
        if filepath is None:
            user_path = get_user_albums_path()

            if getattr(sys, 'frozen', False):
                # We’re in the PyInstaller bundle => use _MEIPASS/app/albums.json
                base_dir = sys._MEIPASS  # type: ignore[attr-defined]
                packaged_path = os.path.join(base_dir, "app", "albums.json")
            else:
                # Normal dev environment => relative to this file’s directory
                here = os.path.dirname(__file__)
                packaged_path = os.path.join(here, "..", "albums.json")
                packaged_path = os.path.normpath(packaged_path)

            if os.path.exists(user_path):
                user_ver = _read_version(user_path)
                pkg_ver = _read_version(packaged_path)
                if pkg_ver > user_ver:
                    try:
                        os.remove(user_path)
                    except OSError:
                        pass
                    self.filepath = packaged_path
                else:
                    self.filepath = user_path
            else:
                self.filepath = packaged_path
        else:
            self.filepath = filepath

        self.albums = []
        self.version = 0
        self.load_albums()

    def load_albums(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.version = data.get("version", 0)
                self.albums = data.get("albums", [])
        else:
            self.albums = []
            self.version = 0

    def get_albums(self):
        return self.albums

    def get_version(self):
        return self.version

    def reload_albums(self, filepath=None):
        """Reload albums from the provided filepath or existing one."""
        if filepath:
            self.filepath = filepath
        else:
            user_path = get_user_albums_path()
            if os.path.exists(user_path):
                self.filepath = user_path
        self.load_albums()
