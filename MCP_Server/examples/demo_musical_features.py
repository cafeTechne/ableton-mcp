import sys
import os
import time
from unittest.mock import MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server
os.environ["ABLETON_MCP_TRACE"] = "1"

def run_demo():
    print("--- Musical Tools Live Demo ---")
    conn = server.get_ableton_connection()
    if not conn.connect():
        print("Connect to Ableton first.")
        return
    ctx = MagicMock()

    # 1. Setup Chords Track (Track 0)
    print("\n[Track 1] Chords (Harmonic Minor)...")
    try:
        # Create Track
        res_t = conn.send_command("create_midi_track", {"index": 0})
        t_idx = 0 # Assuming index 0
        conn.send_command("set_track_name", {"track_index": t_idx, "name": "Demo Chords"})
        
        # Load Auto Filter (for automation test)
        # We try to load 'Auto Filter' (Core Library).
        # We rely on previous cache having it? Or just standard name.
        # query="Auto Filter".
        print("Loading Auto Filter...")
        uri = server._resolve_uri_by_name("Auto Filter", "devices")
        if uri:
             conn.send_command("load_device", {"track_index": t_idx, "uri": uri})
        else:
             print("Auto Filter not found in cache, skipping automation setup.")

        # Generate Chords (Jazz Minor: i7-ii7dim-V7-i7)
        # Instrument: "Grand Piano"
        res_chords = server.generate_chord_progression(
            ctx, t_idx, 0, 
            key="C", scale="harmonic_minor", genre_progression="jazz_minor", 
            instrument_name="Grand Piano"
        )
        print(f"Chords: {res_chords}")
        
        # Apply Automation (filter sweep)
        # Clip index 0. Parameter "Frequency".
        if uri:
            print("Applying Filter Automation...")
            res_auto = server.apply_automation(
                ctx, t_idx, 0, 
                parameter_name="Frequency", 
                start_val=200.0, end_val=2000.0, 
                duration_bars=4
            )
            print(f"Automation: {res_auto}")

    except Exception as e:
        print(f"Chords Error: {e}")

    # 2. Setup Bass Track (Track 1)
    print("\n[Track 2] Bassline (Pulse)...")
    try:
        conn.send_command("create_midi_track", {"index": 1})
        t_idx_b = 1
        conn.send_command("set_track_name", {"track_index": t_idx_b, "name": "Demo Bass"})
        
        # Bassline
        res_bass = server.generate_bassline(
            ctx, t_idx_b, 0, 
            key="C", scale="harmonic_minor", genre_progression="jazz_minor", 
            style="pulse", instrument_name="Bass-Hip-Hop Sub"
        )
        print(f"Bass: {res_bass}")
        
    except Exception as e:
        print(f"Bass Error: {e}")
        
    print("\n--- Demo Complete. Press Play in Live! ---")

if __name__ == "__main__":
    run_demo()
