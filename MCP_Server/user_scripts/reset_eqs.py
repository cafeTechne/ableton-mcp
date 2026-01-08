"""
Reset all EQ Eight bands to restore audio.

Use this script if EQ settings have caused audio issues.
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

def reset_eqs():
    print("🔁 Resetting EQ Bands to restore audio...")
    conn = get_ableton_connection()
    
    # Get actual tracks from session
    context = conn.send_command("get_song_context", {"include_clips": False})
    tracks = context.get("tracks", [])
    
    for track in tracks:
        idx = track.get("index")
        name = track.get("name", f"Track {idx}")
        
        # Skip master/return
        if track.get("is_return_track") or track.get("is_master"):
            continue
            
        print(f"   Resetting Track {idx} ({name})...")
        
        for band in range(1, 9):
            try:
                conn.send_command("set_eq8_band", {
                    "track_index": idx,
                    "band_index": band,
                    "enabled": False,
                    "gain": 0.5  # Reset gain to 0dB (normalized)
                })
            except:
                pass
                
    print("\n✅ EQs Reset! Audio should be audible.")

if __name__ == "__main__":
    reset_eqs()
