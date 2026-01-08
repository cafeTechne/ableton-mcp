"""
Fix Scene 3 (Variation/Breakdown)
Verify empty slots and force populate from Scene 2 (Drop)
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

print("=== FIXING SCENE 3 ===")

# 1. Map Tracks
track_map = {}
for i in range(20):
    try:
        info = conn.send_command("get_track_info", {"track_index": i})
        name = info.get("name")
        if name: track_map[name] = i
    except: pass
print("Track Map:", track_map)

# 2. Target Scene Index
src_scene = 1 # Scene 2 (Drop)
dest_scene = 2 # Scene 3 (Variation)

# Ensure Scene exists
try:
    conn.send_command("create_scene", {"index": dest_scene})
    conn.send_command("set_scene_name", {"scene_index": dest_scene, "name": "Deep Breakdown"})
except:
    pass # Likely exists

# 3. Duplicate Clips (Blind)
for name, idx in track_map.items():
    if "Return" in name or "Master" in name: continue
    
    print(f"Track '{name}' ({idx}): Duplicating Src->Dest...")
    try:
        conn.send_command("duplicate_clip", {
            "track_index": idx,
            "clip_index": src_scene,
            "destination_index": dest_scene
        })
        print("  ✓ Success")
    except Exception as e:
        print(f"  Note: {e}")
        
    if name == "Kick":
        # Delete Kick for Breakdown
        print("  Removing Kick from Breakdown...")
        try:
             conn.send_command("delete_clip", {"track_index": idx, "clip_index": dest_scene})
        except: pass

print("\n=== FIRING SCENE 3 ===")
conn.send_command("fire_scene", {"scene_index": dest_scene})
print("Done.")
