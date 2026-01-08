"""
Fix Vocal Chant (Advanced)
Use generate_rhythmic_comp with valid chords to create diatonic chant
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import generate_rhythmic_comp

conn = get_ableton_connection()

print("=== FIXING VOCAL CHANT (HARMONIC) ===")

# Track 6 is Vocal Chant (from Output 2991/3000)
track_idx = 6

# Progression: i VI VII (Classic minor/modal vibe)
# Key: A Minor
# Style: reggae_skank (Offbeat stabs)

for scene, name in [(1, "Drop"), (2, "Breakdown")]:
    print(f"Generating for Scene {scene} ({name})...")
    
    # Clear old
    try:
        conn.send_command("delete_clip", {"track_index": track_idx, "clip_index": scene})
    except: pass

    # Generate
    res = generate_rhythmic_comp(
        track_index=track_idx,
        clip_index=scene,
        key="A",
        scale="minor",
        progression="i VI VII i", # String format
        style="reggae_skank",
        velocity=100,
        octave=4, # C4 range
        humanize=0.2,
        beats_per_chord=2.0 # Faster changes? 2 beats per chord = 2 chords per bar.
        # Total 4 chords * 2 beats = 8 beats (2 bars). 
        # Repeating to fill 8 bars?
    )
    print(f"  {res}")

print("\n=== FIRING SCENE 3 ===")
conn.send_command("fire_scene", {"scene_index": 2})
print("Done.")
