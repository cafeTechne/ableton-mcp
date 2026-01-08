"""
Fix Scene 1 Clips
Populate missing clips for Drop/Section B
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import generate_bassline_advanced_wrapper, pattern_generator
from mcp_tooling.util import load_device_by_name

conn = get_ableton_connection()

print("=== FIXING SCENE 1 (DROP) ===")

# Valid indices from Map
tracks = {
    "Hand Perc": 1,
    "Kick": 2,
    "Rim Perc": 5,
    "Bass": 7,
    "Vocal": 9,
    "Atmo": 10
}

# 1. Percussion: Duplicate from Scene 0 if possible, else regenerate
dest_clip = 1
src_clip = 0

for name, idx in [("Hand Perc", 1), ("Kick", 2), ("Rim Perc", 5)]:
    print(f"fixing {name} (Track {idx})...")
    # Clear slot first
    try:
        conn.send_command("delete_clip", {"track_index": idx, "clip_index": dest_clip})
    except:
        pass

    # Try duplicate
    try:
        conn.send_command("duplicate_clip", {
            "track_index": idx,
            "clip_index": src_clip,
            "destination_index": dest_clip
        })
        print(f"  Duplicated Clip 0 -> 1")
    except Exception as e:
        print(f"  Duplicate failed ({e}), regenerating...")
        # Fallback generation
        ptype = "breakbeat" if name == "Hand Perc" else ("hiphop" if name == "Kick" else "trap")
        pattern_generator(
            track_index=idx,
            clip_slot_index=dest_clip,
            pattern_type=ptype,
            bars=8,
            root_note=36 if name != "Rim Perc" else 37,
            velocity=100
        )

# 2. Bass: Regenerate for Scene 1
print("Fixing Bass (Track 7)...")
try:
    conn.send_command("delete_clip", {"track_index": 7, "clip_index": dest_clip})
except:
    pass

# generate_bassline_advanced(track_index, clip_index...)
# Wait, need to use the wrapper from generators (logic) since I am script
from mcp_tooling.generators import generate_bassline_advanced_wrapper
generate_bassline_advanced_wrapper(
    track_index=7,
    clip_index=dest_clip,
    key="A",
    scale="minor",
    progression="i i VI V",
    style="syncopated"
)

# 3. Vocal: Regenerate
print("Fixing Vocal (Track 9)...")
try:
    conn.send_command("delete_clip", {"track_index": 9, "clip_index": dest_clip})
except:
    pass
# Custom pattern logic from Part 4
notes = []
root = 60
for bar in range(0, 8):
    notes.append({"pitch": root, "start_time": bar * 4.0 + 0.0, "duration": 0.5, "velocity": 110})
    notes.append({"pitch": root - 2, "start_time": bar * 4.0 + 1.5, "duration": 0.5, "velocity": 90})

conn.send_command("create_clip", {"track_index": 9, "clip_index": dest_clip, "length": 32.0}) # 8 bars * 4 = 32 beats
conn.send_command("add_notes_to_clip", {"track_index": 9, "clip_index": dest_clip, "notes": notes})

# 4. Atmosphere: Regenerate
print("Fixing Atmosphere (Track 10)...")
try:
    conn.send_command("delete_clip", {"track_index": 10, "clip_index": dest_clip})
except:
    pass
drone = [{"pitch": 45, "start_time": 0.0, "duration": 32.0, "velocity": 60}]
conn.send_command("create_clip", {"track_index": 10, "clip_index": dest_clip, "length": 32.0})
conn.send_command("add_notes_to_clip", {"track_index": 10, "clip_index": dest_clip, "notes": drone})

print("\n=== FIRING SCENE 1 ===")
conn.send_command("fire_scene", {"scene_index": dest_clip})
    
print("\n✓ Scene 1 Populated!")
