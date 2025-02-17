import os

class FileVerifier:
    def __init__(self, albums_manager):
        self.albums_manager = albums_manager

    def verify_all_shared(self, shared_directory):
        """
        Verify that all albums listed in albums.json are found under the shared directory.
        Each album has a 'directory' name and each track has a 'track_file'.
        """
        missing = []
        all_albums = self.albums_manager.get_albums()
        for album in all_albums:
            album_dir = os.path.join(shared_directory, album['directory'])
            if not os.path.isdir(album_dir):
                missing.append(f"Missing album directory: {album_dir}")
                continue

            for track in album.get('tracks', []):
                track_path = os.path.join(album_dir, track['track_file'])
                if not os.path.isfile(track_path):
                    missing.append(f"Missing track file: {track_path}")

        return missing

    def verify_all_separate(self, separate_directories):
        """
        Verify that for all albums, the directories and track files exist.
        separate_directories is a dict {album_title: album_directory_path}
        """
        missing = []
        all_albums = self.albums_manager.get_albums()
        for album in all_albums:
            album_title = album['title']
            if album_title not in separate_directories:
                missing.append(f"No directory specified for album: {album_title}")
                continue

            album_dir = separate_directories[album_title]
            if not os.path.isdir(album_dir):
                missing.append(f"Missing album directory: {album_dir}")
                continue

            for track in album.get('tracks', []):
                track_path = os.path.join(album_dir, track['track_file'])
                if not os.path.isfile(track_path):
                    missing.append(f"Missing track file: {track_path}")

        return missing

    def verify_some_shared(self, selected_albums, shared_directory):
        """
        Verify that only the selected albums are checked, each under the shared directory.
        """
        missing = []
        # Create a lookup of albums by title
        albums_by_title = {a['title']: a for a in self.albums_manager.get_albums()}
        for album_title in selected_albums:
            if album_title not in albums_by_title:
                missing.append(f"Album not found in albums.json: {album_title}")
                continue

            album = albums_by_title[album_title]
            album_dir = os.path.join(shared_directory, album['directory'])
            if not os.path.isdir(album_dir):
                missing.append(f"Missing album directory: {album_dir}")
                continue

            for track in album.get('tracks', []):
                track_path = os.path.join(album_dir, track['track_file'])
                if not os.path.isfile(track_path):
                    missing.append(f"Missing track file: {track_path}")

        return missing

    def verify_some_separate(self, selected_albums, separate_directories):
        """
        Verify that only the selected albums are checked, each in its specified directory.
        """
        missing = []
        albums_by_title = {a['title']: a for a in self.albums_manager.get_albums()}
        for album_title in selected_albums:
            if album_title not in albums_by_title:
                missing.append(f"Album not found in albums.json: {album_title}")
                continue

            album = albums_by_title[album_title]

            if album_title not in separate_directories:
                missing.append(f"No directory specified for album: {album_title}")
                continue

            album_dir = separate_directories[album_title]
            if not os.path.isdir(album_dir):
                missing.append(f"Missing album directory: {album_dir}")
                continue

            for track in album.get('tracks', []):
                track_path = os.path.join(album_dir, track['track_file'])
                if not os.path.isfile(track_path):
                    missing.append(f"Missing track file: {track_path}")

        return missing

    def verify(self, all_or_some, shared_or_separate, selected_albums=None, shared_directory=None, separate_directories=None):
        """
        High-level verification method that decides which verification method to call
        based on the scenario.
        
        Returns:
            missing (list): A list of missing directories or files (strings).
            If empty, it means everything was found.
        """
        selected_albums = selected_albums or []
        separate_directories = separate_directories or {}

        if all_or_some == "all" and shared_or_separate == "shared":
            return self.verify_all_shared(shared_directory)
        elif all_or_some == "all" and shared_or_separate == "separate":
            return self.verify_all_separate(separate_directories)
        elif all_or_some == "some" and shared_or_separate == "shared":
            return self.verify_some_shared(selected_albums, shared_directory)
        elif all_or_some == "some" and shared_or_separate == "separate":
            return self.verify_some_separate(selected_albums, separate_directories)
        else:
            return ["Invalid scenario provided."]
