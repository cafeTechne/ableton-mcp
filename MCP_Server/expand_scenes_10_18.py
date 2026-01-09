"""
Expand Scenes 10-18 with F# Mixolydian Chiptune Content

SAFETY: Only populates clip indices 9-17. Does NOT modify tracks or scenes 1-8.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import generate_chord_progression_advanced
from mcp_tooling.basslines import generate_bassline_from_progression
from mcp_tooling.constants import PROGRESSIONS

def expand_scenes():
    conn = get_ableton_connection()
    
    # Scene definitions: (clip_index, mood_name, progression, key, scale, bass_style)
    # F# Mixolydian for major, D# minor (relative minor) for minor progressions
    scenes = [
        (9,  "Heroic",   "chip_heroic",     "F#", "mixolydian", "octave"),
        (10, "Gothic",   "chip_gothic",     "D#", "minor",      "simple"),
        (11, "Action",   "chip_action",     "F#", "mixolydian", "syncopated"),
        (12, "Bouncy",   "chip_bouncy",     "F#", "mixolydian", "octave"),
        (13, "Power",    "chip_power",      "F#", "mixolydian", "simple"),
        (14, "Boss",     "chip_boss_minor", "D#", "minor",      "syncopated"),
        (15, "Stage",    "chip_stage",      "F#", "mixolydian", "jazz_walking"),
        (16, "Dance",    "chip_dance",      "D#", "minor",      "syncopated"),
        (17, "Triumph",  "chip_triumph",    "F#", "mixolydian", "octave"),
    ]
    
    print("Expanding Scenes 10-18 (clip indices 9-17)...")
    print("=" * 50)
    
    # Ensure enough scenes exist
    print("\n📋 Ensuring scenes exist...")
    for i in range(18):
        try:
            conn.send_command("create_scene", {"index": -1})
        except:
            pass  # May already exist
    
    # Track 0: Chords (using generator)
    print("\n🎹 Track 0 (Chords):")
    for clip_idx, mood, progression, key, scale, _ in scenes:
        try:
            result = generate_chord_progression_advanced(
                track_index=0,
                clip_index=clip_idx,
                key=key,
                scale=scale,
                progression=progression,
                beats_per_chord=4.0,
                total_bars=4,
                velocity=90
            )
            # Label the clip
            conn.send_command("set_clip_name", {
                "track_index": 0,
                "clip_index": clip_idx,
                "name": f"{mood} ({key} {scale})"
            })
            print(f"  Scene {clip_idx + 1}: {mood} - {progression} ({key} {scale})")
        except Exception as e:
            print(f"  Scene {clip_idx + 1} FAILED: {e}")
    
    # Track 1: Bass
    print("\n🎸 Track 1 (Bass):")
    
    style_map = {
        "simple": "rock",
        "octave": "rock",
        "syncopated": "funk",
        "jazz_walking": "jazz"
    }
    
    for clip_idx, mood, progression, key, scale, bass_style in scenes:
        try:
            chords = PROGRESSIONS.get(progression, ["I", "IV", "V", "I"])
            
            notes = generate_bassline_from_progression(
                chords=chords,
                key=key,
                scale=scale,
                beats_per_chord=4.0,
                style=style_map.get(bass_style, "rock"),
                velocity=100,
                octave=2
            )
            
            clip_length = len(chords) * 4.0
            try:
                conn.send_command("delete_clip", {"track_index": 1, "clip_index": clip_idx})
            except:
                pass
            
            conn.send_command("create_clip", {
                "track_index": 1,
                "clip_index": clip_idx,
                "length": clip_length
            })
            
            conn.send_command("add_notes_to_clip", {
                "track_index": 1,
                "clip_index": clip_idx,
                "notes": notes
            })
            
            conn.send_command("set_clip_name", {
                "track_index": 1,
                "clip_index": clip_idx,
                "name": f"{mood} Bass ({bass_style})"
            })
            print(f"  Scene {clip_idx + 1}: {mood} - {bass_style} ({key} {scale})")
        except Exception as e:
            print(f"  Scene {clip_idx + 1} FAILED: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Scenes 10-18 populated!")
    print("Fire scenes 10-18 to hear the new content.")

if __name__ == "__main__":
    expand_scenes()
