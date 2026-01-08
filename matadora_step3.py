"""
Matadora-style Track Builder - Step 3
Create drum pattern and bassline
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# ========== DRUMS ==========
print("Creating drum pattern (4 bars)...")

# Create a 4-bar clip on the Drums track
conn.send_command("create_clip", {
    "track_index": 0,
    "clip_index": 0,
    "length": 16.0  # 4 bars at 4 beats each
})

# Four-on-the-floor kick pattern (C1 = 36)
# Kick on every beat
kick_notes = []
for beat in range(16):
    kick_notes.append({
        "pitch": 36,  # C1 - kick
        "start": float(beat),
        "duration": 0.5,
        "velocity": 110 if beat % 4 == 0 else 100  # Accent on downbeat
    })

# Clap/Snare on 2 and 4 (D1 = 38)
clap_notes = []
for bar in range(4):
    for beat in [1, 3]:  # beats 2 and 4 in each bar
        clap_notes.append({
            "pitch": 38,  # D1 - snare/clap
            "start": float(bar * 4 + beat),
            "duration": 0.25,
            "velocity": 100
        })

# Hi-hats - 16th notes (F#1 = 42)
hihat_notes = []
for sixteenth in range(64):  # 16 sixteenths per bar * 4 bars
    velocity = 80 if sixteenth % 4 == 0 else 60  # Accent on quarter notes
    hihat_notes.append({
        "pitch": 42,  # F#1 - closed hihat
        "start": float(sixteenth * 0.25),
        "duration": 0.2,
        "velocity": velocity
    })

# Open hi-hat on offbeats (A#1 = 46)
open_hh = []
for bar in range(4):
    for beat in [0.5, 2.5]:  # Offbeat of 1 and 3
        open_hh.append({
            "pitch": 46,  # A#1 - open hihat
            "start": float(bar * 4 + beat),
            "duration": 0.5,
            "velocity": 85
        })

# Add all drum notes
all_drum_notes = kick_notes + clap_notes + hihat_notes + open_hh
conn.send_command("add_notes_to_clip", {
    "track_index": 0,
    "clip_index": 0,
    "notes": all_drum_notes
})
print(f"Added {len(all_drum_notes)} drum notes!")

# Name the clip
conn.send_command("set_clip_name", {
    "track_index": 0,
    "clip_index": 0,
    "name": "Main Beat"
})

# ========== BASS (A minor) ==========
print("\nCreating bassline (A minor, syncopated)...")

# Create a 4-bar clip on the Bass track
conn.send_command("create_clip", {
    "track_index": 1,
    "clip_index": 0,
    "length": 16.0
})

# A minor bassline - funky, syncopated
# Root = A2 (45), also using E2 (40), G2 (43)
bass_notes = [
    # Bar 1 - A minor groove
    {"pitch": 45, "start": 0.0, "duration": 0.5, "velocity": 110},    # A
    {"pitch": 45, "start": 0.75, "duration": 0.25, "velocity": 90},   # syncopation
    {"pitch": 40, "start": 1.5, "duration": 0.5, "velocity": 100},    # E
    {"pitch": 43, "start": 2.25, "duration": 0.25, "velocity": 85},   # G
    {"pitch": 45, "start": 3.0, "duration": 0.5, "velocity": 100},    # A
    {"pitch": 45, "start": 3.75, "duration": 0.25, "velocity": 80},   # syncopation
    
    # Bar 2 - variation
    {"pitch": 45, "start": 4.0, "duration": 0.5, "velocity": 110},
    {"pitch": 43, "start": 4.75, "duration": 0.25, "velocity": 90},
    {"pitch": 40, "start": 5.5, "duration": 0.5, "velocity": 100},
    {"pitch": 38, "start": 6.0, "duration": 0.25, "velocity": 85},    # D
    {"pitch": 40, "start": 6.5, "duration": 0.5, "velocity": 100},    # E
    {"pitch": 45, "start": 7.5, "duration": 0.5, "velocity": 95},
    
    # Bar 3 - repeat bar 1
    {"pitch": 45, "start": 8.0, "duration": 0.5, "velocity": 110},
    {"pitch": 45, "start": 8.75, "duration": 0.25, "velocity": 90},
    {"pitch": 40, "start": 9.5, "duration": 0.5, "velocity": 100},
    {"pitch": 43, "start": 10.25, "duration": 0.25, "velocity": 85},
    {"pitch": 45, "start": 11.0, "duration": 0.5, "velocity": 100},
    {"pitch": 45, "start": 11.75, "duration": 0.25, "velocity": 80},
    
    # Bar 4 - turnaround
    {"pitch": 45, "start": 12.0, "duration": 0.5, "velocity": 110},
    {"pitch": 47, "start": 12.75, "duration": 0.25, "velocity": 90},  # B - tension
    {"pitch": 48, "start": 13.25, "duration": 0.25, "velocity": 95},  # C
    {"pitch": 47, "start": 13.75, "duration": 0.25, "velocity": 90},  # B
    {"pitch": 45, "start": 14.0, "duration": 0.5, "velocity": 100},   # A
    {"pitch": 40, "start": 15.0, "duration": 0.5, "velocity": 95},    # E - leading back
    {"pitch": 43, "start": 15.5, "duration": 0.5, "velocity": 90},    # G
]

conn.send_command("add_notes_to_clip", {
    "track_index": 1,
    "clip_index": 0,
    "notes": bass_notes
})
print(f"Added {len(bass_notes)} bass notes!")

conn.send_command("set_clip_name", {
    "track_index": 1,
    "clip_index": 0,
    "name": "Main Bass"
})

print("\n✓ Drums and bass complete!")
