import sys
import os
import time
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server
os.environ["ABLETON_MCP_TRACE"] = "1"

def prove_jazz():
    print("--- 🎷 Proving Jazz Changes 🎷 ---")
    conn = server.get_ableton_connection()
    if not conn.connect():
        print("❌ Connect to Ableton first.")
        return
    ctx = MagicMock()

    # 1. Create Track
    print("\n[Track] Jazz Verification...")
    res_t = conn.send_command("create_midi_track", {"index": 0})
    t_idx = 0
    conn.send_command("set_track_name", {"track_index": t_idx, "name": "Jazz Verify"})
    
    # 2. Generate Jazz Minor (C harmonic minor)
    # i7 = C Eb G B (B is natural in Harm Min? No C Harm Min: C D Eb F G Ab B. 7th is Bb? No.
    # i7 in Minor usually implies Cmin7 (C Eb G Bb).
    # But C Harm Min has B natural. So i(maj7)? 
    # My logic: i = index 0. 0,2,4,6.
    # Scale[6] = B. So C-Eb-G-B (CmM7 - Minor Major 7). Correct for Jazz Minor.
    # ii7dim (Half-dim or Dim): D F Ab B? No.
    # ii=D. ii7. Index 1. 1,3,5,0. D F Ab C? 
    # Scale[1]=D. Scale[3]=F. Scale[5]=Ab. Scale[0]=C. -> Dm7b5 (Half Dim).
    # V7: G B D F.
    
    # We do NOT request instrument_name to isolate the chord logic check.
    res_chords = server.generate_chord_progression(
        ctx, t_idx, 0, 
        key="C", scale="harmonic_minor", genre_progression="jazz_minor"
    )
    print(f"Generated: {res_chords}")
    
    # 3. Inspect Notes
    print("   🔍 Reading Clip Notes from Live...")
    try:
        notes = conn.send_command("get_clip_notes", {"track_index": t_idx, "clip_index": 0})
        # Note dict: {pitch, start_time, duration...}
        # Group by Bar (start_time // 4.0)
        bars = {}
        for n in notes:
            bar_idx = int(n["start_time"] // 4.0)
            if bar_idx not in bars: bars[bar_idx] = [] # list of pitches
            bars[bar_idx].append(int(n["pitch"]))
            
        # Sort for display
        for b in bars:
            bars[b].sort()
            
        print(f"\n   📊 Analysis:")
        print(f"   Bar 0 (i7)     : {bars.get(0, [])}")
        print(f"   Bar 1 (ii7dim) : {bars.get(1, [])}")
        print(f"   Bar 2 (V7)     : {bars.get(2, [])}")
        print(f"   Bar 3 (i7)     : {bars.get(3, [])}")
        
        # Check differences
        if bars.get(0) != bars.get(1) and bars.get(1) != bars.get(2):
            print("\n   ✅ SUCCESS: Chords are changing!")
        else:
            print("\n   ❌ FAILURE: Chords are identical/repeating.")
            
        # 4. Bassline Verification
        print("\n[Track 2] Bassline Verification...")
        conn.send_command("create_midi_track", {"index": 1})
        t_idx_b = 1
        conn.send_command("set_track_name", {"track_index": t_idx_b, "name": "Jazz Bass"})
        
        # Bassline
        res_bass = server.generate_bassline(
            ctx, t_idx_b, 0, 
            key="C", scale="harmonic_minor", genre_progression="jazz_minor", 
            style="pulse"
        )
        print(f"Generated Bass: {res_bass}")
        
    except Exception as e:
        print(f"Error inspecting notes: {e}")

if __name__ == "__main__":
    prove_jazz()
