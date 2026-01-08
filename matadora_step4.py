"""
Matadora-style Track Builder - Step 4
Add synth lead (with Arpeggiator) and pad chords
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# ========== SYNTH LEAD with ARPEGGIATOR ==========
print("Loading Arpeggiator on Synth Lead track...")

# Load Arpeggiator MIDI effect
conn.send_command("search_and_load_device", {
    "track_index": 2,
    "query": "Arpeggiator",
    "category": "midi_effects"
})

# Create a 4-bar clip with chord triggers for the arpeggiator
print("Creating synth lead clip...")
conn.send_command("create_clip", {
    "track_index": 2,
    "clip_index": 0,
    "length": 16.0
})

# Am chord voicing: A3, C4, E4, G4 (Am7)
# The arpeggiator will break this into patterns
synth_notes = [
    # Bar 1-2: Am7
    {"pitch": 57, "start": 0.0, "duration": 8.0, "velocity": 90},   # A3
    {"pitch": 60, "start": 0.0, "duration": 8.0, "velocity": 85},   # C4
    {"pitch": 64, "start": 0.0, "duration": 8.0, "velocity": 85},   # E4
    {"pitch": 67, "start": 0.0, "duration": 8.0, "velocity": 80},   # G4
    
    # Bar 3-4: F major 7 -> E minor (tension/release)
    {"pitch": 53, "start": 8.0, "duration": 4.0, "velocity": 90},   # F3
    {"pitch": 57, "start": 8.0, "duration": 4.0, "velocity": 85},   # A3
    {"pitch": 60, "start": 8.0, "duration": 4.0, "velocity": 85},   # C4
    {"pitch": 64, "start": 8.0, "duration": 4.0, "velocity": 80},   # E4
    
    {"pitch": 52, "start": 12.0, "duration": 4.0, "velocity": 90},  # E3
    {"pitch": 55, "start": 12.0, "duration": 4.0, "velocity": 85},  # G3
    {"pitch": 59, "start": 12.0, "duration": 4.0, "velocity": 85},  # B3
    {"pitch": 64, "start": 12.0, "duration": 4.0, "velocity": 80},  # E4
]

conn.send_command("add_notes_to_clip", {
    "track_index": 2,
    "clip_index": 0,
    "notes": synth_notes
})
print(f"Added {len(synth_notes)} synth notes (arpeggiator will process these)")

conn.send_command("set_clip_name", {
    "track_index": 2,
    "clip_index": 0,
    "name": "Lead Arp"
})

# ========== PAD CHORDS ==========
print("\nCreating pad chords...")

conn.send_command("create_clip", {
    "track_index": 3,
    "clip_index": 0,
    "length": 16.0
})

# Warm, sustained pad chords - Am progression
# Am -> F -> G -> Em (classic tropical house progression)
pad_notes = [
    # Am (bars 1-2)
    {"pitch": 45, "start": 0.0, "duration": 7.5, "velocity": 70},   # A2
    {"pitch": 57, "start": 0.0, "duration": 7.5, "velocity": 65},   # A3
    {"pitch": 60, "start": 0.0, "duration": 7.5, "velocity": 65},   # C4
    {"pitch": 64, "start": 0.0, "duration": 7.5, "velocity": 60},   # E4
    
    # F (bar 3)
    {"pitch": 41, "start": 8.0, "duration": 3.5, "velocity": 70},   # F2
    {"pitch": 53, "start": 8.0, "duration": 3.5, "velocity": 65},   # F3
    {"pitch": 57, "start": 8.0, "duration": 3.5, "velocity": 65},   # A3
    {"pitch": 60, "start": 8.0, "duration": 3.5, "velocity": 60},   # C4
    
    # G (bar 3.5)
    {"pitch": 43, "start": 12.0, "duration": 3.5, "velocity": 70},  # G2
    {"pitch": 55, "start": 12.0, "duration": 3.5, "velocity": 65},  # G3
    {"pitch": 59, "start": 12.0, "duration": 3.5, "velocity": 65},  # B3
    {"pitch": 62, "start": 12.0, "duration": 3.5, "velocity": 60},  # D4
]

conn.send_command("add_notes_to_clip", {
    "track_index": 3,
    "clip_index": 0,
    "notes": pad_notes
})
print(f"Added {len(pad_notes)} pad notes")

conn.send_command("set_clip_name", {
    "track_index": 3,
    "clip_index": 0,
    "name": "Pad Chords"
})

print("\n✓ Synth lead and pad complete!")
