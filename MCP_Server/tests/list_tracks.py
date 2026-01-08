
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

def list_tracks():
    conn = get_ableton_connection()
    print("📋 Listing Session Tracks:")
    for i in range(50):
        try:
            info = conn.send_command("get_track_info", {"track_index": i})
            name = info.get("name", "Unknown")
            print(f"{i}: {name}")
        except Exception as e:
            # If we hit an error (likely index out of range), we stop
            if "out of range" in str(e).lower():
                break
            # print(f"{i}: [Error] {str(e)}")

if __name__ == "__main__":
    list_tracks()
