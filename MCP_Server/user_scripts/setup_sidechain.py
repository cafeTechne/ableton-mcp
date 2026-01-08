"""
Setup Sidechain Pumping

This script demonstrates sidechain compression setup.
NOTE: Full sidechain routing requires manual configuration in Ableton
as the API doesn't support sidechain source routing yet.

This script:
1. Finds tracks by name
2. Loads Compressor on target tracks
3. Sets pumping parameters
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.devices import search_and_load_device

def find_track_by_name(conn, name):
    """Find track index by name using get_song_context."""
    context = conn.send_command("get_song_context", {"include_clips": False})
    for track in context.get("tracks", []):
        if track.get("name") == name:
            return track.get("index")
    return -1

def setup_sidechain_pumping():
    print("🌊 Setting up Sidechain Pumping...")
    conn = get_ableton_connection()
    
    # 1. Find Sidechain Trigger track
    SOURCE_NAME = "Sidechain Trigger"
    SOURCE_TRACK_IDX = find_track_by_name(conn, SOURCE_NAME)
    if SOURCE_TRACK_IDX == -1:
        print(f"   ❌ Could not find track: {SOURCE_NAME}")
        print("   💡 Create a track named 'Sidechain Trigger' with a kick pattern")
        return
    print(f"   📣 Sidechain Source: {SOURCE_NAME} (Index {SOURCE_TRACK_IDX})")
    
    # 2. Target tracks
    TARGET_NAMES = [
        "Sub Bass", "Mid Bass", "Chord Stabs", 
        "Pad / Atmos", "Lead / Topline", "Arp / Pluck"
    ]
    
    for name in TARGET_NAMES:
        track_idx = find_track_by_name(conn, name)
        if track_idx == -1:
            print(f"   ⚠️ Skipping {name}: Track not found")
            continue
            
        print(f"   ⚓ Processing {name} (Index {track_idx})...")
        
        # Load Compressor using correct API
        result = search_and_load_device(track_idx, "Compressor", "audio_effects")
        print(f"      📦 {result}")
        time.sleep(1.0)
        
        # Get devices to find the Compressor
        t_info = conn.send_command("get_track_info", {"track_index": track_idx})
        devices = t_info.get("devices", [])
        comp_idx = -1
        for dev in devices:
            if "compressor" in dev.get("name", "").lower():
                comp_idx = dev.get("index")
                break
        
        if comp_idx == -1:
            print(f"      ❌ Compressor not found on {name}")
            continue

        # Set Pumping Parameters (normalized values)
        params = {
            "Threshold": 0.4,  # Normalized
            "Ratio": 0.8,      # Normalized  
            "Attack": 0.0,     # Fast attack
            "Release": 0.15   # Quick release for pumping
        }
        
        for p_name, p_val in params.items():
            try:
                conn.send_command("set_device_parameter", {
                    "track_index": track_idx,
                    "device_index": comp_idx,
                    "parameter_name": p_name,  # FIXED: was "parameter"
                    "value": p_val
                })
            except Exception as e:
                print(f"      ⚠️ Failed to set {p_name}: {e}")
        
        print(f"      ✅ Compressor configured")
        print(f"      ⚠️ Manual step: Set sidechain input to '{SOURCE_NAME}' in Ableton")
            
    print("\n✅ Sidechain setup complete!")
    print("💡 Remember to manually set sidechain routing in each Compressor")

if __name__ == "__main__":
    setup_sidechain_pumping()
