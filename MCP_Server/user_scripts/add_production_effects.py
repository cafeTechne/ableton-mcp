"""
Add Production Effects to Session

Loads EQ Eight, Compressor, Reverb etc. on tracks based on instrument type.
Uses proper track detection and API calls.
"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.devices import search_and_load_device

# Effect chains by track type (detected from name)
EFFECT_CHAINS = {
    "kick": ["EQ Eight", "Glue Compressor"],
    "snare": ["EQ Eight", "Glue Compressor"],
    "hat": ["EQ Eight"],
    "drum": ["EQ Eight", "Glue Compressor"],
    "bass": ["EQ Eight", "Compressor"],
    "piano": ["EQ Eight", "Reverb"],
    "keys": ["EQ Eight", "Reverb"],
    "vocal": ["EQ Eight", "Compressor", "Reverb"],
    "vox": ["EQ Eight", "Compressor", "Reverb"],
    "guitar": ["EQ Eight", "Amp"],
    "gtr": ["EQ Eight", "Amp"],
    "brass": ["EQ Eight", "Reverb"],
    "string": ["EQ Eight", "Reverb"],
    "wind": ["EQ Eight", "Reverb"],
    "pad": ["EQ Eight", "Reverb"],
    "synth": ["EQ Eight", "Compressor"],
    "lead": ["EQ Eight", "Delay", "Reverb"],
}

DEFAULT_CHAIN = ["EQ Eight"]

def get_effect_chain(track_name):
    """Determine effect chain from track name."""
    name_lower = track_name.lower()
    for keyword, chain in EFFECT_CHAINS.items():
        if keyword in name_lower:
            return chain
    return DEFAULT_CHAIN

def add_production_effects():
    print("🎛️ Adding Production Effects...")
    conn = get_ableton_connection()
    
    # Get all tracks
    context = conn.send_command("get_song_context", {"include_clips": False})
    tracks = context.get("tracks", [])
    
    for track in tracks:
        idx = track.get("index")
        name = track.get("name", f"Track {idx}")
        
        # Skip master/return
        if track.get("is_return_track") or track.get("is_master"):
            continue
            
        chain = get_effect_chain(name)
        print(f"\n📍 Track {idx} ({name}): {chain}")
        
        for effect in chain:
            result = search_and_load_device(idx, effect, "audio_effects")
            print(f"   + {effect}: {result}")
            time.sleep(0.5)
    
    print("\n✅ Production Effects Added!")

if __name__ == "__main__":
    add_production_effects()
