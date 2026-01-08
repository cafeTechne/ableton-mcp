"""
Matadora Rebuild - Using Actual Pattern Generator
Stop hand-coding terrible MIDI, use the tools we have
"""
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import pattern_generator
from mcp_tooling.devices import search_and_load_device
import time

conn = get_ableton_connection()

print("=== CLEARING SESSION ===")
session_info = conn.send_command("get_session_info", {})
track_count = session_info.get("track_count", 0)

for i in range(track_count - 1, -1, -1):
    try:
        conn.send_command("delete_track", {"track_index": i})
    except:
        pass

conn.send_command("set_tempo", {"tempo": 122})
print("Session cleared, tempo set to 122 BPM\n")

print("=== CREATING PERCUSSION TRACKS ===")

# Track 0: Main percussion with breakbeat pattern (sparse, organic feel)
result = conn.send_command("create_midi_track", {"index": -1})
perc_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": perc_idx, "name": "Hand Perc"})
print(f"Created: Hand Perc (track {perc_idx})")

# Track 1: Kick/stomp layer
result = conn.send_command("create_midi_track", {"index": -1})
kick_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": kick_idx, "name": "Kick"})
print(f"Created: Kick (track {kick_idx})")

print("\n=== LOADING DRUM KITS ===")

# Load organic/hand percussion kit
print("Loading percussion kit on Hand Perc...")
search_and_load_device(perc_idx, "Drum Rack", "drums")
time.sleep(1.0)

# Load kick kit
print("Loading kick kit...")
search_and_load_device(kick_idx, "Drum Rack", "drums")
time.sleep(1.0)

print("\n=== GENERATING PATTERNS ===")

# Generate sparse breakbeat pattern (more organic than four_on_floor)
print("Generating sparse percussion pattern (breakbeat style)...")
pattern_generator(
    track_index=perc_idx,
    clip_slot_index=0,
    pattern_type="breakbeat",
    bars=8,
    root_note=36,  # C1
    velocity=95,
    swing=0.15,  # Add groove
    humanize=0.25,  # Human feel
    fill=False  # No fill, keep it ritualistic
)

# Generate minimal kick pattern (just accents)
print("Generating kick pattern (hip-hop style for sparseness)...")
pattern_generator(
    track_index=kick_idx,
    clip_slot_index=0,
    pattern_type="hiphop",
    bars=8,
    root_note=36,
    velocity=110,
    swing=0.1,
    humanize=0.15,
    fill=False
)

print("\n=== ADDING EFFECTS ===")

# Saturator on percussion for warmth
print("Adding Saturator to Hand Perc...")
search_and_load_device(perc_idx, "Saturator", "audio_effects")

# Compressor on kick for punch
print("Adding Compressor to Kick...")
search_and_load_device(kick_idx, "Compressor", "audio_effects")

print("\n=== FIRING SCENE ===")
conn.send_command("fire_scene", {"scene_index": 0})

print("\n✓ MATADORA-STYLE INTRO COMPLETE (using pattern generators)!")
print("  - 122 BPM")
print("  - Breakbeat pattern (sparse, organic)")
print("  - Hip-hop kick pattern (minimal)")
print("  - Swing + humanization for groove")
print("\nNow playing—this should sound WAY better than hand-coded patterns!")
