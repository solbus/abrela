from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.image_cache_manager import cache_image_if_needed

class CachingWorker(QObject):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, albums, all_or_some, selected_albums, shared_or_separate, shared_directory, separate_directories):
        super().__init__()
        self.albums = albums
        self.all_or_some = all_or_some
        self.selected_albums = selected_albums
        self.shared_or_separate = shared_or_separate
        self.shared_directory = shared_directory
        self.separate_directories = separate_directories

        # Filter albums
        if self.all_or_some == "all":
            self.display_albums = self.albums
        else:
            self.display_albums = [a for a in self.albums if a['title'] in self.selected_albums]

        # Only consider albums with recognized type
        self.display_albums = [a for a in self.display_albums if a.get('type') in ["Live", "Compilation", "Studio"]]

        self.total = len(self.display_albums)
        # Pre-cache the common size used by all_albums_view
        self.size = (175, 175)

    @pyqtSlot()
    def run(self):
        for i, album in enumerate(self.display_albums, start=1):
            # Pre-cache the 175x175 image
            cache_image_if_needed(
                album,
                self.shared_or_separate,
                self.shared_directory,
                self.separate_directories,
                width=self.size[0],
                height=self.size[1],
                format="JPG",
                quality=95
            )

            progress = int((i / self.total) * 100)
            self.progress_updated.emit(progress)

        self.finished.emit()
