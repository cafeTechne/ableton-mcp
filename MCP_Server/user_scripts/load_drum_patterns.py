
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

def load_patterns():
    print("🎹 Loading House Drum Patterns...")
    conn = get_ableton_connection()
    
    # Track assignments from previous scan
    track_map = {
        "Kick": 3,
        "Clap / Snare": 4,
        "Closed Hat": 5,
        "Open Hat": 6,
        "Shaker": 7,
        "Percussion Low": 8,
        "Percussion High": 9,
        "Drum Fills": 10,
        "Drum FX": 11
    }
    
    def add_pattern(track_idx, notes, length=16.0):
        # Create clip slot 0
        conn.send_command("create_clip", {"track_index": track_idx, "clip_index": 0, "length": length})
        # Add notes: (pitch, start, duration, velocity, mute)
        conn.send_command("add_notes_to_clip", {"track_index": track_idx, "clip_index": 0, "notes": notes})
        print(f"   ✅ Applied {len(notes)} notes to Track {track_idx}")

    BARS = 4
    BEATS = BARS * 4
    
    # 1. Kick (4-on-the-floor)
    kick_notes = []
    for beat in range(BEATS):
        kick_notes.append((60, beat * 1.0, 0.2, 110, False))
    add_pattern(track_map["Kick"], kick_notes)
    
    # 2. Clap / Snare (Backbeat)
    clap_notes = []
    for bar in range(BARS):
        clap_notes.append((60, bar * 4.0 + 1.0, 0.2, 105, False))
        clap_notes.append((60, bar * 4.0 + 3.0, 0.2, 105, False))
    add_pattern(track_map["Clap / Snare"], clap_notes)
    
    # 3. Closed Hat (Straight 8ths)
    ch_notes = []
    for step in range(BEATS * 2):
        ch_notes.append((60, step * 0.5, 0.1, 80 if step % 2 == 0 else 95, False))
    add_pattern(track_map["Closed Hat"], ch_notes)
    
    # 4. Open Hat (Off-beats)
    oh_notes = []
    for beat in range(BEATS):
        oh_notes.append((60, beat * 1.0 + 0.5, 0.3, 110, False))
    add_pattern(track_map["Open Hat"], oh_notes)
    
    # 5. Shaker (16th groove)
    shk_notes = []
    for step in range(BEATS * 4):
        vel = 90 if step % 4 == 0 else (70 if step % 2 == 0 else 60)
        shk_notes.append((60, step * 0.25, 0.1, vel, False))
    add_pattern(track_map["Shaker"], shk_notes)
    
    # 6. Percussion Low (Syncopation)
    pl_notes = []
    for bar in range(BARS):
        pl_notes.append((60, bar * 4.0 + 1.75, 0.2, 90, False))
        pl_notes.append((60, bar * 4.0 + 3.75, 0.2, 95, False))
    add_pattern(track_map["Percussion Low"], pl_notes)
    
    # 7. Percussion High (Accents)
    ph_notes = []
    for bar in range(BARS):
        ph_notes.append((60, bar * 4.0 + 1.25, 0.1, 100, False))
        ph_notes.append((60, bar * 4.0 + 2.25, 0.1, 90, False))
    add_pattern(track_map["Percussion High"], ph_notes)
    
    # 8. Drum FX (Impact at start)
    fx_notes = [(60, 0.0, 4.0, 115, False)]
    add_pattern(track_map["Drum FX"], fx_notes)

    print("\n✨ All House Patterns Loaded!")

if __name__ == "__main__":
    load_patterns()
