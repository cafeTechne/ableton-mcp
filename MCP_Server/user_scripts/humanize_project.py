import sys
import json
import random
import time
from typing import List, Dict, Any

# Add MCP_Server to path
import os

# Add parent directory to path to import mcp_tooling
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.humanization import HumanizeProfile, apply_humanization

"""
MIDI Humanization Script for AbletonMCP.
----------------------------------------
Applies randomization to Timing, Velocity, Probability, and Velocity Deviation
for all MIDI clips in the current project.

Note: Audio Humanization is intentionally NOT supported.
"""

def humanize_midi_clip(conn, track_idx: int, clip_idx: int, clip_name: str):
    """Humanize a MIDI clip using both micro-timing/velocity and Live 11 attributes."""
    print(f"  - Humanizing MIDI Clip: {clip_name}")
    
    # 1. Get notes with extended attributes (probability, velocity_deviation)
    res = conn.send_command("get_notes_extended", {
        "track_index": track_idx,
        "clip_index": clip_idx,
        "start_time": 0,
        "time_span": 1000000 # Large enough for any clip
    })
    
    notes = res.get("notes", [])
    if not notes:
        return
    
    # 2. Apply core humanization (Timing Jitter and Velocity Variation)
    # We'll use a "human" preset
    profile = HumanizeProfile.get_preset("human")
    apply_humanization(notes, profile)
    
    # 3. Add Live 11 Extended Features (Probability and Velocity Deviation)
    for note in notes:
        # Subtle velocity deviation (random range for velocity)
        # 0 to 127. Recommended 10-30% deviation for noticeable effect.
        note["velocity_deviation"] = random.randint(10, 30)
        
        # Human probability (95-100% chance to play)
        # Subtle skipping for ghost note feel
        note["probability"] = random.uniform(0.95, 1.0)
    
    # 4. Update notes in Ableton
    conn.send_command("update_notes", {
        "track_index": track_idx,
        "clip_index": clip_idx,
        "notes": notes
    })

def main():
    try:
        conn = get_ableton_connection()
        print("Fetching song context...")
        context = conn.send_command("get_song_context", {"include_clips": True})
        
        tracks = context.get("tracks", [])
        print(f"Found {len(tracks)} tracks.")
        
        for track in tracks:
            track_idx = track.get("index")
            track_name = track.get("name")
            track_type = track.get("type")
            clips = track.get("clips", [])
            
            if not clips:
                continue
                
            print(f"Track {track_idx} [{track_name}]: {len(clips)} clips")
            
            for clip in clips:
                clip_idx = clip.get("slot")
                clip_name = clip.get("name") or f"Clip {clip_idx}"
                
                if track_type == "midi":
                    humanize_midi_clip(conn, track_idx, clip_idx, clip_name)
                    
        print("\nProject humanization complete!")
        print("Check Ableton Live to see the changes.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
