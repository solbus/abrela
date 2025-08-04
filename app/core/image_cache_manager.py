import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from app.core.path_utils import get_original_art_path

def get_cache_dir():
    # 1) Read APPDATA environment variable
    appdata = os.environ.get("APPDATA")  # e.g., "C:/Users/<User>/AppData/Roaming"

    # Fallback in case APPDATA is somehow missing
    if not appdata:
        appdata = os.path.expanduser("~")  # e.g. "C:/Users/<User>"

    # 2) Build the Abrela/cache path
    cache_dir = os.path.join(appdata, "Abrela", "cache")
    os.makedirs(cache_dir, exist_ok=True)  # create if doesn’t exist
    return cache_dir

def title_to_slug(title: str) -> str:
    return "".join(c.lower() if c.isalnum() else "_" for c in title)

def get_cached_image_path(album_title: str, width: int, height: int) -> str:
    slug = title_to_slug(album_title)
    cache_filename = f"{slug}_{width}x{height}.jpg"  # or .png
    return os.path.join(get_cache_dir(), cache_filename)

def cache_image_if_needed(album, shared_directory, width, height, format="JPG", quality=95):
    """
    Ensure there's a cached image for the given album at the specified size.
    If not cached, it will create and save it.
    
    Returns the cached image path (or empty string if not possible).
    """
    cache_path = get_cached_image_path(album['title'], width, height)

    # If already cached, return early
    if os.path.exists(cache_path):
        return cache_path

    # Get original path
    original_path = get_original_art_path(album, shared_directory)
    if not os.path.isfile(original_path):
        return ""

    pix = QPixmap(original_path)
    if pix.isNull():
        return ""

    # Scale with SmoothTransformation
    pix = pix.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    # Save with quality
    pix.save(cache_path, format, quality)

    return cache_path
