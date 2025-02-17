import json
import os
import sys

class AlbumsManager:
    def __init__(self, filepath=None):
        # If no explicit filepath, compute the correct path for the frozen or unfrozen case
        if filepath is None:
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
