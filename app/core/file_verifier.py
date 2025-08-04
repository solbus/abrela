import os


class FileVerifier:
    def __init__(self, albums_manager):
        self.albums_manager = albums_manager

    def find_existing_albums(self, shared_directory):
        """Return list of albums found in the shared directory."""
        present = []
        for album in self.albums_manager.get_albums():
            album_dir = os.path.join(shared_directory, album.get("directory", ""))
            if os.path.isdir(album_dir):
                present.append(album)
        return present

    def verify_existing_shared(self, shared_directory):
        """Verify track files for albums present in the shared directory."""
        missing = []
        for album in self.find_existing_albums(shared_directory):
            album_dir = os.path.join(shared_directory, album.get("directory", ""))
            for track in album.get("tracks", []):
                track_path = os.path.join(album_dir, track.get("track_file", ""))
                if not os.path.isfile(track_path):
                    missing.append(f"Missing track file: {track_path}")
        return missing

