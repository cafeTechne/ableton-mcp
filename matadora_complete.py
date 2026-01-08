"""
Matadora Rebuild - Complete: Sample-Based Approach
Search for samples in Ableton browser and build percussion intro
"""
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.ableton_helpers import load_sample_to_simpler

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

print("=== CREATING TRACKS ===")
# Track 0: Clap/Hand Perc
conn.send_command("create_midi_track", {"index": 0, "name": "Clap"})
print("Created: Clap")

# Track 1: Kick/Stomp
conn.send_command("create_midi_track", {"index": 1, "name": "Kick"})
print("Created: Kick")

# Track 2: Rim/Stick
conn.send_command("create_midi_track", {"index": 2, "name": "Rim"})
print("Created: Rim")

# Track 3: Texture/Noise
conn.send_command("create_audio_track", {"index": 3, "name": "Texture"})
print("Created: Texture\n")

print("=== LOADING SAMPLES ===")

# Search for and load organic clap
print("Searching for clap sample...")
try:
    clap_result = load_sample_to_simpler(
        conn=conn,
        track_index=0,
        search_query="clap",
        category="percussion"
    )
    print(f"Loaded clap: {clap_result}")
except Exception as e:
    print(f"Clap load failed: {e}, loading Simpler manually...")
    conn.send_command("search_and_load_device", {
        "track_index": 0,
        "query": "Simpler",
        "category": "instruments"
    })

# Search for and load kick
print("Searching for kick sample...")
try:
    kick_result = load_sample_to_simpler(
        conn=conn,
        track_index=1,
        search_query="kick",
        category="drums"
    )
    print(f"Loaded kick: {kick_result}")
except Exception as e:
    print(f"Kick load failed: {e}, loading Simpler manually...")
    conn.send_command("search_and_load_device", {
        "track_index": 1,
        "query": "Simpler",
        "category": "instruments"
    })

# Search for and load rim/stick
print("Searching for rim sample...")
try:
    rim_result = load_sample_to_simpler(
        conn=conn,
        track_index=2,
        search_query="rim",
        category="percussion"
    )
    print(f"Loaded rim: {rim_result}")
except Exception as e:
    print(f"Rim load failed: {e}, loading Simpler manually...")
    conn.send_command("search_and_load_device", {
        "track_index": 2,
        "query": "Simpler",
        "category": "instruments"
    })

print("\n=== ADDING EFFECTS ===")

# Saturator on clap for warmth
print("Adding Saturator to Clap...")
conn.send_command("search_and_load_device", {
    "track_index": 0,
    "query": "Saturator",
    "category": "audio_effects"
})

# Compressor on kick for punch
print("Adding Compressor to Kick...")
conn.send_command("search_and_load_device", {
    "track_index": 1,
    "query": "Compressor",
    "category": "audio_effects"
})

# Auto Filter on texture for movement
print("Adding Auto Filter to Texture...")
conn.send_command("search_and_load_device", {
    "track_index": 3,
    "query": "Auto Filter",
    "category": "audio_effects"
})

print("\n=== CREATING PATTERNS ===")

# CLAP PATTERN (sparse, ritualistic)
print("Creating clap pattern...")
conn.send_command("create_clip", {
    "track_index": 0,
    "clip_index": 0,
    "length": 32.0  # 8 bars
})

clap_notes = [
    # Bar 1-2: Call
    {"pitch": 60, "start": 0.0, "duration": 0.1, "velocity": 100},
    {"pitch": 60, "start": 1.0, "duration": 0.1, "velocity": 75},
    {"pitch": 60, "start": 2.5, "duration": 0.1, "velocity": 95},
    
    {"pitch": 60, "start": 4.0, "duration": 0.1, "velocity": 100},
    {"pitch": 60, "start": 5.0, "duration": 0.1, "velocity": 70},
    {"pitch": 60, "start": 6.5, "duration": 0.1, "velocity": 90},
    
    # Bar 5-6: Repeat with variation
    {"pitch": 60, "start": 16.0, "duration": 0.1, "velocity": 105},
    {"pitch": 60, "start": 17.0, "duration": 0.1, "velocity": 80},
    {"pitch": 60, "start": 18.5, "duration": 0.1, "velocity": 100},
    {"pitch": 60, "start": 19.5, "duration": 0.1, "velocity": 75},
    
    {"pitch": 60, "start": 20.0, "duration": 0.1, "velocity": 105},
    {"pitch": 60, "start": 21.0, "duration": 0.1, "velocity": 72},
    {"pitch": 60, "start": 22.5, "duration": 0.1, "velocity": 95},
]

