def ms_to_mmss(ms):
    ms = int(round(ms))
    seconds = ms // 1000
    m = seconds // 60
    s = seconds % 60
    return f"{m:02d}:{s:02d}"

def ms_to_hhmmss(ms):
    ms = int(round(ms))
    seconds = ms // 1000
    h = seconds // 3600
    seconds %= 3600
    m = seconds // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def ms_diff_to_minsec(ms):
    ms = int(round(ms))
    seconds = ms // 1000
    m = seconds // 60
    s = seconds % 60
    return f"{m}min {s}sec"

def sum_segments_duration(segments):
    total = 0
    for seg in segments:
        if seg['segment_type'] == 'track':
            total += (seg['end_ms'] - seg['start_ms'])
        else:
            total += seg['duration']
    return total

def get_transition_value(t, key, default=0):
    val = t.get(key, default)
    if val is None:
        return default
    return val

def find_track(albums_manager, album_title, track_title):
    all_albums = albums_manager.get_albums()
    for a in all_albums:
        if a['title'] == album_title:
            for t in a['tracks']:
                if t['track_title'] == track_title:
                    return a, t
    return None, None

def get_current_track_data(albums_manager, current_album_title, current_track_index):
    all_albums = albums_manager.get_albums()
    for a in all_albums:
        if a['title'] == current_album_title:
            return a, a['tracks'][current_track_index - 1]
    return None, None

def add_track_to_timeline(timeline_entries, from_album_title, from_track_index, to_album_title, to_track, default_transition=False, transition_data=None):
    track_duration_ms = to_track.get('duration', 180000)
    entry = {
        'type': 'track',
        'album_title': to_album_title,
        'track_title': to_track['track_title'],
        'duration': track_duration_ms,
        'default_transition': default_transition,
        'transition_data': transition_data
    }
    timeline_entries.append(entry)

def load_initial_timeline(albums_manager, current_album_title, current_track_index):
    album, track = get_current_track_data(albums_manager, current_album_title, current_track_index)
    track_duration_ms = track.get('duration', 180000)
    return [{
        'type': 'track',
        'album_title': album['title'],
        'track_title': track['track_title'],
        'duration': track_duration_ms,
        'default_transition': False,
        'transition_data': None
    }]

def compute_segments_from_timeline(timeline_entries):
    segs = []
    current_timeline_time = 0

    for i, entry in enumerate(timeline_entries):
        track_duration = entry['duration']
        current_offset = entry.get('starting_offset', 0)

        transition_data = entry.get('transition_data')
        if transition_data:
            # 1) Render the “source” portion
            timestamp = get_transition_value(transition_data, 'timestamp', 0)
            played_track_length = timestamp - current_offset
            segs.append({
                'segment_type': 'track',
                'album_title': entry['album_title'],
                'track_title': entry['track_title'],
                'start_ms': current_timeline_time,
                'end_ms': current_timeline_time + played_track_length,
                'full_duration_ms': played_track_length
            })
            current_timeline_time += played_track_length

            # 2) Render the “transition” segment
            source_fade_out = get_transition_value(transition_data, 'source_fade_out_duration', 0)
            target_fade_in  = get_transition_value(transition_data, 'target_fade_in_duration', 0)
            transition_time = source_fade_out + target_fade_in
            segs.append({
                'segment_type': 'transition',
                'duration': transition_time,
                'transition_data': transition_data,
            })
            current_timeline_time += transition_time

            # 3) Calculate the “starting_offset” for the next track
            target_fade_in_ts = get_transition_value(transition_data, 'target_fade_in_timestamp', 0)
            crossfade_consumed = target_fade_in_ts + source_fade_out + target_fade_in

            if i + 1 < len(timeline_entries):
                timeline_entries[i+1]['starting_offset'] = crossfade_consumed

        else:
            # No transition; just play the rest of the track
            played_track_length = track_duration - current_offset
            segs.append({
                'segment_type': 'track',
                'album_title': entry['album_title'],
                'track_title': entry['track_title'],
                'start_ms': current_timeline_time,
                'end_ms': current_timeline_time + played_track_length,
                'full_duration_ms': played_track_length
            })
            current_timeline_time += played_track_length

    return segs

def get_filtered_transitions(
    albums_manager,
    current_album_title,
    current_track_index,
    selected_albums
):
    album, track = get_current_track_data(
        albums_manager,
        current_album_title,
        current_track_index
    )
    if not album or not track:
        return False, []

    all_tracks = album['tracks']
    user_selected_all = (not selected_albums)
    album_is_owned = (album['title'] in selected_albums) if selected_albums else True

    default_exists = False
    if current_track_index < len(all_tracks) and (user_selected_all or album_is_owned):
        default_exists = True

    transitions = track.get('transitions', [])
    valid_transitions = []
    for t in transitions:
        target_album_title = t.get('target_album', album['title']) or album['title']
        if user_selected_all or (target_album_title in selected_albums):
            valid_transitions.append(t)

    return default_exists, valid_transitions
