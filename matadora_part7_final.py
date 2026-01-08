"""
Matadora Part 7 - Final Instrument Fix
Fix Hand Perc and Rim Perc
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.util import load_device_by_name

conn = get_ableton_connection()

# Map is roughly known but let's just use names
track_map = {}
for i in range(15):
    try:
        info = conn.send_command("get_track_info", {"track_index": i})
        name = info.get("name")
        if name: track_map[name] = i
    except: pass

print("Current Map:", track_map)

# Fix Hand Perc
if "Hand Perc" in track_map:
    idx = track_map["Hand Perc"]
    print(f"Fixing Hand Perc (Track {idx})...")
    # Try loading "Impulse" (Built-in instrument)
    res = load_device_by_name(idx, "Impulse", "instruments")
    if res.get("loaded"):
        print("✓ Loaded Impulse")
    else:
        # Try generic "Drum Rack"
        load_device_by_name(idx, "Drum Rack", "instruments")

# Fix Rim Perc
if "Rim Perc" in track_map:
    idx = track_map["Rim Perc"]
    print(f"Fixing Rim Perc (Track {idx})...")
    # Try loading "Impulse" too? Or "Simpler"
    res = load_device_by_name(idx, "Simpler", "instruments")
    if res.get("loaded"):
        print("✓ Loaded Simpler")

print("\n=== FIRING SCENE 3 ===")
conn.send_command("fire_scene", {"scene_index": 2})
print("Done.")
