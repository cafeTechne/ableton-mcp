
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.ableton_helpers import load_sample_to_simpler

def expand_session():
    print("🚀 Expanding Session Structure...")
    conn = get_ableton_connection()
    
    tracks_to_add = [
        # Name, Type, Search Query, Category
        ("Sub Bass", "midi", "Sub Bass", "sounds"),
        ("Mid Bass", "midi", "Mid Bass", "sounds"),
        ("Bass FX", "midi", "Bass Fill", "sounds"),
        
        ("Chord Stabs", "midi", "Chord", "sounds"),
        ("Pad / Atmos", "midi", "Pad", "sounds"),
        ("Lead / Topline", "midi", "Lead", "sounds"),
        ("Arp / Pluck", "midi", "Arp", "sounds"),
        
        ("Riser Up", "audio", "Riser Up", "samples"),
        ("Riser Down", "audio", "Riser Down", "samples"),
        ("White Noise", "audio", "White Noise", "samples"),
        ("Impacts", "audio", "Impact", "samples"),
        ("Reverse FX", "audio", "Reverse", "samples"),
        ("FX Bus", "midi", None, None), # Empty for grouping
        
        ("Sidechain Trigger", "midi", None, None),
        ("Reference Track", "audio", None, None),
        ("Metering / Spectrum", "audio", "Spectrum", "audio_effects")
    ]
    
    for name, t_type, query, category in tracks_to_add:
        print(f"➕ Adding '{name}' ({t_type})...")
        if t_type == "midi":
            res = conn.send_command("create_midi_track", {"index": -1})
        else:
            res = conn.send_command("create_audio_track", {"index": -1})
        
        track_idx = res.get("index")
        conn.send_command("set_track_name", {"track_index": track_idx, "name": name})
        
        if query and category:
            if category == "samples":
                print(f"   🔍 Searching for sample: '{query}'...")
                load_sample_to_simpler(track_idx, query)
            else:
                print(f"   🔍 Searching for {category}: '{query}'...")
                # Use search_and_load_device for non-sample categories
                conn.send_command("search_and_load_device", {
                    "track_index": track_idx,
                    "query": query,
                    "category": category
                })
        
        if name == "Sidechain Trigger":
            print("   🔇 Muting Sidechain Trigger...")
            conn.send_command("set_track_mute", {"track_index": track_idx, "mute": True})
            # Add a short trigger note
            conn.send_command("create_clip", {"track_index": track_idx, "clip_index": 0, "length": 1.0})
            conn.send_command("add_notes_to_clip", {
                "track_index": track_idx, 
                "clip_index": 0, 
                "notes": [(60, 0.0, 0.1, 100, False), (60, 1.0, 0.1, 100, False)]
            })
            
        if name == "Reference Track":
             print("   🔇 Muting Reference Track...")
             conn.send_command("set_track_mute", {"track_index": track_idx, "mute": True})

    print("\n✨ Session Expanded Successfully!")

if __name__ == "__main__":
    expand_session()
