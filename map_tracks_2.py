"""
Map Tracks 2 - Post Deletion
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

tracks = {}
for i in range(20):
    try:
        info = conn.send_command("get_track_info", {"track_index": i})
        if info.get("status") == "error":
            break
        name = info.get("name")
        tracks[name] = i
        print(f"Track {i}: {name}")
    except:
        break

# Check Scenes
# song = conn.send_command("get_song_context") # broken?
# Just rely on indices for scenes. We know we have 4 (0-3).
