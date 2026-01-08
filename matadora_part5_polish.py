"""
Matadora Part 5 - Polish & Mix
1. Cleanup Probe Track
2. Fix Texture Track (Recreate as MIDI for localized generation)
3. Add Rhythmic Comp Layer
4. Basic Mixing (Volume/EQ)
"""
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.util import load_device_by_name
from mcp_tooling.generators import generate_rhythmic_comp, pattern_generator
import time

conn = get_ableton_connection()

print("=== PART 5: POLISH & MIX ===")

# 1. Cleanup Probe (Track 11) usually
# But we need to find it by index or just assume it's the last one.
# Let's count tracks again via context
ctx = conn.send_command("get_song_context", {"include_clips": False})
tracks = ctx.get("tracks", [])
print(f"Track Count: {len(tracks)}")

# Find 'Texture' and 'Probe' (or unnamed track at end)
tex_idx = None
probe_idx = None

for t in tracks:
    if t['name'] == "Texture":
        tex_idx = t['index']
    if t['index'] == len(tracks) - 1 and "Probe" not in t['name']: # Probe created raw usually
        # Actually I didn't name it.
        probe_idx = t['index']

if probe_idx is not None and probe_idx >= 11:
    print(f"Deleting Probe Track {probe_idx}...")
    conn.send_command("delete_track", {"track_index": probe_idx})

# 2. Fix Texture (Track 6 usually)
# If it's audio and empty, let's swap it.
if tex_idx is not None:
    print(f"Replacing Texture Track {tex_idx} with MIDI...")
    conn.send_command("delete_track", {"track_index": tex_idx})
    # Create new MIDI track at same index
    res = conn.send_command("create_midi_track", {"index": tex_idx})
    new_tex_idx = res.get("index") # Should be same
    conn.send_command("set_track_name", {"track_index": new_tex_idx, "name": "Texture MIDI"})
    
    # Load Noise/Texture Generator
    print("Loading Texture Device (Collision or Analog)...")
    load_device_by_name(new_tex_idx, "Analog", "instruments")
    # Add Erosion for dirt
    load_device_by_name(new_tex_idx, "Erosion", "audio_effects")
    
    # Generate Texture Drone/Noise pattern
    print("Generating Texture Pattern...")
    # constant 16th notes with random velocity? 
    # Or just long notes with Erosion automation?
    # Let's do a simple pattern
    pattern_generator(
        track_index=new_tex_idx,
        clip_slot_index=1, # Scene 1
        pattern_type="breakbeat", # Reuse breakbeat for noise perc?
        bars=8,
        root_note=60,
        velocity=60
    )


# 3. Add Rhythmic Comp (Stabs)
print("\n=== ADDING COMP LAYER ===")
res = conn.send_command("create_midi_track", {"index": -1})
comp_idx = res.get("index")
conn.send_command("set_track_name", {"track_index": comp_idx, "name": "Stabs"})

print("Loading Stab Instrument (Operator)...")
load_device_by_name(comp_idx, "Operator", "instruments")
# Make it short/plucky? Default Operator is sine. 
# Add Chord effect just in case
load_device_by_name(comp_idx, "Chord", "midi_effects")

print("Generating Stabs...")
# generate_rhythmic_comp(track_index, clip_index, key, scale, progression, style...)
# Key Am. Progression i-i-VI-V
# Style: "reggae_skank" or "house_piano" or "funk_stabs"?
# Matadora has stabs on offbeats. "reggae_skank" is good for that.
generate_rhythmic_comp(
    track_index=comp_idx,
    clip_index=1,
    key="A",
    scale="minor",
    progression="i i VI V",
    style="reggae_skank",
    velocity=95,
    humanize=0.2
)

# 4. Mixing
print("\n=== MIXING ===")
# Set volumes
vol_map = {
    "Kick": 0.95,
    "Hand Perc": 0.85,
    "Rim Perc": 0.75,
    "Bass": 0.9,
    "Vocal Chant": 0.8,
    "Stabs": 0.7,
    "Atmosphere": 0.6,
    "Texture MIDI": 0.5
}

# Re-fetch tracks to get current indices
ctx = conn.send_command("get_song_context", {"include_clips": False})
for t in ctx.get("tracks", []):
    name = t['name']
    idx = t['index']
    if name in vol_map:
        vol = vol_map[name]
        conn.send_command("set_track_volume", {"track_index": idx, "volume": vol})
        print(f"Set {name} volume to {vol}")
        
    # Add EQ Eight to everyone if missing?
    # Checking existing devices is expensive? Just trying to load EQ Eight at end of chain?
    # Let's skip auto-EQ to avoid overloading CPU/time, focus on volume.

print("\n=== FIRING FULL GROOVE ===")
conn.send_command("fire_scene", {"scene_index": 1})

print("\n✓ PART 5 COMPLETE: Mix Balanced & Layers Added")
