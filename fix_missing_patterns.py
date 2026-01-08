"""
Fix Missing Patterns (Vocal & Texture)
Target correct indices for Scene 3
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import pattern_generator

conn = get_ableton_connection()

print("=== POPULATING VOCAL & TEXTURE (SCENE 3) ===")

# Indices from Output 2991
vocal_idx = 6
tex_idx = 9 # Track 4 is Audio, 9 is 10-Analog (MIDI)
scene_idx = 2

# 1. Vocal Chant (Track 6)
print(f"Generating Vocal Chant on Track {vocal_idx}...")
# Custom rhythmic chant
# "Hey!" on offbeat (1.5, 3.5)
notes = []
root = 60
for bar in range(0, 8):
    notes.append({"pitch": root, "start_time": bar * 4.0 + 1.5, "duration": 0.25, "velocity": 105})
    notes.append({"pitch": root-2, "start_time": bar * 4.0 + 3.5, "duration": 0.25, "velocity": 95})

try:
    conn.send_command("create_clip", {"track_index": vocal_idx, "clip_index": scene_idx, "length": 32.0})
    conn.send_command("add_notes_to_clip", {"track_index": vocal_idx, "clip_index": scene_idx, "notes": notes})
    print("  ✓ Vocal pattern created")
except Exception as e:
    print(f"  Error Vocal: {e}")

# 2. Texture (Track 4)
print(f"Generating Texture Drone on Track {tex_idx}...")
# Long sustained note
drone = [{"pitch": 60, "start_time": 0.0, "duration": 32.0, "velocity": 70}]
try:
    conn.send_command("create_clip", {"track_index": tex_idx, "clip_index": scene_idx, "length": 32.0})
    conn.send_command("add_notes_to_clip", {"track_index": tex_idx, "clip_index": scene_idx, "notes": drone})
    print("  ✓ Texture pattern created")
except Exception as e:
    print(f"  Error Texture: {e}")

print("\n=== FIRING SCENE 3 ===")
conn.send_command("fire_scene", {"scene_index": scene_idx})
print("Done.")
