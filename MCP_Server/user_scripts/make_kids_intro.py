"""
Children's Song Intro Generator
A bouncy, fun intro like "Shake Your Sillies Out" but better!

Features:
- Context-aware: checks existing tracks before creating new ones
- Upbeat tempo (130 BPM)
- Bright I-IV-V-IV progression in G major
- Bouncy piano chords
- Playful bass line
- Kid-friendly drum pattern with tambourine feel
"""
import sys
import os
import time

# Ensure we can import mcp_server modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.theory import get_chord_notes
from mcp_tooling.util import load_device_by_name


def main():
    print("🎈 Children's Song Intro Generator 🎈")
    print("=" * 40)
    
    conn = get_ableton_connection()
    if not conn:
        print("Could not connect to Ableton. Please ensure Live is running.")
        return

    # Get current context
    print("\n📋 Checking current session...")
    context = conn.send_command("get_song_context", {"include_clips": True})
    
    print(f"   Tempo: {context['tempo']} BPM")
    print(f"   Tracks: {context['track_count']}")
    print(f"   Existing clips: {sum(1 for t in context['tracks'] if t['has_clips'])}")
    
    # Set upbeat tempo
    print("\n🎵 Setting tempo to 130 BPM...")
    conn.send_command("set_tempo", {"tempo": 130})

    # Find or create tracks
    def find_track_by_name(tracks, pattern):
        for t in tracks:
            if pattern.lower() in t["name"].lower():
                return t["index"]
        return None

    def ensure_track(name, track_type="midi"):
        """Find existing track or create new one."""
        existing = find_track_by_name(context["tracks"], name)
        if existing is not None:
            print(f"   Using existing track '{context['tracks'][existing]['name']}' at index {existing}")
            conn.send_command("set_track_name", {"track_index": existing, "name": name})
            return existing
        else:
            print(f"   Creating new track '{name}'...")
            result = conn.send_command("create_midi_track", {"index": -1})
            idx = result.get("index", len(context["tracks"]))
            conn.send_command("set_track_name", {"track_index": idx, "name": name})
            return idx

    def load_device_safe(track_idx, query, category="all"):
        """Load device using live browser search (fail-proof)."""
        try:
            print(f"   Loading '{query}' on track {track_idx}...")
            result = load_device_by_name(track_idx, query, category)
            if result.get("loaded"):
                print(f"   ✓ Loaded '{result.get('item_name', query)}'")
            else:
                print(f"   ⚠ Could not find '{query}': {result.get('error', 'Unknown error')}")
        except Exception as e:
            print(f"   ⚠ Error loading '{query}': {e}")

    print("\n🎹 Setting up tracks...")
    
    # Use existing MIDI tracks or create new ones
    keys_idx = ensure_track("Kids Keys")
    bass_idx = ensure_track("Kids Bass")
    drums_idx = ensure_track("Kids Drums")
    
    # Load instruments
    print("\n🎺 Loading instruments...")
    load_device_safe(keys_idx, "Piano", category="instruments")
    load_device_safe(bass_idx, "Bass", category="sounds")
    load_device_safe(drums_idx, "Kit", category="drums")
    
    time.sleep(0.5)  # Give devices time to load

    # Musical parameters - G major, upbeat kids progression
    # I - IV - V - IV (G - C - D - C)
    key = "G"
    scale = "major"
    progression = ["I", "IV", "V", "IV"]  # G C D C - classic kids song feel
    bars_per_chord = 1
    total_bars = 4
    clip_length = total_bars * 4.0  # 16 beats

    print("\n🎶 Generating bouncy chord progression...")
    
    # Create keys clip with bouncy rhythm
    conn.send_command("create_clip", {"track_index": keys_idx, "clip_index": 0, "length": clip_length})
    conn.send_command("set_clip_name", {"track_index": keys_idx, "clip_index": 0, "name": "Kids Intro Chords"})
    
    # Chord map for G major
    chord_roots = {"I": 55, "IV": 60, "V": 62}  # G3, C4, D4
    
    keys_notes = []
    for bar_idx, numeral in enumerate(progression):
        root = chord_roots[numeral]
        beat_start = bar_idx * 4.0
        
        # Bouncy rhythm: hit on 1, 2+, 3, 4+ (syncopated feel)
        rhythm = [(0.0, 0.4), (1.5, 0.4), (2.0, 0.4), (3.5, 0.4)]
        
        for offset, dur in rhythm:
            # Major chord: root, +4, +7
            for interval in [0, 4, 7]:
                keys_notes.append({
                    "pitch": root + interval,
                    "start_time": beat_start + offset,
                    "duration": dur,
                    "velocity": 90 if offset == 0 else 75
                })
    
    conn.send_command("add_notes_to_clip", {"track_index": keys_idx, "clip_index": 0, "notes": keys_notes})

    print("🎸 Generating playful bass line...")
    
    # Create bass clip
    conn.send_command("create_clip", {"track_index": bass_idx, "clip_index": 0, "length": clip_length})
    conn.send_command("set_clip_name", {"track_index": bass_idx, "clip_index": 0, "name": "Kids Intro Bass"})
    
    bass_roots = {"I": 43, "IV": 48, "V": 50}  # G2, C3, D3
    
    bass_notes = []
    for bar_idx, numeral in enumerate(progression):
        root = bass_roots[numeral]
        fifth = root + 7
        beat_start = bar_idx * 4.0
        
        # Bouncy bass: root on 1 and 3, fifth on 2+ and 4+
        bass_notes.extend([
            {"pitch": root, "start_time": beat_start + 0.0, "duration": 0.5, "velocity": 100},
            {"pitch": fifth, "start_time": beat_start + 1.5, "duration": 0.4, "velocity": 80},
            {"pitch": root, "start_time": beat_start + 2.0, "duration": 0.5, "velocity": 95},
            {"pitch": fifth, "start_time": beat_start + 3.5, "duration": 0.4, "velocity": 80},
        ])
    
    conn.send_command("add_notes_to_clip", {"track_index": bass_idx, "clip_index": 0, "notes": bass_notes})

    print("🥁 Generating fun drum pattern...")
    
    # Create drum clip
    conn.send_command("create_clip", {"track_index": drums_idx, "clip_index": 0, "length": clip_length})
    conn.send_command("set_clip_name", {"track_index": drums_idx, "clip_index": 0, "name": "Kids Intro Drums"})
    
    # Drum mapping (GM standard)
    KICK = 36
    SNARE = 38
    CLAP = 39
    CLOSED_HAT = 42
    TAMBOURINE = 54  # Adds that kids-song shimmer
    
    drum_notes = []
    for bar in range(total_bars):
        beat_start = bar * 4.0
        
        # Kick on 1 and 3
        drum_notes.append({"pitch": KICK, "start_time": beat_start + 0.0, "duration": 0.25, "velocity": 100})
        drum_notes.append({"pitch": KICK, "start_time": beat_start + 2.0, "duration": 0.25, "velocity": 95})
        
        # Snare/Clap on 2 and 4 (alternating for fun)
        drum_notes.append({"pitch": SNARE, "start_time": beat_start + 1.0, "duration": 0.25, "velocity": 90})
        drum_notes.append({"pitch": CLAP, "start_time": beat_start + 3.0, "duration": 0.25, "velocity": 85})
        
        # Tambourine on all 8th notes (kids song shimmer!)
        for i in range(8):
            vel = 70 if i % 2 == 0 else 55
            drum_notes.append({"pitch": TAMBOURINE, "start_time": beat_start + (i * 0.5), "duration": 0.2, "velocity": vel})
        
        # Closed hi-hat on off-beats
        for i in [1, 3, 5, 7]:
            drum_notes.append({"pitch": CLOSED_HAT, "start_time": beat_start + (i * 0.5), "duration": 0.25, "velocity": 60})
    
    conn.send_command("add_notes_to_clip", {"track_index": drums_idx, "clip_index": 0, "notes": drum_notes})

    # Enable looping
    conn.send_command("set_clip_loop", {"track_index": keys_idx, "clip_index": 0, "loop_on": True})
    conn.send_command("set_clip_loop", {"track_index": bass_idx, "clip_index": 0, "loop_on": True})
    conn.send_command("set_clip_loop", {"track_index": drums_idx, "clip_index": 0, "loop_on": True})

    print("\n" + "=" * 40)
    print("🎉 SUCCESS! Kids song intro created!")
    print("=" * 40)
    print(f"\n   Tempo: 130 BPM")
    print(f"   Key: G Major")
    print(f"   Progression: G - C - D - C (I - IV - V - IV)")
    print(f"   Style: Bouncy, syncopated, tambourine shimmer")
    print(f"\n   Press play in Ableton to hear it! 🎈")


if __name__ == "__main__":
    main()
