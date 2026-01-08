"""
Quick Mix (Blind)
Set volumes by assumed index since list commands are flaky
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

print("=== QUICK MIX (BLIND INDICES) ===")

# Indices based on build history
mix = {
    0: 0.85, # Hand Perc
    1: 0.95, # Kick
    # 2-4? Maybe missing or deleted in rebuilds?
    5: 0.75, # Rim
    6: 0.5,  # Texture (Audio)
    7: 0.9,  # Bass
    9: 0.8,  # Vocal
    10: 0.6, # Atmosphere
    11: 0.0, # Probe (Mute it if it exists)
    12: 0.7  # Stabs
}

for idx, vol in mix.items():
    try:
        conn.send_command("set_track_volume", {"track_index": idx, "volume": vol})
        print(f"Set Track {idx} volume: {vol}")
    except Exception as e:
        print(f"Could not set Track {idx}: {e}")

# Fire Scene 1 again to force update
conn.send_command("fire_scene", {"scene_index": 1})
