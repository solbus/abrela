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

import subprocess

try:
    # Check ffmpeg version
    subprocess.run([AudioSegment.converter, '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # Check ffprobe version
    subprocess.run(['ffprobe', '-version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print("ffmpeg and ffprobe are accessible.")
except Exception as e:
    print(f"Error accessing ffmpeg or ffprobe: {e}")

import time
import threading
from app.audio.audio_processor import export_audio

def create_final_mix(segments, timeline_entries, output_path, progress_callback=None):
    print("[DEBUG] create_final_mix called.")
    print(f"[DEBUG]   Number of segments={len(segments)}")
    print(f"[DEBUG]   timeline_entries={len(timeline_entries)} items")

    final_mix = AudioSegment.silent(duration=0, frame_rate=44100).set_channels(2).set_sample_width(4)

    if not segments:
        final_mix = AudioSegment.silent(duration=1000, frame_rate=44100).set_channels(2).set_sample_width(4)
        export_audio(final_mix, output_path)
        print(f"[DEBUG]   No segments, exported 1 second of silence to {output_path}")
        return

    total_segments = len(segments)
    # Allocate 35% to this step (from 20% up to 55%).
    portion_for_mixing = 55.0 - 20.0
    portion_per_segment = portion_for_mixing / total_segments
    current_progress = 20.0  # Left off at 20% after build_segments

    # Place the first track
    final_mix = segments[0]["audio_segment"]
    mix_time = len(final_mix)
    print(f"[DEBUG]   Started final_mix with first segment, length={mix_time} ms")

    if progress_callback:
        current_progress += portion_per_segment
        progress_callback(int(current_progress))

    print(f"[DEBUG]   final_mix after first overlay -> length={len(final_mix)} ms, "
          f"dBFS={final_mix.dBFS if final_mix.rms != 0 else 'N/A (silent?)'}")

    # Overlay subsequent tracks
    for i in range(1, len(segments)):
        print(f"[DEBUG] -- Now placing segment #{i} using track {i-1}'s transition_data for overlap --")
        track_segment = segments[i]["audio_segment"]
        prev_transition_data = timeline_entries[i-1].get("transition_data") or {}
        transition_type = prev_transition_data.get("type", "")
        is_custom = (transition_type == "Studio")

        fade_in = prev_transition_data.get("target_fade_in_duration", 0)
        fade_out = prev_transition_data.get("source_fade_out_duration", 0)

        print(f"[DEBUG]   For track #{i}, fade_in={fade_in}, fade_out={fade_out} (from track {i-1}'s data)")

        if is_custom:
            start_position = mix_time - (fade_in + fade_out)
            if start_position < 0:
                start_position = 0
            print(f"[DEBUG]   (Segment #{i}) custom transition. start_position={start_position}, fade_in={fade_in}, fade_out={fade_out}")
        else:
            start_position = mix_time
            print(f"[DEBUG]   (Segment #{i}) default transition. start_position={start_position} (no overlap)")

        track_end_time = start_position + len(track_segment)

        if track_end_time > len(final_mix):
            needed = track_end_time - len(final_mix)
            extra_silence = AudioSegment.silent(
                duration=needed,
                frame_rate=44100
            ).set_channels(2).set_sample_width(4)

            final_mix = final_mix + extra_silence
            print(f"[DEBUG]   Padded final_mix with {needed} ms of silence, new length={len(final_mix)} ms")

        final_mix = final_mix.overlay(track_segment, position=start_position)

        mix_time = max(mix_time, track_end_time)
        print(f"[DEBUG]   Overlaid track #{i}, track_end_time={track_end_time}, mix_time={mix_time}")

        print(f"[DEBUG]   final_mix after overlay #{i} -> length={len(final_mix)} ms, "
              f"dBFS={final_mix.dBFS if final_mix.rms != 0 else 'N/A (silent?)'}")
        
        if progress_callback:
            current_progress += portion_per_segment
            progress_callback(int(current_progress))

    # 1) Define function that does the actual export
    def do_export():
        export_audio(final_mix, output_path)

    # 2) Start that export in a separate thread
    export_thread = threading.Thread(target=do_export)
    export_thread.start()

    # 3) Meanwhile, increment progress from 55% up to 99% for last step
    if progress_callback:
        for p in range(int(current_progress), 100):
            # Sleep briefly for the user to see movement
            time.sleep(0.4)

            # If the export is done early, break out
            if not export_thread.is_alive():
                break
            progress_callback(p)

    # 4) Wait for the export to finish entirely
    export_thread.join()

    # 5) Now finalize progress at 99 (if not already there), then 100.
    if progress_callback:
        progress_callback(99)
        progress_callback(100)

    print("[DEBUG] create_final_mix complete.\n")
