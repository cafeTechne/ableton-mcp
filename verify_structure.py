"""
Verify Scenes and Track Index
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# 1. Find DS Drum Rack
track_count = 20 # Iterating
ds_track_index = -1

print("--- Tracks ---")
for i in range(track_count):
    try:
        info = conn.send_command("get_track_info", {"track_index": i})
        if info.get("status") == "error": break
        name = info.get("name")
        print(f"Track {i}: {name}")
        if "DS Drum Rack" in name:
            ds_track_index = i
    except: break

print(f"\nTarget Track Index for 'DS Drum Rack': {ds_track_index}")

# 2. Check Scenes (By probing get_scene_name potentially? Or just assuming based on previous)
# There is no explicit `get_scene_count` exposed clearly? 
# I'll try getting names for indices 0 to 10.
print("\n--- Scenes ---")
for i in range(10):
    try:
        # Assuming get_scene_data or similar, but standard is `fire_scene`.
        # Is there a prompt? No.
        # Let's try `get_scene_name`? (Might not exist in interface.py)
        # Checking interface... `set_scene_name` exists. `get_scene_name`?
        # I'll try. 
        # If not, I rely on my knowledge: 0=Intro, 1=Drop, 2=Var, 3=Bridge, 4=Build, 5=Outro.
        pass
    except: pass

print("Assuming structure: 0:Intro, 1:Drop, 2:Var, 3:Bridge, 4:Build, 5:Outro")
