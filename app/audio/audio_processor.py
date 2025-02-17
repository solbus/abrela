from pydub import AudioSegment
import os

# Determine the base directory (two levels up from the current file)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

# Construct the full path to ffmpeg.exe
ffmpeg_path = os.path.join(base_dir, 'vendor', 'ffmpeg.exe')

# Assign the path to pydub's AudioSegment converter
AudioSegment.converter = ffmpeg_path

# Construct the path to the 'vendor' directory
vendor_dir = os.path.join(base_dir, 'vendor')

# Add the 'vendor' directory to the system PATH
os.environ["PATH"] = vendor_dir + os.pathsep + os.environ.get("PATH", "")

"""
This was just for testing. Keeping in case I break something.
import subprocess

try:
    # Check ffmpeg version
    subprocess.run([AudioSegment.converter, '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Check ffprobe version
    subprocess.run(['ffprobe', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("ffmpeg and ffprobe are accessible.")
except Exception as e:
    print(f"Error accessing ffmpeg or ffprobe: {e}")
"""

# -------------------
# 1. Loading / Saving
# -------------------

def load_audio(file_path: str) -> AudioSegment:
    """
    Load an MP3 (or other format) via pydub into an AudioSegment.
    Ensure it’s 44.1kHz, stereo, and 32 bits per sample in pydub’s internal representation.
    """
    audio = AudioSegment.from_file(file_path)  # pydub will know format from extension

    # Force 44.1 kHz, stereo, 32-bit sample width (4 bytes => 32-bit int)
    audio = audio.set_frame_rate(44100).set_channels(2).set_sample_width(4)

    print(f"[DEBUG] load_audio({file_path}): "
          f"length={len(audio)} ms, "
          f"dBFS={audio.dBFS if audio.rms != 0 else 'N/A (silent?)'}")

    return audio

def export_audio(audio: AudioSegment, out_path: str):
    """
    Export final audio at 320 kbps MP3, 44.1kHz, stereo, with 32 bits per sample internally.
    """
    audio.export(out_path, format="mp3", bitrate="320k")

    print(f"[DEBUG] export_audio -> {out_path}")

# --------------
# 2. Basic Fades
# --------------

def apply_fade_in(audio: AudioSegment, fade_duration_ms: int) -> AudioSegment:
    """
    Fade from 0% to 100% volume over the given duration in milliseconds.
    """
    if fade_duration_ms <= 0:
        return audio
    return audio.fade_in(fade_duration_ms)

def apply_fade_out(audio: AudioSegment, fade_duration_ms: int) -> AudioSegment:
    """
    Fade from 100% down to 0% volume over the given duration in milliseconds.
    """
    if fade_duration_ms <= 0:
        return audio
    return audio.fade_out(fade_duration_ms)
