"""
Matadora-style Track Builder
Sofi Tukker inspired - 122 BPM, A minor
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# 1. Set tempo to 122 BPM
print("Setting tempo to 122 BPM...")
conn.send_command("set_tempo", {"tempo": 122})

# 2. Get current session info
info = conn.send_command("get_session_info", {})
print(f"Session info retrieved")
print(f"Tracks: {info.get('track_count', 'unknown')}")

# 3. Create tracks
print("\nCreating tracks...")

# Drums track
result = conn.send_command("create_midi_track", {"index": 0, "name": "Drums"})
print(f"Created: Drums - {result}")

# Bass track
result = conn.send_command("create_midi_track", {"index": 1, "name": "Bass"})
print(f"Created: Bass - {result}")

# Synth Lead track
result = conn.send_command("create_midi_track", {"index": 2, "name": "Synth Lead"})
print(f"Created: Synth Lead - {result}")

# Pad track
result = conn.send_command("create_midi_track", {"index": 3, "name": "Pad"})
print(f"Created: Pad - {result}")

print("\n✓ Foundation complete! Tempo: 122 BPM, 4 tracks created.")
