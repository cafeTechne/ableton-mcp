
import sys
import os
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

def humanize_piano_only():
    print("🎹 Humanizing Piano Track Only...")
    conn = get_ableton_connection()

    # CONSTANTS
    T_PIANO = 4 # Confirmed via list_tracks
    
    # Chords
    CHORD_C = [60, 64, 67]
    CHORD_Am = [57, 60, 64]
    CHORD_F = [53, 57, 60]
    CHORD_Fm = [53, 56, 60]
    CHORD_G = [55, 59, 62]

    # Progressions
    PROG_MAIN_CHORDS = [
        (CHORD_C, 0.0, 4.0), 
        (CHORD_Am, 4.0, 4.0),
        (CHORD_F, 8.0, 4.0),
        (CHORD_G, 12.0, 4.0)
    ]
    PROG_BRIDGE_CHORDS = [
        (CHORD_F, 0.0, 4.0),
        (CHORD_Fm, 4.0, 4.0),
        (CHORD_C, 8.0, 4.0),
        (CHORD_G, 12.0, 4.0)
    ]
    LENGTH_MAIN = 16.0
    
    # GENERATOR
    def gen_piano_triplets(measure_chords):
        notes = []
        triplet_len = 1.0 / 3.0
        for chord, start, dur in measure_chords:
            ticks = int(dur * 3)
            for t in range(ticks):
                # Nominal
                base_pos = start + (t * triplet_len)
                
                # HUMANIZATION
                # Timing wobble (+/- 20ms)
                time_wobble = random.uniform(-0.02, 0.02)
                
                # Velocity Accents (Metric)
                # Accent on beat (t%3==0)
                base_vel = 80 + (15 if t%3==0 else 0)
                
                for pitch in chord:
                    # Note independent wobble
                    note_wobble = random.uniform(-0.015, 0.015) # Strumming effect
                    vel_noise = random.randint(-12, 12)
                    final_vel = max(1, min(127, base_vel + vel_noise))
                    
                    final_pos = max(0.0, base_pos + time_wobble + note_wobble)
                    # Duration variance (legato vs staccato overlap)
                    final_dur = triplet_len * 0.9 + random.uniform(-0.05, 0.05)
                    
                    notes.append((pitch, final_pos, final_dur, final_vel, False))
        return notes

    def create_clip(scene_idx, notes, length=4.0):
        try:
            conn.send_command("delete_clip", {"track_index": T_PIANO, "clip_index": scene_idx})
        except: pass
        conn.send_command("create_clip", {"track_index": T_PIANO, "clip_index": scene_idx, "length": length})
        conn.send_command("add_notes_to_clip", {"track_index": T_PIANO, "clip_index": scene_idx, "notes": notes})

    # EXECUTION
    
    # Scene 0: Intro (C Vamp)
    print("   Scene 1 (Intro)...")
    create_clip(0, gen_piano_triplets([(CHORD_C, 0.0, 4.0)]), length=4.0)

    # Scene 1: Verse (Main Prog)
    print("   Scene 2 (Verse)...")
    create_clip(1, gen_piano_triplets(PROG_MAIN_CHORDS), length=16.0)

    # Scene 2: Chorus (Main Prog)
    print("   Scene 3 (Chorus)...")
    create_clip(2, gen_piano_triplets(PROG_MAIN_CHORDS), length=16.0)

    # Scene 3: Bridge (Bridge Prog)
    print("   Scene 4 (Bridge)...")
    create_clip(3, gen_piano_triplets(PROG_BRIDGE_CHORDS), length=16.0)

    # Scene 4: Outro (C Hold)
    print("   Scene 5 (Outro)...")
    create_clip(4, gen_piano_triplets([(CHORD_C, 0.0, 4.0)]), length=4.0)
    
    print("\n✅ Piano Track Humanized!")

if __name__ == "__main__":
    humanize_piano_only()
