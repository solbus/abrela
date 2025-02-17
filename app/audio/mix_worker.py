import os
from PyQt6.QtCore import QObject, pyqtSignal
from app.audio.create_mix import create_final_mix
from app.audio.segment_builder import build_segments

class MixWorker(QObject):
    finished = pyqtSignal()
    progress_changed = pyqtSignal(int)

    def __init__(self, timeline_entries, format_choice, save_dir, parent=None):
        super().__init__(parent)
        self.timeline_entries = timeline_entries
        self.format_choice = format_choice
        self.save_dir = save_dir

    def run(self):
        try:
            print("[DEBUG] MixWorker.run() called")
            print("[DEBUG] timeline_entries passed to MixWorker:")
            for i, entry in enumerate(self.timeline_entries):
                print(f"   {i}: {entry}")

            if self.format_choice == "long_mp3":
                out_path = os.path.join(self.save_dir, "final_mix.mp3")

                def progress_cb(pct):
                    """
                    A small callback that just emits the progress_changed signal.
                    """
                    self.progress_changed.emit(pct)

                # 1) Build each track segment with segment_builder
                print("[DEBUG] Now calling build_segments...")
                segments = build_segments(self.timeline_entries, progress_cb)
                print(f"[DEBUG] build_segments returned {len(segments)} segments.")

                # 2) Create one big final mix with overlay logic
                create_final_mix(segments, self.timeline_entries, out_path, progress_cb)

            else:
                # "Separate MP3s" scenario:
                count = len([e for e in self.timeline_entries if e['type'] == 'track'])
                processed = 0
                for idx, entry in enumerate(self.timeline_entries, start=1):
                    if entry['type'] != 'track':
                        continue

                    from app.audio.audio_processor import load_audio, export_audio
                    audio = load_audio(entry['file_path'])

                    safe_title = entry['track_title'].replace("/", "_").replace("\\", "_")
                    filename = f"{idx:02d} - {safe_title}.mp3"
                    out_path = os.path.join(self.save_dir, filename)
                    export_audio(audio, out_path)

                    processed += 1
                    pct = int((processed / count) * 100)
                    self.progress_changed.emit(pct)

        except Exception as e:
            print("Error in MixWorker:", e)
        finally:
            self.finished.emit()
