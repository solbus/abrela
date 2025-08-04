import os


def get_original_art_path(album, shared_directory):
    album_art_file = album.get("album_art", "cover.jpg")
    if shared_directory and album.get("directory"):
        return os.path.join(shared_directory, album["directory"], album_art_file)
    return ""

