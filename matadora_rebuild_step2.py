"""
Matadora Rebuild - Step 2: Sparse Hand Percussion
Create ritualistic, breathing percussion pattern
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# Load Drum Rack on Hand Perc track
print("Loading Drum Rack with organic kit...")
conn.send_command("search_and_load_device", {
    "track_index": 0,
    "query": "Drum Rack",
    "category": "drums"
})

# Create 8-bar intro clip (32 beats)
print("\nCreating sparse hand percussion pattern (8 bars)...")
conn.send_command("create_clip", {
    "track_index": 0,
    "clip_index": 0,
    "length": 32.0
})

# SPARSE, RITUALISTIC PATTERN
# Key principle: Space between hits matters
# Velocity variation is crucial

perc_notes = []

# Pattern A: Clap + Stomp call-and-response (bars 1-2)
# Clap (higher pitch, D1 = 38)
perc_notes.extend([
    {"pitch": 38, "start": 0.0, "duration": 0.1, "velocity": 100},   # Strong
    {"pitch": 38, "start": 1.0, "duration": 0.1, "velocity": 75},    # Ghost
    {"pitch": 38, "start": 2.5, "duration": 0.1, "velocity": 95},    # Accent
    
    {"pitch": 38, "start": 4.0, "duration": 0.1, "velocity": 100},
    {"pitch": 38, "start": 5.0, "duration": 0.1, "velocity": 70},
    {"pitch": 38, "start": 6.5, "duration": 0.1, "velocity": 90},
])

# Stomp/Kick (C1 = 36) - lower, responding
perc_notes.extend([
    {"pitch": 36, "start": 1.5, "duration": 0.15, "velocity": 110},
    {"pitch": 36, "start": 3.0, "duration": 0.15, "velocity": 85},
    
    {"pitch": 36, "start": 5.5, "duration": 0.15, "velocity": 110},
    {"pitch": 36, "start": 7.0, "duration": 0.15, "velocity": 80},
])

# Pattern B: Add rim/stick hits for texture (bars 3-4)
# Rim (E1 = 40)
perc_notes.extend([
    {"pitch": 40, "start": 8.25, "duration": 0.08, "velocity": 65},   # Offbeat
    {"pitch": 40, "start": 9.75, "duration": 0.08, "velocity": 60},
    {"pitch": 40, "start": 10.5, "duration": 0.08, "velocity": 70},
    
    {"pitch": 40, "start": 12.25, "duration": 0.08, "velocity": 65},
    {"pitch": 40, "start": 13.75, "duration": 0.08, "velocity": 55},
    {"pitch": 40, "start": 14.5, "duration": 0.08, "velocity": 68},
])

# Repeat pattern A with variation (bars 5-6)
perc_notes.extend([
    {"pitch": 38, "start": 16.0, "duration": 0.1, "velocity": 105},
    {"pitch": 38, "start": 17.0, "duration": 0.1, "velocity": 80},
    {"pitch": 38, "start": 18.5, "duration": 0.1, "velocity": 100},
    {"pitch": 38, "start": 19.5, "duration": 0.1, "velocity": 75},  # Extra hit
    
    {"pitch": 38, "start": 20.0, "duration": 0.1, "velocity": 105},
    {"pitch": 38, "start": 21.0, "duration": 0.1, "velocity": 72},
    {"pitch": 38, "start": 22.5, "duration": 0.1, "velocity": 95},
])

perc_notes.extend([
    {"pitch": 36, "start": 17.5, "duration": 0.15, "velocity": 115},
    {"pitch": 36, "start": 19.0, "duration": 0.15, "velocity": 90},
    
    {"pitch": 36, "start": 21.5, "duration": 0.15, "velocity": 115},
    {"pitch": 36, "start": 23.0, "duration": 0.15, "velocity": 85},
])

# Build tension (bars 7-8) - add more rim hits
perc_notes.extend([
    {"pitch": 40, "start": 24.25, "duration": 0.08, "velocity": 70},
    {"pitch": 40, "start": 25.0, "duration": 0.08, "velocity": 65},
    {"pitch": 40, "start": 25.75, "duration": 0.08, "velocity": 75},
    {"pitch": 40, "start": 26.5, "duration": 0.08, "velocity": 72},
    
    {"pitch": 40, "start": 28.25, "duration": 0.08, "velocity": 68},
    {"pitch": 40, "start": 29.0, "duration": 0.08, "velocity": 70},
    {"pitch": 40, "start": 29.75, "duration": 0.08, "velocity": 75},
    {"pitch": 40, "start": 30.5, "duration": 0.08, "velocity": 80},
])

# Final stomp before drop
perc_notes.append({"pitch": 36, "start": 31.0, "duration": 0.2, "velocity": 127})

conn.send_command("add_notes_to_clip", {
    "track_index": 0,
    "clip_index": 0,
    "notes": perc_notes
})

print(f"Added {len(perc_notes)} percussion hits (sparse, breathing pattern)")

conn.send_command("set_clip_name", {
    "track_index": 0,
    "clip_index": 0,
    "name": "Hand Perc Intro"
})

print("\n✓ Ritualistic percussion pattern created!")
print("  - Call-and-response clap/stomp")
print("  - Velocity variation for human feel")
print("  - Space is intentional")
