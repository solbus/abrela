from app.audio.audio_processor import (
    load_audio,
    apply_fade_in,
    apply_fade_out,
)

def build_segments(timeline_entries, progress_callback=None):
    print("[DEBUG] build_segments() called")
    if not timeline_entries:
        print("[DEBUG] timeline_entries is empty. Returning no segments.")
        return []

    total_tracks = sum(1 for e in timeline_entries if e.get("type") == "track")

    # Move from 0% to 20% of the progress bar this step
    portion_per_track = 20.0 / total_tracks if total_tracks else 0
    current_progress = 0.0

    # Print out each entry just to confirm
    print("[DEBUG] The timeline_entries are:")
    for idx, entry in enumerate(timeline_entries):
        print(f"  {idx}: {entry}")

    segments = []

    for i, entry in enumerate(timeline_entries):
        # Skip non-audio items
        if entry.get("type") != "track":
            print(f"[DEBUG] Skipping timeline_entries[{i}] because it's not a 'track'. entry={entry}")
            continue

        print(f"\n[DEBUG] ---- Building segment for track index {i} ----")
        print(f"[DEBUG]   album_title={entry.get('album_title')}, track_title={entry.get('track_title')}")

        # Load the entire audio file
        file_path = entry["file_path"]
        print(f"[DEBUG]   loading audio from {file_path}")
        audio_full = load_audio(file_path)
        print(f"[DEBUG]   loaded audio length = {len(audio_full)} ms, "
              f"dBFS={audio_full.dBFS if audio_full.rms != 0 else 'N/A (silent?)'}")

        # Identify first/middle/last
        is_first = (i == 0)
        is_last = (i == len(timeline_entries) - 1)

        prev_transition_data = {}
        if i > 0:
            prev_transition_data = timeline_entries[i-1].get("transition_data") or {}

        current_transition_data = entry.get("transition_data") or {}

        # Helper function
        def is_custom(td):
            return (td.get("type") == "Studio")

        # Determine if incoming transition is custom or default
        if i == 0:
            in_transition_type = "none"
        else:
            in_transition_type = "custom" if is_custom(prev_transition_data) else "default"

        # Determine if outgoing transition is custom or default
        out_transition_type = "custom" if is_custom(current_transition_data) else "default"

        print(f"[DEBUG]   in_transition_type={in_transition_type}, out_transition_type={out_transition_type}")

        # The final slice from audio_full
        segment_crop = None

        # Then the usual logic
        if not is_first and not is_last:
            if in_transition_type == "custom" and out_transition_type == "custom":
                #
                # INCOMING (fade_in) from track i-1's data:
                #
                in_start_ms = prev_transition_data.get("target_fade_in_timestamp", 0)
                if in_start_ms < 0:
                    in_start_ms = 0
                fade_in_ms = prev_transition_data.get("target_fade_in_duration", 0)

                #
                # OUTGOING (fade_out) from track i's own data:
                #
                fade_out_ms = current_transition_data.get("source_fade_out_duration", 0)
                out_timestamp = current_transition_data.get("timestamp", len(audio_full))

                # Pull the next-track fade-in from *this* track’s data.
                # Because "target_fade_in_duration" is used by the upcoming track
                # (track i+1) to fade in on top of the tail end of track i.
                next_fade_in_ms = current_transition_data.get("target_fade_in_duration", 0)

                # We'll define the raw start/end points for slicing:
                # length_needed = (out_timestamp - in_start_ms) + fade_in_ms + fade_out_ms
                length_needed = (out_timestamp - in_start_ms) + fade_out_ms + next_fade_in_ms
                if length_needed < 0:
                    length_needed = 0
                end_ms = in_start_ms + length_needed
                if end_ms > len(audio_full):
                    end_ms = len(audio_full)

                print(f"[DEBUG]   middle->custom/custom slice: start_ms={in_start_ms}, end_ms={end_ms}, length={length_needed}")
                segment_crop = audio_full[in_start_ms:end_ms]

                # Now apply fade_in from prev track, fade_out from current:
                if fade_in_ms > 0:
                    print(f"[DEBUG]   applying fade_in of {fade_in_ms} ms (from prev track data)")
                    segment_crop = apply_fade_in(segment_crop, fade_in_ms)
                    print(f"[DEBUG]     after fade_in: length={len(segment_crop)} ms, "
                          f"dBFS={segment_crop.dBFS if segment_crop.rms != 0 else 'N/A (silent?)'}")

                if fade_out_ms > 0:
                    print(f"[DEBUG]   applying fade_out of {fade_out_ms} ms (from current track data)")
                    segment_crop = apply_fade_out(segment_crop, fade_out_ms)
                    print(f"[DEBUG]     after fade_out: length={len(segment_crop)} ms, "
                          f"dBFS={segment_crop.dBFS if segment_crop.rms != 0 else 'N/A (silent?)'}")

            elif in_transition_type == "custom" and out_transition_type == "default":
                print("[DEBUG]   middle->custom/default -> applying custom fade-in (from previous track), then full track thereafter.")

                # 1) Determine where this track should start (based on previous track’s custom transition)
                in_start_ms = prev_transition_data.get("target_fade_in_timestamp", 0)
                if in_start_ms < 0:
                    in_start_ms = 0
                if in_start_ms >= len(audio_full):
                    # If the timestamp is beyond this track's length, return a silent segment
                    print("[DEBUG]   in_start_ms is beyond track length; creating a 0ms silent segment.")
                    segment_crop = audio_full[:0]  # 0ms slice
                else:
                    # Slice from in_start_ms to the very end of the file
                    segment_crop = audio_full[in_start_ms:]

                # 2) Apply the custom fade-in from the previous track’s transition data
                fade_in_ms = prev_transition_data.get("target_fade_in_duration", 0)
                if fade_in_ms > 0:
                    print(f"[DEBUG]   applying fade_in of {fade_in_ms} ms (from prev track data)")
                    segment_crop = apply_fade_in(segment_crop, fade_in_ms)
                    print(f"[DEBUG]     after fade_in: length={len(segment_crop)} ms, "
                        f"dBFS={segment_crop.dBFS if segment_crop.rms != 0 else 'N/A (silent?)'}")

            elif in_transition_type == "default" and out_transition_type == "custom":
                print("[DEBUG]   middle->default/custom -> starting from 0, applying custom slice/fade-out for this track.")

                # 1) Identify how far into this track we keep audio, plus extra for fade-out
                c_timestamp = current_transition_data.get("timestamp", len(audio_full))
                if c_timestamp < 0:
                    c_timestamp = 0
                fade_out_ms = current_transition_data.get("source_fade_out_duration", 0)
                c_fade_in_ms = current_transition_data.get("target_fade_in_duration", 0)

                # The total length needed is from 0 up to c_timestamp + fade_out
                length_needed = c_timestamp + fade_out_ms + c_fade_in_ms
                if length_needed > len(audio_full):
                    length_needed = len(audio_full)

                # 2) Slice from 0 up to length_needed
                segment_crop = audio_full[:length_needed]
                print(f"[DEBUG]   slicing track from start=0 to end={length_needed} ms")

                # 3) Apply custom fade-out
                if fade_out_ms > 0:
                    print(f"[DEBUG]   applying fade_out of {fade_out_ms} ms (from current track data)")
                    segment_crop = apply_fade_out(segment_crop, fade_out_ms)
                    print(f"[DEBUG]     after fade_out: length={len(segment_crop)} ms, "
                        f"dBFS={segment_crop.dBFS if segment_crop.rms != 0 else 'N/A (silent?)'}")

            else:
                print("[DEBUG]   middle->default/default not yet implemented (placeholder). Using full track.")
                segment_crop = audio_full

        elif is_first:
            if out_transition_type == "custom":
                c_timestamp = current_transition_data.get("timestamp", 0)
                # For the very first track, there's no "incoming" fade_in from the previous track.
                # fade_in_ms = 0 if i == 0 (since there's no track -1).
                fade_in_ms = 0  
                # We do consider fade-out from track i's data:
                c_fade_in_dur = current_transition_data.get("target_fade_in_duration", 0)
                c_fade_out_dur = current_transition_data.get("source_fade_out_duration", 0)

                length_needed = c_timestamp + c_fade_in_dur + c_fade_out_dur

                if length_needed < 0:
                    length_needed = 0
                if length_needed > len(audio_full):
                    length_needed = len(audio_full)

                segment_crop = audio_full[0:length_needed]
                print(f"[DEBUG]   applying fade_out of {c_fade_out_dur} ms (from current track data)")

                if c_fade_out_dur > 0:
                    print(f"[DEBUG]   applying fade_out of {c_fade_out_dur} ms")
                    segment_crop = apply_fade_out(segment_crop, c_fade_out_dur)

            else:
                # ...
                print("[DEBUG]   first->default, using full track.")
                segment_crop = audio_full

        else:  # is_last
            if in_transition_type == "custom":
                p_tf_in_ts = prev_transition_data.get("target_fade_in_timestamp", 0)
                if p_tf_in_ts < 0:
                    p_tf_in_ts = 0
                if p_tf_in_ts > len(audio_full):
                    p_tf_in_ts = len(audio_full)

                segment_crop = audio_full[p_tf_in_ts:]
                print(f"[DEBUG]   last->custom slice: start={p_tf_in_ts} to end({len(audio_full)} ms)")

                # last track's "entering fade_in" also belongs to the previous track's data:
                fade_in_ms = prev_transition_data.get("target_fade_in_duration", 0)
                if fade_in_ms > 0:
                    print(f"[DEBUG]   applying fade_in of {fade_in_ms} ms (from prev track data)")
                    segment_crop = apply_fade_in(segment_crop, fade_in_ms)
                    print(f"[DEBUG]     after fade_in: length={len(segment_crop)} ms, "
                          f"dBFS={segment_crop.dBFS if segment_crop.rms != 0 else 'N/A (silent?)'}")

            else:
                print("[DEBUG]   last->default, using full track.")
                segment_crop = audio_full

        # If none of the above assigned a slice, just default to the entire file
        if segment_crop is None:
            segment_crop = audio_full

        # Standardize sample rate/channels/bit-depth
        segment_crop = (
            segment_crop
            .set_frame_rate(44100)
            .set_channels(2)
            .set_sample_width(4)
        )

        segment_info = {
            "audio_segment": segment_crop,
            "track_title": entry.get("track_title", "Unknown Track"),
            "album_title": entry.get("album_title", "Unknown Album"),
        }

        # Quick debug about the final slice length
        print(f"[DEBUG]   Final cropped segment i={i}: length={len(segment_crop)} ms, "
              f"dBFS={segment_crop.dBFS if segment_crop.rms != 0 else 'N/A (silent?)'}")

        if progress_callback and total_tracks > 0:
            current_progress += portion_per_track
            progress_callback(int(current_progress))

        segments.append(segment_info)

    print(f"[DEBUG] Done building segments. Return count={len(segments)}\n")
    return segments
