
import sys
import os
import json
import logging

sys.path.append(os.getcwd())
from mcp_tooling.connection import AbletonConnection

# Disable logging to stderr/stdout to clean up output
logging.getLogger("mcp_server").setLevel(logging.CRITICAL)

def verify_api_expansion():
    print("VERIFICATION START")
    
    conn = AbletonConnection()
    try:
        if not conn.connect():
            print("CONNECT FAIL")
            return
        print("CONNECT OK")
        
        tests = [
            ("Song", "get_metronome", {}),
            ("Mixer", "get_master_info", {}),
            ("App", "get_live_version", {}),
            ("Scene", "get_scene_overview", {}),
            ("Group", "get_all_groups", {}),
            ("Browser", "get_browser_state", {}),
            ("ClipSlot", "get_track_slots", {"track_index": 0})
        ]
        
        for name, cmd, params in tests:
            try:
                # We won't use conn.send_command because it logs. 
                # Let's just use the connection directly or use send_command but ignore logs?
                # The logger is configured in the module, so my earlier setLevel should work.
                res = conn.send_command(cmd, params)
                print(f"PASS {name}")
            except Exception as e:
                print(f"FAIL {name}: {e}")
                
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_api_expansion()
