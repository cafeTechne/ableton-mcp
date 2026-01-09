import sys
import random
from pathlib import Path

# Add the project root to sys.path so we can import mcp_tooling
sys.path.append(str(Path(__file__).resolve().parent))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import (
    generate_chord_progression_advanced as gen_chords,
    generate_bassline_advanced_wrapper as gen_bass
)
from mcp_tooling.drummer import generate_drum_pattern, list_genres
from mcp_tooling.devices import search_and_load_device

def build_chiptune():
    conn = get_ableton_connection()
    
    # 0. Ensure Drum Kit is loaded (606)
    print("Ensuring 606 Core Kit on Track 2...")
    search_and_load_device(track_index=2, query="606 Core Kit")

    # 1. Define F# Mixolydian Progressions
    # Note: In F# Mixolydian (v is minor, bVII is major)
    progressions = [
        "I bVII IV I",                  # Classic Mixolydian
        "I IV v bVII",                  # Soulful
        "I ii v I",                       # Jazz-ish Mixolydian
        "I bVII vi v IV",               # Descending
        "I IV bVII IV I bVII IV I",     # 8-chord Rocker
        "v IV bVII I",                  # Turnaround feel
        "I vi ii V"                      # Standard (using V instead of v for tension)
    ]
    
    # Drum genres for variety
    drum_genres = ['breakbeat', 'hip_hop', 'trap', 'footwork', 'garage', 'dubstep', 'house']
    
    print("Building 8 scenes of F# Mixolydian magic...")
    
    # We'll fill scenes 0 to 7 (8 scenes total)
    for i in range(8):
        # Choose or cycle progressions
        prog = progressions[i % len(progressions)]
        genre = drum_genres[i % len(drum_genres)]
        
        # Calculate bars. User asked for 16-bar bass pattern. 
        # Let's make the whole scene 16 bars for consistency.
        num_bars = 16
        beats_per_chord = (num_bars * 4) / len(prog.split())
        
        print(f"--- Scene {i+1} (Slot {i}) ---")
        print(f"Progression: {prog} | Genre: {genre} | Length: {num_bars} bars")

        # Lead Chords (Track 0)
        try:
            res = gen_chords(
                track_index=0, 
                clip_index=i, 
                key='F#', 
                scale='mixolydian', # Explicit mixolydian
                progression=prog, 
                beats_per_chord=beats_per_chord, 
                total_bars=num_bars, 
                arpeggiate=True
            )
            # Label the clip for improvisation
            conn.send_command("set_clip_name", {"track_index": 0, "clip_index": i, "name": prog})
            print(f"  Chords: {res} (Labeled: {prog})")
        except Exception as e:
            print(f"  Chords failed: {e}")

        # Jazz Walking Bass (Track 1)
        try:
            # User specifically asked for 'jazz' walking and 16 bars
            res = gen_bass(
                track_index=1, 
                clip_index=i, 
                key='F#', 
                scale='mixolydian', 
                progression=prog, 
                beats_per_chord=1.0, # Quarter note walk
                total_bars=num_bars, 
                style='jazz', 
                octave=2
            )
            print(f"  Bass: {res}")
        except Exception as e:
            print(f"  Bass failed: {e}")

        # Drums (Track 2)
        try:
            res = generate_drum_pattern(
                track_index=2,
                clip_index=i,
                genre=genre,
                bars=num_bars,
                humanize=0.08,
                clear_existing=True
            )
            print(f"  Drums: {res}")
        except Exception as e:
            print(f"  Drums failed: {e}")

    # 4. Play Scene 1
    print("Firing Scene 1 and starting playback...")
    conn.send_command('fire_scene_by_index', {'scene_index': 0})
    conn.send_command('start_playback', {})
    
    print("Arrangement ready! 🕹️ 8 scenes populated with 16-bar Jazz Walking Basslines.")

if __name__ == "__main__":
    build_chiptune()
