import sys
import os
import time

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.ableton_helpers import ensure_track_exists
from mcp_tooling.util import load_device_by_name
from mcp_tooling.generators import (
    generate_chord_progression_advanced,
    generate_bassline_advanced_wrapper,
    generate_brass_advanced_wrapper,
    generate_brass_advanced_wrapper,
    generate_woodwinds_advanced_wrapper,
    pattern_generator,
    add_basic_drum_pattern,
    generate_strings_advanced_wrapper
)

def create_ska_track():
    print("🏁 Starting Ska Track Generation (G Minor, 140 BPM)...")
    conn = get_ableton_connection()
    
    # 1. Setup Global
    conn.send_command("set_tempo", {"tempo": 140.0})
    KEY = "G Minor"
    SCALE = "minor"
    # i - VII - VI - V7 is classic Andalusian/Ska energy
    PROG = "i VII VI V7" 
    BARS = 8
    
    def prepare_track(idx, name, device_search):
        """Helper to ensure clean MIDI track state."""
        print(f"\n🎵 Preparing Track {idx}: {name}")
        
        # 1. Ensure exists
        real_idx = ensure_track_exists(idx, prefer="midi")
        
        # 2. Check Type & Clean
        info = conn.send_command("get_track_info", {"track_index": real_idx})
        if info.get("is_audio_track"):
            print(f"   ⚠️ Track {real_idx} is Audio. Deleting and recreating as MIDI...")
            conn.send_command("delete_track", {"track_index": real_idx})
            time.sleep(1.0)
            real_idx = ensure_track_exists(idx, prefer="midi")
            
        # 3. Rename
        conn.send_command("set_track_name", {"track_index": real_idx, "name": name})
        
        # 4. Clear Clip Slot 0
        try:
            conn.send_command("delete_clip", {"track_index": real_idx, "clip_index": 0})
        except Exception:
            pass # No clip to delete
            
        # 5. Load Device
        if device_search:
            print(f"   💾 Loading '{device_search}'...")
            load_device_by_name(real_idx, device_search, "instruments")
            time.sleep(1.5)
            
        return real_idx

    # 2. Drums
    idx_drums = prepare_track(0, "Ska Drums", "Kit")
    
    # Generate Beat - Ska uses a 'one-drop' or strong backbeat. 
    # Our pattern_generator 'rock' is decent, or we can use basic 'rock'
    # High hats are crucial on offbeats for Ska, but let's start with a solid beat.
    pattern_generator(
        track_index=idx_drums,
        clip_slot_index=0,
        pattern_type="rock", # Solid backbeat foundation
        bars=BARS,
        velocity=110
    )
    time.sleep(1.0)
    # Layer Hi-Hats on offbeats?
    # We'll rely on the generated beat for now.
    
    # 3. Bass
    idx_bass = prepare_track(1, "Ska Bass", "Bass-Electric")
    
    generate_bassline_advanced_wrapper(
        track_index=idx_bass,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="ska", # Explicit ska style for walking bass
        beats_per_chord=4.0,
        velocity=115,
        octave=1
    )
    time.sleep(1.0)
    
    # 4. Keys
    idx_keys = prepare_track(2, "Ska Keys", "Organ")
    
    # Use 'reggae' style from strings generator to get the offbeat chop!
    generate_strings_advanced_wrapper(
        track_index=idx_keys,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="reggae", # HACK: Use reggae strings logic for offbeat chords
        beats_per_chord=4.0,
        velocity=110,
        octave=3
    )
    time.sleep(1.0)

    # 5. Brass
    idx_brass = prepare_track(3, "Ska Brass", "Brass")
    
    generate_brass_advanced_wrapper(
        track_index=idx_brass,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="ska", # Explicit ska style
        beats_per_chord=4.0,
        velocity=120,
        octave=3
    )
    time.sleep(1.0)
    
    # 6. Woodwinds
    idx_winds = prepare_track(4, "Ska Sax", "Sax")
    
    generate_woodwinds_advanced_wrapper(
        track_index=idx_winds,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="reggae", # Reggae/Ska often share "swung" or linear melodic lines
        beats_per_chord=4.0,
        velocity=100,
        octave=4
    )
    time.sleep(1.0)
    
    print("\n✅ Ska Track Created! 🏁")

if __name__ == "__main__":
    create_ska_track()
