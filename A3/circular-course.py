# modified by Michael Feldmann
#!/usr/bin/env python3
import sys
import json
import random

def generate_tracks(num_tracks: int, length_of_track: int):
    """
    Generates a data structure with 'num_tracks' circular tracks.
    Each track has exactly 'length_of_track' segments:
      - 1 segment: 'start-and-goal-t'
      - (length_of_track - 1) segments: 'segment-t-c'
    Returns a Python dict that can be serialized to JSON.
    """
    all_tracks = []

    for t in range(1, num_tracks + 1):
        track_id = str(t)
        segments = []
		# Verhinderung aufeinanderfolgende Verzweigungen
        split_last_time = False

        # First segment: start-and-goal-t
        start_segment_id = f"start-and-goal-{t}"
        if length_of_track == 1:
            # Edge case: track length is 1 => no "normal" segments, loops onto itself
            next_segments = [start_segment_id]
        else:
            next_segments = [f"segment-{t}-1"]

        start_segment = {
            "segmentId": start_segment_id,
            "type": "start-goal",
            "nextSegments": next_segments
        }
        
        # Caesar-Segment
        caesar_segment_id = f"caesar-{t}"
        caesar_segment = {
            "segmentId": caesar_segment_id,
            "type": "caesar",
            "nextSegments": next_segments
        }
        
        segments.append(start_segment)
        segments.append(caesar_segment)
        
        # Create normal segments: segment-t-c for c in [1..(L-1)] and Bottleneck-Segments and Slow-Down-Segments
        for c in range(1, length_of_track):
            seg_id = f"segment-{t}-{c}"
            # Zusätzlich SegmentType (zufällige Auswahl)
            seg_type = random.choice(['normal', 'bottleneck', 'slow-down'])
            
            if (
                c > 2 and c < length_of_track - 2  # Ausschluss des Anfangssegment und vor Start/Caesar
                and not split_last_time 		   # Verhinderung aufeinanderfolgende Verzweigungen
                and random.choices([True, False], weights=[25, 75], k=1)[0]   # Zufall, ob eine Verzweigung entsteht (25%)
            ):
                # Erzeuge Verzweigungen
                next_segs = [f"segment-{t}-{c}-1", f"segment-{t}-{c}-2"]

                # Sub-Segmente definieren
                sub_segment_1 = {
                    "segmentId": f"segment-{t}-{c}-1",
                    "type": random.choice(['normal', 'bottleneck']),
                    "nextSegments": [f"segment-{t}-{c+1}"]  # Beide führen zum regulären Ziel
                }
                sub_segment_2 = {
                    "segmentId": f"segment-{t}-{c}-2",
                    "type": random.choice(['normal', 'bottleneck']),
                    "nextSegments": [f"segment-{t}-{c+1}"]
                }
                segments.append(sub_segment_1)
                segments.append(sub_segment_2)
                segments[-3]["nextSegments"] = next_segs
                split_last_time = True
            else:
                # If this is the last normal segment, it loops back to 'start-and-goal-t'
                if c == length_of_track - 1:
                    next_segs = [start_segment_id, caesar_segment_id]
                else:
                    next_segs = [f"segment-{t}-{c+1}"]

                segment = {
                    "segmentId": seg_id,
                    "type": seg_type,
                    "nextSegments": next_segs
                }
                segments.append(segment)
                split_last_time = False

        track_definition = {
            "trackId": track_id,
            "segments": segments
        }
        all_tracks.append(track_definition)

    return {"tracks": all_tracks}


def main():
    if len(sys.argv) != 4:
        print(f"Usage: {sys.argv[0]} <num_tracks> <length_of_track> <output_file>")
        sys.exit(1)

    num_tracks = int(sys.argv[1])
    length_of_track = int(sys.argv[2])
    output_file = sys.argv[3]

    tracks_data = generate_tracks(num_tracks, length_of_track)

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(tracks_data, f, indent=2)
        f.write('\n')
    print(f"Successfully generated {num_tracks} track(s) of length {length_of_track} into '{output_file}'")

if __name__ == "__main__":
    main()
