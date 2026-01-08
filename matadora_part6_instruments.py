"""
Matadora Part 6 - Instruments & Scene 3 (Robust)
1. Find tracks dynamically
2. Load Instruments (Try/Except)
3. Create Scene 3
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.util import load_device_by_name

conn = get_ableton_connection()

print("=== PART 6 ROBUST ===")

# 1. Map Tracks Dynamically
track_map = {}
print("Mapping tracks...")
for i in range(20):
    try:
        info = conn.send_command("get_track_info", {"track_index": i})
        name = info.get("name")
        if name:
            track_map[name] = i
    except:
        pass

print("Track Map:", track_map)

# Targets
targets = {
    "Kick": ["Kick 909", "Kick-808", "Kick"],
    "Hand Perc": ["Bongo Kit", "Conga Kit", "Latin Percussion"],
    "Rim Perc": ["Rim Shot", "Kit-Core 909", "Drum Rack"],
    "Texture": ["Pad-Analog", "Analog", "Operator"],
    "Vocal Chant": ["Choir Aahs", "Choir", "Simpler"]
}

# 2. Load Instruments
print("\n=== LOADING INSTRUMENTS ===")
for t_name, presets in targets.items():
    if t_name in track_map:
        idx = track_map[t_name]
        print(f"Loading {t_name} (Track {idx})...")
        loaded = False
        for p in presets:
            try:
                print(f"  Trying '{p}'...")
                res = load_device_by_name(idx, p, "instruments")
                if res.get("loaded"):
                    print(f"  ✓ Loaded {p}")
                    loaded = True
                    break
            except Exception as e:
                print(f"  Error loading {p}: {e}")
        
        if not loaded:
            print(f"  FAILED to load any preset for {t_name}")
    else:
        print(f"Warning: Track '{t_name}' not found in map.")

# 3. Create Scene 3
print("\n=== CREATING SCENE 3 (VARIATION) ===")
scene_idx = 2
try:
    conn.send_command("create_scene", {"index": scene_idx})
    conn.send_command("set_scene_name", {"scene_index": scene_idx, "name": "Variation"})
except:
    pass

# Copy Clips
print("Copying clips from Scene 1 to Scene 3...")
for t_name, idx in track_map.items():
    # Only copy specific tracks? No, copy all relevant
    if t_name in targets or t_name in ["Bass", "Stabs", "Atmosphere"]:
        try:
             conn.send_command("duplicate_clip", {
                "track_index": idx,
                "clip_index": 1, 
                "destination_index": 2
            })
        except:
            pass

# Mod: Remove Kick
if "Kick" in track_map:
    kick_idx = track_map["Kick"]
    print("Removing Kick from Scene 3...")
    try:
        conn.send_command("delete_clip", {"track_index": kick_idx, "clip_index": 2})
    except:
        pass

print("\n=== FIRING SCENE 3 ===")
conn.send_command("fire_scene", {"scene_index": 2})
print("Done.")
