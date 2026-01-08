
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

def full_diag():
    conn = get_ableton_connection()
    print("FULL MIDI COMPATIBILITY DIAGNOSTIC")
    for i in range(4, 26):
        try:
            info = conn.send_command("get_track_info", {"track_index": i})
            name = info.get("name")
            is_midi = info.get("is_midi_track")
            is_audio = info.get("is_audio_track")
            
            status = "N/A"
            try:
                # Try slot 9 (Scene 10) - likely empty
                slot = 9
                try: conn.send_command("delete_clip", {"track_index": i, "clip_index": slot})
                except: pass
                
                conn.send_command("create_clip", {"track_index": i, "clip_index": slot, "length": 1.0})
                status = "OK"
                conn.send_command("delete_clip", {"track_index": i, "clip_index": slot})
            except Exception as e:
                status = f"FAILED: {str(e)}"
            
            print(f"{i:2}: {name:20} | MIDI={is_midi} | Audio={is_audio} | Clip={status}")
        except Exception as e:
            print(f"{i:2}: [SYSTEM ERROR] {str(e)}")

if __name__ == "__main__":
    full_diag()
