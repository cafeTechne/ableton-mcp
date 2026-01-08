"""
Matadora Rebuild - Percussion-First Approach
Clear session and start with ritualistic percussion intro
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

print("Clearing current session...")

# Delete all tracks except Master
session_info = conn.send_command("get_session_info", {})
track_count = session_info.get("track_count", 0)

print(f"Found {track_count} tracks, deleting all MIDI/Audio tracks...")

# Delete tracks in reverse order to avoid index shifting
for i in range(track_count - 1, -1, -1):
    try:
        conn.send_command("delete_track", {"track_index": i})
    except:
        pass  # Skip if it's the Master or can't be deleted

print("Session cleared!")

# Set tempo to 122 BPM
print("\nSetting tempo to 122 BPM...")
conn.send_command("set_tempo", {"tempo": 122})

# Create new track structure
print("\nCreating percussion-first track structure...")

# Track 1: Hand Percussion (organic)
conn.send_command("create_midi_track", {"index": 0, "name": "Hand Perc"})
print("Created: Hand Perc")

# Track 2: Percussion Transients (synthetic punch)
conn.send_command("create_midi_track", {"index": 1, "name": "Perc Punch"})
print("Created: Perc Punch")

# Track 3: Vocal Chant (placeholder for now)
conn.send_command("create_audio_track", {"index": 2, "name": "Vocal Chant"})
print("Created: Vocal Chant")

# Track 4: Texture/Air
conn.send_command("create_audio_track", {"index": 3, "name": "Texture"})
print("Created: Texture")

print("\n✓ Clean slate ready for percussion-first build!")
