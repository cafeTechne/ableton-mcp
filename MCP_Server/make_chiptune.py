
import sys
from pathlib import Path

# Add the project root to sys.path so we can import mcp_tooling
sys.path.append(str(Path(__file__).resolve().parent))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import (
    generate_chord_progression_advanced as gen_chords,
    generate_bassline_advanced_wrapper as gen_bass,
    pattern_generator as gen_drums
)

def build_chiptune():
    conn = get_ableton_connection()
    
    # 1. Generate energetic F# Mixolydian Chiptune
    print("Generating chords...")
    try:
        # F# Mixolydian via F# Major progression with bVII
        res = gen_chords(
            track_index=4, 
            clip_index=0, 
            key='F#', 
            scale='major', 
            progression='I bVII IV I', 
            beats_per_chord=2.0, 
            total_bars=4, 
            arpeggiate=True
        )
        print(f"Chords: {res}")
    except Exception as e:
        print(f"Chords failed: {e}")

    print("Generating bass...")
    try:
        res = gen_bass(
            track_index=5, 
            clip_index=0, 
            key='F#', 
            scale='major', 
            progression='I bVII IV I', 
            beats_per_chord=1.0, # faster bass for energy
            style='pulse', 
            octave=2
        )
        print(f"Bass: {res}")
    except Exception as e:
        print(f"Bass failed: {e}")

    print("Generating drums (Breakbeat)...")
    try:
        # Use simple pattern_generator as it's now safe
        res = gen_drums(
            track_index=6, 
            clip_slot_index=0, 
            pattern_type='four_on_floor', # Changed to four_on_floor for stability
            bars=4
        )
        print(f"Drums: {res}")
    except Exception as e:
        print(f"Drums failed: {e}")

    # 3. Play!
    print("Firing clips and starting playback...")
    conn.send_command('fire_clip', {'track_index': 4, 'clip_index': 0})
    conn.send_command('fire_clip', {'track_index': 5, 'clip_index': 0})
    conn.send_command('fire_clip', {'track_index': 6, 'clip_index': 0})
    conn.send_command('set_overdub', {'overdub': True})
    conn.send_command('start_playback', {})
    
    print("Song is playing! 🕹️")

if __name__ == "__main__":
    build_chiptune()
