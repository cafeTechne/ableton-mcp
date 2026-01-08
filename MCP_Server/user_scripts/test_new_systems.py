import sys
import os
import time

# Add parent directory to path to import mcp_tooling
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_tooling.generators import (
    generate_chord_progression_advanced,
    generate_bassline_advanced_wrapper,
    pattern_generator,
    generate_strings_advanced_wrapper,
    generate_woodwinds_advanced_wrapper,
    generate_brass_advanced_wrapper,
    add_basic_drum_pattern
)
from mcp_tooling.connection import get_ableton_connection

def run_stress_test():
    print("🚀 Starting Full System Stress Test...")
    
    # 1. Setup Parameters (Complex Inputs)
    KEY = "C# Minor" # Sharp key to test normalization
    SCALE = "minor"
    PROG = "i VII VI V" # Andalusian cadence-ish
    TEMPO = 120 # Implicit
    BARS = 4
    
    print(f"🎵 Generating 4-bar loop in {KEY} ({PROG})...")

    # 2. Tracks Setup (Indices 0-5)
    # We assume tracks exist or we let the generators create them (they use ensure_track_exists)
    # Track 0: Drums
    # Track 1: Bass
    # Track 2: Piano (Chords)
    # Track 3: Strings
    # Track 4: Brass
    # Track 5: Winds

    # 3. DRUMS (Pattern Generator with Fill)
    print("\n🥁 Generating Drums (Trap w/ Fill)...")
    res = pattern_generator(
        track_index=0,
        clip_slot_index=0,
        pattern_type="trap",
        bars=BARS,
        root_note=36, # C1
        velocity=110,
        fill=True # Test fill logic
    )
    print(res)
    time.sleep(1.0)
    
    # Also add some hi-hats via basic drums for layering? No, let's stick to pattern_gen for main drums.
    # Actually, pattern_generator "trap" might be sparse. Let's add top loop.
    print("🥁 Layering 4-on-floor hats...")
    res = add_basic_drum_pattern(
        track_index=0, 
        clip_index=1, # Next slot
        length_beats=BARS*4,
        style="four_on_floor"
    )
    print(res)
    time.sleep(1.0)

    # 4. CHORDS (High Humanize & Voice Leading)
    print("\n🎹 Generating Piano Chords (Voice Lead + Humanize)...")
    res = generate_chord_progression_advanced(
        track_index=2,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        beats_per_chord=4.0, # 1 bar per chord
        voice_lead=True,
        humanize=0.3, # High humanize to test start_time clamping
        velocity=90
    )
    print(res)
    time.sleep(1.0)

    # 5. BASS (Funk Style - busy notes)
    print("\n🎸 Generating Funk Bass...")
    res = generate_bassline_advanced_wrapper(
        track_index=1,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="funk",
        beats_per_chord=4.0,
        velocity=100,
        octave=1
    )
    print(res)
    time.sleep(1.0)

    # 6. STRINGS (Disco - octave jumps)
    print("\n🎻 Generating Disco Strings...")
    res = generate_strings_advanced_wrapper(
        track_index=3,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="disco",
        beats_per_chord=4.0,
        velocity=95,
        octave=4
    )
    print(res)
    time.sleep(1.0)

    # 7. BRASS (Ska - offbeats)
    print("\n🎺 Generating Ska Brass...")
    res = generate_brass_advanced_wrapper(
        track_index=4,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="ska",
        beats_per_chord=4.0,
        velocity=110,
        octave=3
    )
    print(res)
    time.sleep(1.0)
    
    # 8. WINDS (Classical - runs)
    print("\n🎐 Generating Classical Woodwinds...")
    res = generate_woodwinds_advanced_wrapper(
        track_index=5,
        clip_index=0,
        key=KEY,
        scale=SCALE,
        progression=PROG,
        style="classical",
        beats_per_chord=4.0,
        velocity=85,
        octave=5
    )
    print(res)

    print("\n✅ Stress Test Generation Complete! Please listen in Ableton.")

if __name__ == "__main__":
    run_stress_test()
