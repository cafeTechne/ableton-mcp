"""
Populate Drums All Scenes
Target: Track 0 (DS Drum Rack)
Scenes: 0 to 5
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.drummer import generate_drum_pattern, list_genres

conn = get_ableton_connection()

TRACK_IDX = 0 # DS Drum Rack

print("=== POPULATING DRUMS (TRACK 0) ===")

# Check available genres to be safe
genres = list_genres()
print(f"Available genres sample: {genres[:10]}")

has_house = "house" in genres
has_reggae = "reggae" in genres

# Scene 0: Intro (Hip Hop / Lo-fi)
print("\n--- Scene 0: Intro ---")
print(generate_drum_pattern(
    track_index=TRACK_IDX, clip_index=0,
    genre="hip_hop" if "hip_hop" in genres else "breakbeat",
    variation="A", bars=4, velocity_scale=0.8
))

# Scene 1: Drop (House / Techno)
print("\n--- Scene 1: Drop ---")
main_genre = "house" if has_house else "techno"
print(generate_drum_pattern(
    track_index=TRACK_IDX, clip_index=1,
    genre=main_genre,
    variation="A", bars=4, velocity_scale=1.0
))

# Scene 2: Variation (House B)
print("\n--- Scene 2: Variation ---")
print(generate_drum_pattern(
    track_index=TRACK_IDX, clip_index=2,
    genre=main_genre,
    variation="B", bars=4, velocity_scale=1.0
))

# Scene 3: Bridge (Funk / Reggae)
print("\n--- Scene 3: Bridge ---")
bridge_genre = "reggae" if has_reggae else "funk"
print(generate_drum_pattern(
    track_index=TRACK_IDX, clip_index=3,
    genre=bridge_genre,
    variation="A", bars=4, velocity_scale=0.9, swing=0.2
))

# Scene 4: Build (Disco)
print("\n--- Scene 4: Build ---")
print(generate_drum_pattern(
    track_index=TRACK_IDX, clip_index=4,
    genre="disco",
    variation="A", bars=4, velocity_scale=1.1 # Louder!
))

# Scene 5: Outro (Ballad / Soft)
print("\n--- Scene 5: Outro ---")
print(generate_drum_pattern(
    track_index=TRACK_IDX, clip_index=5,
    genre="ballad",
    variation="A", bars=4, velocity_scale=0.6 # Quiet
))

print("\nDone.")
