"""
Create Scene 4 (Outro) & Remove Vocal Chant
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

print("=== CLEANUP & OUTRO ===")

# 1. Remove Vocal Chant Clips (Track 6)
# Scenes 0, 1, 2 exist.
for i in range(4): # 0 to 3
    try:
        conn.send_command("delete_clip", {"track_index": 6, "clip_index": i})
    except: pass
print("✓ Removed Vocal Chant clips.")

# 2. Create Scene 4 (Index 3)
try:
    conn.send_command("create_scene", {"index": 3})
    conn.send_command("set_scene_name", {"scene_index": 3, "name": "Outro"})
except:
    print("Scene 4 might already exist")

# 3. Populate Outro
# Sparse: Texture + Hand Perc
# Texture (Track 9): Copy from Scene 3 (Index 2)
# Hand Perc (Track 1): Copy from Scene 2 (Index 1)

print("Populating Outro...")

# Texture - Generate new Drone
try:
    conn.send_command("create_clip", {"track_index": 9, "clip_index": 3, "length": 8.0})
    conn.send_command("add_notes_to_clip", {
        "track_index": 9, 
        "clip_index": 3, 
        "notes": [{"pitch": 45, "start_time": 0, "duration": 8.0, "velocity": 90}] # A1 Drone
    })
    print("  ✓ Texture generated")
except Exception as e: print(f"  Texture error: {e}")

# Hand Perc
try:
    conn.send_command("duplicate_clip", {
        "track_index": 1, 
        "clip_index": 1, # From Scene 2 (Full pattern)
        "target_clip_index": 3 
    })
    print("  ✓ Hand Perc added")
except Exception as e: print(f"  Hand Perc error: {e}")

print("\n=== FIRING OUTRO ===")
conn.send_command("fire_scene", {"scene_index": 3})
print("Done.")
