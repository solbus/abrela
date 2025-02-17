import os

def get_original_art_path(album, shared_or_separate, shared_directory, separate_directories):
    album_art_file = album.get('album_art', 'cover.jpg')
    if shared_or_separate == "shared":
        if shared_directory and album.get('directory'):
            return os.path.join(shared_directory, album['directory'], album_art_file)
    else:
        # separate
        album_title = album['title']
        if album_title in separate_directories:
            return os.path.join(separate_directories[album_title], album_art_file)
    return ""
