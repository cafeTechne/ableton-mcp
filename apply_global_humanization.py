"""
Apply Global Humanization
Iterate all tracks/scenes and apply appropriate humanization profiles.
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.humanization import apply_humanization, HumanizeProfile

conn = get_ableton_connection()

# Track Map
TRK_DRUMS = 0
TRK_HAND = 1
TRK_KICK = 2
TRK_RIM = 3
TRK_BASS = 5
TRK_STABS = 7

# Profiles
prof_tight = HumanizeProfile.get_preset("tight")
prof_human = HumanizeProfile.get_preset("human")
prof_loose = HumanizeProfile.get_preset("loose")
prof_swing = HumanizeProfile.get_preset("swing")

# Configuration
# Track Index -> (Profile, Amount)
config = {
    TRK_DRUMS: (prof_human, 1.0), # Already done? Doing again adds more jitter. skipping.
    TRK_HAND:  (prof_loose, 0.8), # Latin feel
    TRK_KICK:  (prof_tight, 0.5), # Keep kick tight but slight velocity var
    TRK_RIM:   (prof_human, 0.8),
    TRK_BASS:  (prof_tight, 0.8), # Bass needs to lock
    TRK_STABS: (prof_swing, 0.6), # Stabs slightly swung
}

print("=== GLOBAL HUMANIZATION ===")

for scene_idx in range(6): # 0 to 5
    print(f"\nProcessing Scene {scene_idx}...")
    
    for trk_idx, (prof, amt) in config.items():
        if trk_idx == TRK_DRUMS: continue # Skip drums, already generated with humanization
        
        try:
            # 1. Get Notes
            # Use basic get_notes or extended?
            # 'get_notes_extended' might not be in interface?
            # 'get_clip_notes' is standard.
            # Helper: check interface.py? 
            # Output 3022 viewed clip.py... 
            # I will try "get_notes" (standard). 
            # Wait, interface.py maps "get_notes" to `clip_handler.get_notes`.
            
            resp = conn.send_command("get_notes", {
                "track_index": trk_idx,
                "clip_index": scene_idx
            })
            
            if resp.get("status") == "error":
                continue # No clip
                
            notes = resp.get("notes", [])
            if not notes: continue
            
            # Convert List to Dict
            # [pitch, start, duration, velocity, mute]
            note_dicts = []
            for n in notes:
                if isinstance(n, list):
                    note_dicts.append({
                        "pitch": n[0],
                        "start_time": n[1],
                        "duration": n[2],
                        "velocity": n[3]
                    })
                elif isinstance(n, dict):
                    note_dicts.append(n)

            # 2. Apply Humanization
            apply_humanization(note_dicts, prof, amount=amt)
            
            # 3. Update Notes (Delete & Recreate Clip to be safe)
            # Get clip length first? Default 4.0?
            length = 4.0
            # Try to get length from `get_clip_info` if possible, or assume 4.0 based on generation.
            # Most generated clips are 4 bars (16 beats) or 8 bars.
            # Safe bet: 4.0 (beats? No, 1 bar=4 beats. 4 bars = 16.0).
            # Wait, 4 bars = 16.0 beats.
            # Generated patterns were `bars=4`.
            # So length is 16.0.
            
            # Delete Old
            conn.send_command("delete_clip", {"track_index": trk_idx, "clip_index": scene_idx})
            
            # Create New
            conn.send_command("create_clip", {
                "track_index": trk_idx, 
                "clip_index": scene_idx, 
                "length": 16.0 # Assuming 4 bars
            })
            
            # Add Notes
            conn.send_command("add_notes_to_clip", {
                 "track_index": trk_idx,
                 "clip_index": scene_idx,
                 "notes": note_dicts
            })
            print(f"  Track {trk_idx}: Humanized {len(note_dicts)} notes")
            
        except Exception as e:
            print(f"  Track {trk_idx} Error: {e}")

print("\nDone.")
