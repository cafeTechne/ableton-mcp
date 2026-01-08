"""
Expand Matadora - Scenes 5 & 6 (Fixed)
Varied MIDI performances (Funk, Reggae, Disco styles)
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import (
    generate_bassline_advanced_wrapper,
    generate_rhythmic_comp
)

conn = get_ableton_connection()

print("=== EXPANDING MATADORA (V2) ===")

# Map from Output 3083
TRK_HAND = 1
TRK_KICK = 2
TRK_RIM = 3
TRK_BASS = 5
TRK_STABS = 7
TRK_TEX = 8 

# Scene Indices (after insertion)
SCENE_BRIDGE = 3
SCENE_BUILD = 4

# Create Scenes (if not exist - create_scene inserts)
# We assume we only ran PART of previous script.
# "Creating Bridge" printed. Did it create?
# If it created Bridge(3), then Build(4) might not have run if it crashed.
# Let's verify or just try to create. 
# Better: Set Name explicitly.

print("Configuring Scenes...")
try:
    conn.send_command("create_scene", {"index": 3})
    conn.send_command("set_scene_name", {"scene_index": 3, "name": "Bridge"})
except: pass

try:
    conn.send_command("create_scene", {"index": 4})
    conn.send_command("set_scene_name", {"scene_index": 4, "name": "Build"})
except: pass


# === POPULATE BRIDGE (Scene 3) ===
prog_bridge = "i v i v"

print("Populating Bridge (Bass)...")
print(generate_bassline_advanced_wrapper(
    track_index=TRK_BASS, clip_index=SCENE_BRIDGE,
    key="A", scale="minor", progression=prog_bridge,
    style="funk", velocity=95, humanize=0.2
))

print("Populating Bridge (Stabs)...")
print(generate_rhythmic_comp(
    track_index=TRK_STABS, clip_index=SCENE_BRIDGE,
    key="A", scale="minor", progression=prog_bridge,
    style="reggae_skank", velocity=90, beats_per_chord=2.0
))

print("Populating Bridge (Rim)...")
# Manual Pattern 
conn.send_command("create_clip", {"track_index": TRK_RIM, "clip_index": SCENE_BRIDGE, "length": 4.0})
rim_notes = []
for i in range(4): # 4 bars
    rim_notes.append({"pitch": 60, "start_time": i*4 + 1.5, "duration": 0.1, "velocity": 100})
    rim_notes.append({"pitch": 60, "start_time": i*4 + 3.5, "duration": 0.1, "velocity": 90})
conn.send_command("add_notes_to_clip", {"track_index": TRK_RIM, "clip_index": SCENE_BRIDGE, "notes": rim_notes})


# === POPULATE BUILD (Scene 4) ===
prog_build = "VI VII i i" 

print("Populating Build (Bass)...")
print(generate_bassline_advanced_wrapper(
    track_index=TRK_BASS, clip_index=SCENE_BUILD,
    key="A", scale="minor", progression=prog_build,
    style="disco", velocity=105, humanize=0.1
))

print("Populating Build (Stabs)...")
print(generate_rhythmic_comp(
    track_index=TRK_STABS, clip_index=SCENE_BUILD,
    key="A", scale="minor", progression=prog_build,
    style="disco_octaves", velocity=100
))

print("Populating Build (Hand Perc)...")
conn.send_command("create_clip", {"track_index": TRK_HAND, "clip_index": SCENE_BUILD, "length": 4.0})
hand_notes = []
for i in range(16*4): # 16th notes for 4 bars
    hand_notes.append({"pitch": 60, "start_time": i*0.25, "duration": 0.2, "velocity": 70 + (i%4)*10})
conn.send_command("add_notes_to_clip", {"track_index": TRK_HAND, "clip_index": SCENE_BUILD, "notes": hand_notes})

print("Populating Build (Kick)...")
conn.send_command("create_clip", {"track_index": TRK_KICK, "clip_index": SCENE_BUILD, "length": 4.0})
kick_notes = []
for i in range(16): # 4 on floor * 4 bars
    kick_notes.append({"pitch": 36, "start_time": i, "duration": 0.5, "velocity": 110}) # Quarter notes
conn.send_command("add_notes_to_clip", {"track_index": TRK_KICK, "clip_index": SCENE_BUILD, "notes": kick_notes})


print("\n=== FIRING SCENE 4 (BUILD) === ")
conn.send_command("fire_scene", {"scene_index": SCENE_BUILD}) 
print("Done.")
