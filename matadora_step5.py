"""
Matadora-style Track Builder - Step 5
Add effects and fire all clips
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# ========== EFFECTS ==========
print("Adding effects...")

# Auto Filter on Synth Lead for that Sofi Tukker sweep
print("Adding Auto Filter to Synth Lead...")
conn.send_command("search_and_load_device", {
    "track_index": 2,
    "query": "Auto Filter",
    "category": "audio_effects"
})

# Compressor on Bass for punch
print("Adding Compressor to Bass...")
conn.send_command("search_and_load_device", {
    "track_index": 1,
    "query": "Compressor",
    "category": "audio_effects"
})

# Reverb on Pad for space
print("Adding Reverb to Pad...")
conn.send_command("search_and_load_device", {
    "track_index": 3,
    "query": "Reverb",
    "category": "audio_effects"
})

# ========== FIRE ALL CLIPS ==========
print("\nFiring all clips to play the track!")

# Fire Scene 1 to play all clips together
conn.send_command("fire_scene", {"scene_index": 0})

print("\n✓ Matadora-style track is now playing!")
print("  - 122 BPM")
print("  - A minor")
print("  - Drums, Bass, Arp Lead, Pad")
print("\nListen and let me know what you think!")
