
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

def test_tracks():
    conn = get_ableton_connection()
    for i in [4, 6, 11, 14, 15, 17, 20, 22]:
        try:
            name = conn.send_command("get_track_info", {"track_index": i}).get("name")
            try:
                # Delete existing clip in slot 2 (scene 3) to be safe
                try: conn.send_command("delete_clip", {"track_index": i, "clip_index": 2})
                except: pass
                
                conn.send_command("create_clip", {"track_index": i, "clip_index": 2, "length": 1.0})
                print(f"{i}: {name} - OK")
                # conn.send_command("delete_clip", {"track_index": i, "clip_index": 2})
            except Exception as e:
                print(f"{i}: {name} - FAILED: {str(e)}")
        except Exception as e:
            print(f"{i}: INFO FAILED: {str(e)}")

if __name__ == "__main__":
    test_tracks()
