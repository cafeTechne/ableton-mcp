
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

def run_diagnostics():
    conn = get_ableton_connection()
    for i in range(4, 25):
        try:
            info = conn.send_command("get_track_info", {"track_index": i})
            name = info.get("name")
            is_midi = info.get("is_midi_track")
            
            # Try to create a clip in a slot
            TEST_SLOT = 2
            status = "FAIL"
            try:
                # Delete first if already there
                conn.send_command("delete_clip", {"track_index": i, "clip_index": TEST_SLOT})
            except: pass
            
            try:
                conn.send_command("create_clip", {"track_index": i, "clip_index": TEST_SLOT, "length": 1.0})
                status = "OK"
                # Clean up
                conn.send_command("delete_clip", {"track_index": i, "clip_index": TEST_SLOT})
            except Exception as e:
                status = f"ERR: {str(e)}"
            
            print(f"{i}: {name} | is_midi_track={is_midi} | Test Clip: {status}")
        except Exception as e:
            print(f"{i}: ERROR: {str(e)}")

if __name__ == "__main__":
    run_diagnostics()
