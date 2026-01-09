"""
Anamanaguchi-Style Drums - Driving Punk Rock Patterns

Overwrites clips on the Rock Drums track with driving, straight-ahead beats.
No syncopation - pure energy!
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))

from mcp_tooling.connection import get_ableton_connection

# GM Drum Map
KICK = 36
SNARE = 38
CLOSED_HH = 42
OPEN_HH = 46
CRASH = 49

def create_anamanaguchi_patterns():
    conn = get_ableton_connection()
    
    # Find the Rock Drums track (index 4)
    track_idx = 4
    print(f"Updating Rock Drums track (index {track_idx}) with Anamanaguchi patterns...")
    
    # Define 8 driving punk patterns
    patterns = [
        # Pattern 1: Classic punk (kick-snare-kick-snare, 8th hats)
        {
            "name": "Punk Drive",
            "notes": _punk_drive(bars=4)
        },
        # Pattern 2: Double-time punk
        {
            "name": "Punk Fast",
            "notes": _punk_fast(bars=4)
        },
        # Pattern 3: Driving 4-on-floor with snare 2+4
        {
            "name": "Chiptune Drive",
            "notes": _chiptune_drive(bars=4)
        },
        # Pattern 4: Punk with crash accents
        {
            "name": "Crash Punk",
            "notes": _crash_punk(bars=4)
        },
        # Pattern 5: 16th note hi-hats (energy!)
        {
            "name": "16th Energy",
            "notes": _sixteenth_energy(bars=4)
        },
        # Pattern 6: Half-time feel
        {
            "name": "Half-Time",
            "notes": _half_time(bars=4)
        },
        # Pattern 7: Punk with open hi-hat accents
        {
            "name": "Open Hat Punk",
            "notes": _open_hat_punk(bars=4)
        },
        # Pattern 8: Fill/Build pattern
        {
            "name": "Build Up",
            "notes": _build_up(bars=4)
        },
    ]
    
    for i, pattern in enumerate(patterns):
        try:
            # Delete existing clip
            try:
                conn.send_command("delete_clip", {"track_index": track_idx, "clip_index": i})
            except:
                pass
            
            # Create new clip
            conn.send_command("create_clip", {
                "track_index": track_idx,
                "clip_index": i,
                "length": 16.0  # 4 bars
            })
            
            # Add notes
            conn.send_command("add_notes_to_clip", {
                "track_index": track_idx,
                "clip_index": i,
                "notes": pattern["notes"]
            })
            
            # Label it
            conn.send_command("set_clip_name", {
                "track_index": track_idx,
                "clip_index": i,
                "name": pattern["name"]
            })
            
            print(f"  Scene {i+1}: {pattern['name']} ({len(pattern['notes'])} notes)")
        except Exception as e:
            print(f"  Scene {i+1} failed: {e}")
    
    print("\n🥁 Anamanaguchi patterns loaded! Pure driving energy!")

def _punk_drive(bars=4):
    """Classic punk: kick on 1+3, snare on 2+4, 8th note hats"""
    notes = []
    for bar in range(bars):
        base = bar * 4.0
        # Kick on 1 and 3
        notes.append({"pitch": KICK, "start_time": base + 0, "duration": 0.25, "velocity": 110})
        notes.append({"pitch": KICK, "start_time": base + 2, "duration": 0.25, "velocity": 105})
        # Snare on 2 and 4
        notes.append({"pitch": SNARE, "start_time": base + 1, "duration": 0.25, "velocity": 115})
        notes.append({"pitch": SNARE, "start_time": base + 3, "duration": 0.25, "velocity": 115})
        # 8th note hi-hats
        for beat in range(8):
            vel = 90 if beat % 2 == 0 else 75
            notes.append({"pitch": CLOSED_HH, "start_time": base + beat * 0.5, "duration": 0.2, "velocity": vel})
    return notes

def _punk_fast(bars=4):
    """Double-time punk: kick every beat, snare on 2+4"""
    notes = []
    for bar in range(bars):
        base = bar * 4.0
        # Kick every beat
        for beat in range(4):
            notes.append({"pitch": KICK, "start_time": base + beat, "duration": 0.25, "velocity": 105})
        # Snare on 2 and 4
        notes.append({"pitch": SNARE, "start_time": base + 1, "duration": 0.25, "velocity": 120})
        notes.append({"pitch": SNARE, "start_time": base + 3, "duration": 0.25, "velocity": 120})
        # 8th note hi-hats
        for beat in range(8):
            notes.append({"pitch": CLOSED_HH, "start_time": base + beat * 0.5, "duration": 0.2, "velocity": 85})
    return notes

def _chiptune_drive(bars=4):
    """4-on-floor with snare backbeat"""
    notes = []
    for bar in range(bars):
        base = bar * 4.0
        # Kick on every beat (4-on-floor)
        for beat in range(4):
            notes.append({"pitch": KICK, "start_time": base + beat, "duration": 0.25, "velocity": 110})
        # Snare on 2 and 4
        notes.append({"pitch": SNARE, "start_time": base + 1, "duration": 0.25, "velocity": 115})
        notes.append({"pitch": SNARE, "start_time": base + 3, "duration": 0.25, "velocity": 115})
        # Offbeat hi-hats (classic house/dance feel)
        for beat in range(4):
            notes.append({"pitch": CLOSED_HH, "start_time": base + beat + 0.5, "duration": 0.2, "velocity": 95})
    return notes

def _crash_punk(bars=4):
    """Punk with crash on bar 1"""
    notes = _punk_drive(bars)
    # Add crash on beat 1 of each bar
    for bar in range(bars):
        notes.append({"pitch": CRASH, "start_time": bar * 4.0, "duration": 1.0, "velocity": 100})
    return notes

def _sixteenth_energy(bars=4):
    """16th note hi-hats for maximum energy"""
    notes = []
    for bar in range(bars):
        base = bar * 4.0
        # Kick on 1 and 3
        notes.append({"pitch": KICK, "start_time": base + 0, "duration": 0.25, "velocity": 110})
        notes.append({"pitch": KICK, "start_time": base + 2, "duration": 0.25, "velocity": 105})
        # Snare on 2 and 4
        notes.append({"pitch": SNARE, "start_time": base + 1, "duration": 0.25, "velocity": 115})
        notes.append({"pitch": SNARE, "start_time": base + 3, "duration": 0.25, "velocity": 115})
        # 16th note hi-hats
        for step in range(16):
            vel = 95 if step % 4 == 0 else 70 if step % 2 == 0 else 55
            notes.append({"pitch": CLOSED_HH, "start_time": base + step * 0.25, "duration": 0.15, "velocity": vel})
    return notes

def _half_time(bars=4):
    """Half-time feel for verses"""
    notes = []
    for bar in range(bars):
        base = bar * 4.0
        # Kick on 1 only
        notes.append({"pitch": KICK, "start_time": base + 0, "duration": 0.25, "velocity": 110})
        # Snare on 3 (half-time feel)
        notes.append({"pitch": SNARE, "start_time": base + 2, "duration": 0.25, "velocity": 120})
        # 8th note hi-hats
        for beat in range(8):
            notes.append({"pitch": CLOSED_HH, "start_time": base + beat * 0.5, "duration": 0.2, "velocity": 80})
    return notes

def _open_hat_punk(bars=4):
    """Punk with open hi-hat accents"""
    notes = []
    for bar in range(bars):
        base = bar * 4.0
        # Kick on 1 and 3
        notes.append({"pitch": KICK, "start_time": base + 0, "duration": 0.25, "velocity": 110})
        notes.append({"pitch": KICK, "start_time": base + 2, "duration": 0.25, "velocity": 105})
        # Snare on 2 and 4
        notes.append({"pitch": SNARE, "start_time": base + 1, "duration": 0.25, "velocity": 115})
        notes.append({"pitch": SNARE, "start_time": base + 3, "duration": 0.25, "velocity": 115})
        # Closed hats with open hat on the "and" of 4
        for beat in range(7):
            notes.append({"pitch": CLOSED_HH, "start_time": base + beat * 0.5, "duration": 0.2, "velocity": 85})
        notes.append({"pitch": OPEN_HH, "start_time": base + 3.5, "duration": 0.4, "velocity": 100})
    return notes

def _build_up(bars=4):
    """Build-up pattern with accelerating snare"""
    notes = []
    for bar in range(bars):
        base = bar * 4.0
        # Kick on every quarter
        for beat in range(4):
            notes.append({"pitch": KICK, "start_time": base + beat, "duration": 0.25, "velocity": 105 + bar * 3})
        
        # Accelerating snare based on bar number
        if bar == 0:
            notes.append({"pitch": SNARE, "start_time": base + 2, "duration": 0.25, "velocity": 100})
        elif bar == 1:
            notes.append({"pitch": SNARE, "start_time": base + 1, "duration": 0.25, "velocity": 105})
            notes.append({"pitch": SNARE, "start_time": base + 3, "duration": 0.25, "velocity": 105})
        elif bar == 2:
            for beat in range(4):
                notes.append({"pitch": SNARE, "start_time": base + beat, "duration": 0.25, "velocity": 110})
        else:
            # Bar 4: 8th note snares
            for step in range(8):
                notes.append({"pitch": SNARE, "start_time": base + step * 0.5, "duration": 0.2, "velocity": 115})
        
        # Crash on last beat
        if bar == 3:
            notes.append({"pitch": CRASH, "start_time": base + 3.5, "duration": 1.0, "velocity": 120})
    return notes

if __name__ == "__main__":
    create_anamanaguchi_patterns()
