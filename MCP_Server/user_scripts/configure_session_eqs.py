"""
Configure EQ Eight with Correct Normalized Values

This is the CORRECT way to configure EQ Eight.
All frequency and gain values use NORMALIZED 0.0-1.0 values.

Reference:
- Frequency: norm = log(hz / 10) / log(2200)
- Gain: norm = (db + 15) / 30
"""

import sys
import os
import math

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

# Conversion functions
def hz_to_norm(freq_hz):
    """Convert Hz to normalized 0.0-1.0 for EQ Eight."""
    if freq_hz <= 10: return 0.0
    if freq_hz >= 22000: return 1.0
    return math.log(freq_hz / 10) / math.log(2200)

def db_to_norm(db):
    """Convert dB to normalized 0.0-1.0 for EQ Eight."""
    if db <= -15: return 0.0
    if db >= 15: return 1.0
    return (db + 15) / 30

def configure_eq_for_track(conn, track_idx, preset):
    """Apply EQ preset to track."""
    for band_idx, settings in preset.items():
        params = {
            "track_index": track_idx,
            "band_index": band_idx,
            "enabled": True
        }
        
        if "freq_hz" in settings:
            params["freq"] = hz_to_norm(settings["freq_hz"])
        if "gain_db" in settings:
            params["gain"] = db_to_norm(settings["gain_db"])
        if "q" in settings:
            params["q"] = settings["q"]  # Q is already normalized
        if "filter_type" in settings:
            params["filter_type"] = settings["filter_type"]
            
        conn.send_command("set_eq8_band", params)

def configure_session_eqs():
    """Configure EQ for common instrument types."""
    print("🎛️ Configuring EQ Bands (Normalized Values)...")
    conn = get_ableton_connection()
    
    # Get all tracks
    context = conn.send_command("get_song_context", {"include_clips": False})
    tracks = context.get("tracks", [])
    
    # Presets (using Hz and dB, converted to normalized)
    PRESETS = {
        "kick": {
            1: {"freq_hz": 40, "filter_type": 0},  # HP 40Hz
            2: {"freq_hz": 60, "gain_db": 4, "q": 0.5, "filter_type": 3},  # Boost low
            3: {"freq_hz": 300, "gain_db": -5, "q": 0.6, "filter_type": 3}  # Cut mud
        },
        "snare": {
            1: {"freq_hz": 100, "filter_type": 1},  # HP 100Hz steep
            3: {"freq_hz": 200, "gain_db": 3, "q": 0.5, "filter_type": 3}  # Body
        },
        "bass": {
            1: {"freq_hz": 30, "filter_type": 0},  # HP 30Hz
            2: {"freq_hz": 80, "gain_db": 3, "q": 0.5, "filter_type": 3}  # Boost
        },
        "vocal": {
            1: {"freq_hz": 180, "filter_type": 1},  # HP 180Hz
            3: {"freq_hz": 3000, "gain_db": 2, "q": 0.5, "filter_type": 3},  # Presence
            8: {"freq_hz": 10000, "gain_db": 2, "filter_type": 4}  # Air shelf
        },
        "default": {
            1: {"freq_hz": 120, "filter_type": 0},  # HP 120Hz
            8: {"freq_hz": 10000, "gain_db": 1.5, "filter_type": 4}  # Air
        }
    }
    
    for track in tracks:
        idx = track.get("index")
        name = track.get("name", "").lower()
        
        # Skip master/return tracks
        if track.get("is_return_track") or track.get("is_master"):
            continue
            
        # Check if track has EQ Eight
        t_info = conn.send_command("get_track_info", {"track_index": idx})
        has_eq = any("eq" in d.get("class_name", "").lower() for d in t_info.get("devices", []))
        
        if not has_eq:
            print(f"   ⚠️ Track {idx} ({name}): No EQ found, skipping")
            continue
        
        # Select preset based on track name
        preset_key = "default"
        if "kick" in name or "drum" in name:
            preset_key = "kick"
        elif "snare" in name:
            preset_key = "snare"
        elif "bass" in name:
            preset_key = "bass"
        elif "vocal" in name or "vox" in name:
            preset_key = "vocal"
            
        print(f"   🎚️ Track {idx} ({name}): Applying '{preset_key}' preset")
        configure_eq_for_track(conn, idx, PRESETS[preset_key])
    
    print("\n✅ EQ Configuration Complete!")

if __name__ == "__main__":
    configure_session_eqs()
