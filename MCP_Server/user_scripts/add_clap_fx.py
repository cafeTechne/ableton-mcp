
import sys
import os
import time
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

def add_clap_fx():
    print("✨ Adding Effects to Clap / Snare...")
    conn = get_ableton_connection()
    
    TRACK_IDX = 4  # Clap / Snare
    
    def load_effect(track_idx, query, category="audio_effects"):
        print(f"   📥 Searching and Loading '{query}'...")
        res = conn.send_command("search_and_load_device", {
            "track_index": track_idx,
            "query": query,
            "category": category
        })
        if res.get("loaded"):
            print(f"      ✅ Loaded '{res.get('item_name')}'")
            return True
        else:
            print(f"      ❌ Failed to load '{query}': {res.get('error')}")
            return False

    # 1. Load Reverb
    if load_effect(TRACK_IDX, "Reverb"):
        time.sleep(1.0)
        # Configure Reverb
        params = conn.send_command("get_device_parameters", {"track_index": TRACK_IDX, "device_index": 1})
        if "parameters" in params:
             for p in params["parameters"]:
                 if p["name"] == "Dry/Wet":
                     conn.send_command("set_device_parameter", {
                         "track_index": TRACK_IDX,
                         "device_index": 1,
                         "parameter_index": p["index"],
                         "value": 0.2 # 20%
                     })
                     print("      ✅ Set Reverb Dry/Wet to 20%")
                 if p["name"] == "Decay Time":
                     conn.send_command("set_device_parameter", {
                         "track_index": TRACK_IDX,
                         "device_index": 1,
                         "parameter_index": p["index"],
                         "value": 1.5 # 1.5s
                     })
                     print("      ✅ Set Reverb Decay to 1.5s")

    # 2. Load EQ Eight
    if load_effect(TRACK_IDX, "EQ Eight"):
        time.sleep(1.0)
        # Configure EQ (High Pass)
        params = conn.send_command("get_device_parameters", {"track_index": TRACK_IDX, "device_index": 2})
        if "parameters" in params:
             for p in params["parameters"]:
                 if p["name"] == "1 Filter Type A":
                     conn.send_command("set_device_parameter", {
                         "track_index": TRACK_IDX,
                         "device_index": 2,
                         "parameter_index": p["index"],
                         "value": 0 # High Pass 48dB
                     })
                     print("      ✅ Set EQ Eight Band 1 to High Pass")
                 if p["name"] == "1 Frequency A":
                     conn.send_command("set_device_parameter", {
                         "track_index": TRACK_IDX,
                         "device_index": 2,
                         "parameter_index": p["index"],
                         "value": 0.35 # ~300Hz
                     })
                     print("      ✅ Set EQ Eight Band 1 Frequency to ~300Hz")
        
    print("\n🎸 Clap / Snare FX Chain Updated!")

if __name__ == "__main__":
    add_clap_fx()
