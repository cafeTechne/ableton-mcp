
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import (
    generate_bassline_advanced_wrapper,
    generate_strings_advanced_wrapper,
    generate_rhythmic_comp,
    generate_chord_progression_advanced
)

def add_complementary_midi():
    print("🎹 Generating Complementary MIDI...")
    conn = get_ableton_connection()
    
    KEY = "G"
    SCALE = "major"
    PROG = "I vi V IV"
    BARS = 8
    
    # 1. Sub Bass (Track 14) - Rock/Root style for solid foundation
    print("   🎸 Adding Sub Bass...")
    conn.send_command("delete_clip", {"track_index": 14, "clip_index": 0})
    generate_bassline_advanced_wrapper(
        track_index=14,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="root",
        octave=1,
        velocity=100,
        total_bars=BARS
    )

    # 2. Mid Bass (Track 15) - Pulse for movement
    print("   🎸 Adding Mid Bass...")
    conn.send_command("delete_clip", {"track_index": 15, "clip_index": 0})
    generate_bassline_advanced_wrapper(
        track_index=15,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="pulse",
        octave=2,
        velocity=95,
        total_bars=BARS
    )

    # 3. Chord Stabs (Track 17) - House rhythmic stabs
    print("   🎹 Adding Chord Stabs...")
    conn.send_command("delete_clip", {"track_index": 17, "clip_index": 0})
    generate_rhythmic_comp(
        track_index=17,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="house_piano",
        octave=4,
        velocity=105,
        total_bars=BARS
    )

    # 4. Pad / Atmos (Track 18) - Sustained chords
    print("   ☁️  Adding Pads...")
    conn.send_command("delete_clip", {"track_index": 18, "clip_index": 0})
    generate_strings_advanced_wrapper(
        track_index=18,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="pop",
        octave=3,
        velocity=85,
        total_bars=BARS
    )

    # 5. Lead / Topline (Track 19) - Simple rhythmic lead
    print("   🎷 Adding Lead Topline...")
    conn.send_command("delete_clip", {"track_index": 19, "clip_index": 0})
    # Using 'disco_octaves' for a rhythmic lead feel if no melody gen is ready
    generate_rhythmic_comp(
        track_index=19,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="disco_octaves",
        octave=5,
        velocity=110,
        total_bars=BARS
    )

    # 6. Arp / Pluck (Track 20)
    print("   ✨ Adding Arp Pluck...")
    conn.send_command("delete_clip", {"track_index": 20, "clip_index": 0})
    # For Arp, we'll just use a faster rhythmic comp
    generate_rhythmic_comp(
        track_index=20,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="motown", # Quarters can act as a base for an internal Arp device
        octave=4,
        velocity=90,
        total_bars=BARS
    )

    print("\n✅ Complementary MIDI Generated!")

if __name__ == "__main__":
    add_complementary_midi()
