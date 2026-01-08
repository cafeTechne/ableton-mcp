
import sys
import os
import time
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.ableton_helpers import ensure_track_exists, load_sample_to_simpler
from mcp_tooling.util import load_device_by_name
from mcp_tooling.generators import (
    generate_bassline_advanced_wrapper,
    generate_strings_advanced_wrapper
)

from mcp_tooling.util import search_cache, CACHE_FILE, SAMPLE_CACHE_FILE

def create_house_intro():
    print("🏠 Starting House Intro Generation (G Major, 124 BPM)...")
    conn = get_ableton_connection()
    
    # 1. Setup Global
    conn.send_command("set_tempo", {"tempo": 124.0})
    KEY = "G Major"
    SCALE = "major"
    PROG = "I vi V IV" 
    BARS = 8
    
    def select_from_cache(query, file_path, category=None):
        """Randomly select a cached item matching the query."""
        results = search_cache(file_path, query, limit=50)
        if not results:
            return None
        
        # Filter by category if needed
        if category:
            results = [r for r in results if r.get("category") == category]
            
        if not results:
            return None
            
        selected = random.choice(results)
        return selected # Return full item dict

    def prepare_track(idx, name):
        """Helper to ensure clean MIDI track state without destroying existing structure if possible."""
        print(f"\n🎵 Preparing Track {idx}: {name}")
        
        # Check if track exists and is compatible
        track_info = conn.send_command("get_track_info", {"track_index": idx})
        if track_info.get("status") != "error":
            # Track exists
            is_audio = track_info.get("is_audio_track", False)
            if is_audio:
                 # We need MIDI. Delete it.
                 print(f"   ⚠️ Track {idx} is Audio. Recreating as MIDI...")
                 conn.send_command("delete_track", {"track_index": idx})
                 time.sleep(0.5)
            else:
                 # It's MIDI (or Return/Master, but we assume index < track_count indicates valid)
                 # Just clear the clip
                 try:
                     conn.send_command("delete_clip", {"track_index": idx, "clip_index": 0})
                 except:
                     pass
                 # Rename
                 conn.send_command("set_track_name", {"track_index": idx, "name": name})
                 return idx
        
        # Determine real index or create
        real_idx = ensure_track_exists(idx, prefer="midi", allow_create=True)
        conn.send_command("set_track_name", {"track_index": real_idx, "name": name})
        return real_idx

    # =========================================================================
    # 2. Drums: Sliced Loop
    # =========================================================================
    idx_drums = prepare_track(0, "House Loop")
    
    # Try to find a tasteful sample in cache
    drum_query = "House Loop"
    cached_sample = select_from_cache("Loop", SAMPLE_CACHE_FILE, "samples")
    if cached_sample:
        print(f"   ✨ Selected from Cache: '{cached_sample.get('name')}'")
        drum_query = cached_sample.get("name")
    else:
        print("   ⚠️ Cache miss. Using generic query 'House Loop'")
        
    # Use the reusable helper to load a valid audio loop into Simpler
    if load_sample_to_simpler(idx_drums, drum_query, backup_query="Loop"):
        # Configure Simpler to Slice Mode
        print("   🔪 Configuring Simpler: Slice Mode...")
        conn.send_command("set_simpler_playback_mode", {
            "track_index": idx_drums,
            "mode": "slice"
        })
        time.sleep(1.0)
        
        # Generate Slicing Pattern (trigger slices C1, C#1, etc.)
        print("   🎹 Generating Slice Pattern...")
        notes = []
        
        # Kick (Slice 1 / C1 / 36) at velocity 120 on quarter notes
        for i in range(BARS * 4):
            notes.append({
                "pitch": 36, # C1
                "start_time": float(i),
                "duration": 0.25,
                "velocity": 120
            })
            
        # Random other slices (C#1 to G1) on offbeats for texture
        slices = [37, 38, 39, 40, 41, 42, 43] # ~7 slices
        for i in range(BARS * 4):
            # 8th notes
            if random.random() > 0.3:
                notes.append({
                    "pitch": random.choice(slices),
                    "start_time": float(i) + 0.5,
                    "duration": 0.25,
                    "velocity": 90 + random.randint(-10, 10)
                })
            # 16th notes
            if random.random() > 0.6:
                 notes.append({
                    "pitch": random.choice(slices),
                    "start_time": float(i) + 0.25,
                    "duration": 0.25,
                    "velocity": 80 + random.randint(-10, 10)
                })
                 notes.append({
                    "pitch": random.choice(slices),
                    "start_time": float(i) + 0.75,
                    "duration": 0.25,
                    "velocity": 80 + random.randint(-10, 10)
                })

        conn.send_command("create_clip", {"track_index": idx_drums, "clip_index": 0, "length": float(BARS)})
        conn.send_command("add_notes_to_clip", {
            "track_index": idx_drums,
            "clip_index": 0,
            "notes": notes
        })
    else:
        print("   ❌ Failed to load valid drum loop.")

    # =========================================================================
    # 3. Bass: Classic House
    # =========================================================================
    idx_bass = prepare_track(1, "House Bass")
    
    # Use Cache for Bass
    bass_query = "Bass-Electric"
    bass_category = "instruments" # Default fallback
    
    cached_bass = select_from_cache("Bass", CACHE_FILE)
    if cached_bass:
         print(f"   ✨ Selected Bass from Cache: '{cached_bass.get('name')}' (Category: {cached_bass.get('category')})")
         bass_query = cached_bass.get("name")
         if cached_bass.get("category"):
             bass_category = cached_bass.get("category")

    # Try to load a bass preset
    print(f"   💾 Loading Bass Preset: {bass_query} from '{bass_category}'...")
    try:
        load_device_by_name(idx_bass, bass_query, bass_category)
    except Exception as e:
        print(f"   ❌ Bass Load Error: {e}")
        pass 
        
    time.sleep(1.0)
    
    generate_bassline_advanced_wrapper(
        track_index=idx_bass,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="house",
        beats_per_chord=4.0,
        velocity=110,
        octave=1
    )

    # =========================================================================
    # 4. Keys: Stabs
    # =========================================================================
    idx_keys = prepare_track(2, "House Keys")
    
    # Use Cache for Keys
    keys_query = "Electric Piano"
    keys_category = "instruments"
    
    cached_keys = select_from_cache("Piano", CACHE_FILE)
    if cached_keys:
         print(f"   ✨ Selected Keys from Cache: '{cached_keys.get('name')}'")
         keys_query = cached_keys.get("name")
         if cached_keys.get("category"):
             keys_category = cached_keys.get("category")
         
    print(f"   💾 Loading Keys Preset: {keys_query} from '{keys_category}'...")
    try:
        load_device_by_name(idx_keys, keys_query, keys_category)
    except Exception as e:
        print(f"   ❌ Keys Load Error: {e}")
        pass
        
    time.sleep(1.0)
    
    # Use 'house' style strings generator (it likely generates chords)
    generate_strings_advanced_wrapper(
        track_index=idx_keys,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="house", 
        beats_per_chord=4.0,
        velocity=105,
        octave=3
    )

    print("\n✅ House Intro Created! 🏠")

if __name__ == "__main__":
    create_house_intro()