conn.send_command("add_notes_to_clip", {
    "track_index": 0,
    "clip_index": 0,
    "notes": clap_notes
})
conn.send_command("set_clip_name", {"track_index": 0, "clip_index": 0, "name": "Clap Pattern"})

# KICK PATTERN (response to claps)
print("Creating kick pattern...")
conn.send_command("create_clip", {
    "track_index": 1,
    "clip_index": 0,
    "length": 32.0
})

kick_notes = [
    # Bar 1-2: Response
    {"pitch": 60, "start": 1.5, "duration": 0.15, "velocity": 110},
    {"pitch": 60, "start": 3.0, "duration": 0.15, "velocity": 85},
    
    {"pitch": 60, "start": 5.5, "duration": 0.15, "velocity": 110},
    {"pitch": 60, "start": 7.0, "duration": 0.15, "velocity": 80},
    
    # Bar 5-6
    {"pitch": 60, "start": 17.5, "duration": 0.15, "velocity": 115},
    {"pitch": 60, "start": 19.0, "duration": 0.15, "velocity": 90},
    
    {"pitch": 60, "start": 21.5, "duration": 0.15, "velocity": 115},
    {"pitch": 60, "start": 23.0, "duration": 0.15, "velocity": 85},
    
    # Final stomp
    {"pitch": 60, "start": 31.0, "duration": 0.2, "velocity": 127},
]

conn.send_command("add_notes_to_clip", {
    "track_index": 1,
    "clip_index": 0,
    "notes": kick_notes
})
conn.send_command("set_clip_name", {"track_index": 1, "clip_index": 0, "name": "Kick Pattern"})

# RIM PATTERN (texture, offbeats)
print("Creating rim pattern...")
conn.send_command("create_clip", {
    "track_index": 2,
    "clip_index": 0,
    "length": 32.0
})

rim_notes = [
    # Bar 3-4: Add texture
    {"pitch": 60, "start": 8.25, "duration": 0.08, "velocity": 65},
    {"pitch": 60, "start": 9.75, "duration": 0.08, "velocity": 60},
    {"pitch": 60, "start": 10.5, "duration": 0.08, "velocity": 70},
    
    {"pitch": 60, "start": 12.25, "duration": 0.08, "velocity": 65},
    {"pitch": 60, "start": 13.75, "duration": 0.08, "velocity": 55},
    {"pitch": 60, "start": 14.5, "duration": 0.08, "velocity": 68},
    
    # Bar 7-8: Build tension
    {"pitch": 60, "start": 24.25, "duration": 0.08, "velocity": 70},
    {"pitch": 60, "start": 25.0, "duration": 0.08, "velocity": 65},
    {"pitch": 60, "start": 25.75, "duration": 0.08, "velocity": 75},
    {"pitch": 60, "start": 26.5, "duration": 0.08, "velocity": 72},
    
    {"pitch": 60, "start": 28.25, "duration": 0.08, "velocity": 68},
    {"pitch": 60, "start": 29.0, "duration": 0.08, "velocity": 70},
    {"pitch": 60, "start": 29.75, "duration": 0.08, "velocity": 75},
    {"pitch": 60, "start": 30.5, "duration": 0.08, "velocity": 80},
]

conn.send_command("add_notes_to_clip", {
    "track_index": 2,
    "clip_index": 0,
    "notes": rim_notes
})
conn.send_command("set_clip_name", {"track_index": 2, "clip_index": 0, "name": "Rim Pattern"})

print("\n=== FIRING SCENE ===")
conn.send_command("fire_scene", {"scene_index": 0})

print("\n✓ MATADORA-STYLE INTRO COMPLETE!")
print("  - 122 BPM")
print("  - Sparse, ritualistic percussion")
print("  - Call-and-response clap/kick")
print("  - Rim texture for tension")
print("  - Effects: Saturator, Compressor, Auto Filter")
print("\nNow playing—let's iterate from here!")
