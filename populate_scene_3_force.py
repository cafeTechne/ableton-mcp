"""
Populate Scene 3 Force
Delete existing clips in Scene 3, then duplicate from Scene 2
Targets: Hand Perc, Rim Perc, Bass, Stabs
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

print("=== POPULATE SCENE 3 FORCE ===")

# Map from Output 2991
# Hand Perc: 1
# Rim Perc: 3
# Bass: 5
# Stabs: 8
tracks = {
    "Hand Perc": 1,
    "Rim Perc": 3,
    "Bass": 5,
    "Stabs": 8
}

src_clip = 1 # Scene 2
dest_clip = 2 # Scene 3

for name, idx in tracks.items():
    print(f"Fixing {name} (Track {idx})...")
    
    # 1. Delete Target
    try:
        conn.send_command("delete_clip", {"track_index": idx, "clip_index": dest_clip})
        print("  Deleted existing clip.")
    except Exception as e:
        print(f"  Delete failed/no clip: {e}")
        
    # 2. Duplicate Source
    try:
        conn.send_command("duplicate_clip", {
            "track_index": idx,
            "clip_index": src_clip,
            "target_clip_index": dest_clip
        })
        print("  ✓ Duplicated Scene 2 -> Scene 3")
    except Exception as e:
        print(f"  Duplicate failed: {e}")
        # If duplicate fails (maybe source empty?), Regenerate?
        # User said "midi in scene 2 is good", so source should exist.
        pass

print("\n=== FIRING SCENE 3 ===")
conn.send_command("fire_scene", {"scene_index": dest_clip})
print("Done.")
