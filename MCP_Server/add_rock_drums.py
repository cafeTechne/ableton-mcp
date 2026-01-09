"""
Add Rock Drums Track - Chiptune Expansion

Creates exactly ONE new MIDI track with energetic rock/punk drum patterns.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.drummer import generate_drum_pattern, search_patterns
from mcp_tooling.devices import search_and_load_device

def add_rock_drums():
    conn = get_ableton_connection()
    
    # 1. Find existing track count using get_track_info fallback
    track_count = 0
    for i in range(100):
        try:
            conn.send_command("get_track_info", {"track_index": i})
            track_count = i + 1
        except:
            break
    
    print(f"Found {track_count} existing tracks.")
    
    # 2. Create ONE new MIDI track at the end
    new_track_idx = track_count
    print(f"Creating new MIDI track at index {new_track_idx}...")
    resp = conn.send_command("create_midi_track", {"index": -1})
    new_track_idx = resp.get("index", track_count)
    print(f"Created track at index {new_track_idx}")
    
    # 3. Name it
    conn.send_command("set_track_name", {"track_index": new_track_idx, "name": "Rock Drums"})
    print("Named track 'Rock Drums'")
    
    # 4. Load 606 Core Kit
    print("Loading 606 Core Kit...")
    search_and_load_device(track_index=new_track_idx, query="606 Core Kit")
    
    # 5. Find rock patterns
    rock_patterns = search_patterns("rock", limit=10)
    if not rock_patterns:
        rock_patterns = search_patterns("break", limit=10)  # Fallback
    
    print(f"Found {len(rock_patterns)} rock/break patterns")
    
    # 6. Populate 8 scenes with rock patterns
    for i in range(8):
        pattern = rock_patterns[i % len(rock_patterns)] if rock_patterns else None
        
        if pattern:
            try:
                res = generate_drum_pattern(
                    track_index=new_track_idx,
                    clip_index=i,
                    genre=pattern.get("genre", "breakbeat"),
                    pattern_name=pattern.get("name"),
                    bars=4,
                    humanize=0.05,
                    clear_existing=True
                )
                # Label the clip
                conn.send_command("set_clip_name", {
                    "track_index": new_track_idx,
                    "clip_index": i,
                    "name": pattern.get("name", f"Rock {i+1}")
                })
                print(f"  Scene {i+1}: {pattern.get('name')}")
            except Exception as e:
                print(f"  Scene {i+1} failed: {e}")
        else:
            print(f"  Scene {i+1}: No pattern available")
    
    print(f"\n🥁 Rock Drums track created at index {new_track_idx}!")
    print("Fire scenes 1-8 to hear the energetic beats!")

if __name__ == "__main__":
    add_rock_drums()
