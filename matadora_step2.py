"""
Matadora-style Track Builder - Step 2
Load instruments and rename tracks
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# Rename tracks properly
print("Renaming tracks...")
conn.send_command("set_track_name", {"track_index": 0, "name": "Drums"})
conn.send_command("set_track_name", {"track_index": 1, "name": "Bass"})
conn.send_command("set_track_name", {"track_index": 2, "name": "Synth Lead"})
conn.send_command("set_track_name", {"track_index": 3, "name": "Pad"})
print("Tracks renamed!")

# Load instruments
print("\nLoading instruments...")

# Load Drum Rack on track 0
print("Loading Drum Rack...")
conn.send_command("search_and_load_device", {
    "track_index": 0,
    "query": "Drum Rack",
    "category": "drums"
})

# Load a bass synth on track 1 (Analog or Operator)
print("Loading Bass synth...")
conn.send_command("search_and_load_device", {
    "track_index": 1,
    "query": "Analog",
    "category": "instruments"
})

# Load lead synth on track 2
print("Loading Lead synth...")
conn.send_command("search_and_load_device", {
    "track_index": 2,
    "query": "Analog",
    "category": "instruments"
})

# Load pad on track 3
print("Loading Pad synth...")
conn.send_command("search_and_load_device", {
    "track_index": 3,
    "query": "Analog",
    "category": "instruments"
})

print("\n✓ Instruments loaded!")
