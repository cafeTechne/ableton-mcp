"""
Matadora Part 4 - Vocals & Atmosphere
Add Vocal Chant and Atmospheric Drone
Verify load_device_by_name usage
"""
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.util import load_device_by_name
from mcp_tooling.generators import pattern_generator
import time

conn = get_ableton_connection()

print("=== PART 4: VOCALS & ATMOSPHERE ===")

# Create "Vocal Chant" track
result = conn.send_command("create_midi_track", {"index": -1})
vox_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": vox_idx, "name": "Vocal Chant"})
print(f"Created: Vocal Chant (track {vox_idx})")

# Create "Atmosphere" track
result = conn.send_command("create_midi_track", {"index": -1})
atmo_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": atmo_idx, "name": "Atmosphere"})
print(f"Created: Atmosphere (track {atmo_idx})")

# Load Devices using NEW REFACOR logic
print("\n=== LOADING DEVICES (via load_device_by_name) ===")

# 1. Vocal: Load a Simpler (empty first)
print("Loading Simpler for Vocals...")
res = load_device_by_name(vox_idx, "Simpler", "instruments")
if res.get("loaded"):
    print("✓ Loaded Simpler")
else:
    print(f"FAILED to load Simpler: {res}")

# 2. Atmosphere: Load 'Wavetable' or 'Operator'
print("Loading Wavetable for Atmosphere...")
res = load_device_by_name(atmo_idx, "Wavetable", "instruments")
if res.get("loaded"):
    print("✓ Loaded Wavetable")
else:
    print(f"FAILED to load Wavetable: {res}")
    # Fallback
    load_device_by_name(atmo_idx, "Analog", "instruments")

# Add Reverb to Vocals
print("Adding Reverb to Vocals...")
load_device_by_name(vox_idx, "Reverb", "audio_effects")
# Set Decay time long
conn.send_command("set_device_parameter", {"track_index": vox_idx, "device_index": 1, "parameter_name": "Decay Time", "value": 2000})

# Add Echo to Atmosphere
print("Adding Echo to Atmosphere...")
load_device_by_name(atmo_idx, "Echo", "audio_effects")


print("\n=== GENERATING CLIPS ===")

# Vocal Chant: Sparse hits on offbeats (Matadora style "Hey! Hey!")
# Using pattern/notes
from mcp_tooling.theory import NOTE_NAMES
root = 60 # C3
# Matadora key is Am usually?
# Let's just do a rhythmic chant note
# 4 bars

notes = []
# Beat 1.5, 3.5 (syncopated)
for bar in range(0, 8):
    # Hit on beat 2 (time 1.0) and 4 (time 3.0)? 
    # Or "and" of 1: 0.5
    # Let's do 1.5 (2nd beat 'and') = 1.0 is beat 2. 1.5 is beat 2 and.
    # Matadora: "Ma-ta-do-ra" -> rhythmic motif
    # Let's just do a chant every 2 bars
    notes.append({"pitch": root, "start_time": bar * 4.0 + 0.0, "duration": 0.5, "velocity": 110}) # Downbeat?
    notes.append({"pitch": root - 2, "start_time": bar * 4.0 + 1.5, "duration": 0.5, "velocity": 90})

conn.send_command("create_clip", {"track_index": vox_idx, "clip_index": 1, "length": 8.0}) # Scene 1
conn.send_command("add_notes_to_clip", {"track_index": vox_idx, "clip_index": 1, "notes": notes})
print("Generated Vocal Chant Pattern")

# Atmosphere: Long sustained note (Drone)
drone_notes = [{"pitch": 45, "start_time": 0.0, "duration": 32.0, "velocity": 60}] # A0/A1
conn.send_command("create_clip", {"track_index": atmo_idx, "clip_index": 1, "length": 8.0}) 
conn.send_command("add_notes_to_clip", {"track_index": atmo_idx, "clip_index": 1, "notes": drone_notes})
print("Generated Atmosphere Drone")


print("\n=== UPDATING SCENE 1 ===")
conn.send_command("fire_scene", {"scene_index": 1})

print("\n✓ PART 4 COMPLETE: Matadora Build Finished!")
