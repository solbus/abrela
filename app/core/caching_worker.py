from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from app.core.image_cache_manager import cache_image_if_needed


class CachingWorker(QObject):
    progress_updated = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, albums, shared_directory):
        super().__init__()
        self.albums = [a for a in albums if a.get('type') in ["Live", "Compilation", "Studio"]]
        self.shared_directory = shared_directory
        self.total = len(self.albums)
        self.size = (175, 175)

    @pyqtSlot()
    def run(self):
        if self.total == 0:
            self.progress_updated.emit(100)
            self.finished.emit()
            return

        for i, album in enumerate(self.albums, start=1):
            cache_image_if_needed(
                album,
                self.shared_directory,
                width=self.size[0],
                height=self.size[1],
                format="JPG",
                quality=95,
            )

            progress = int((i / self.total) * 100)
            self.progress_updated.emit(progress)

        self.finished.emit()

