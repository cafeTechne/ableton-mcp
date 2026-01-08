"""
Unmute Hand Perc
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()
TRACK_IDX = 1

print(f"Unmuting Track {TRACK_IDX}...")
# set_track_mute or similar?
# Interface.py: 'mute_track': lambda: self.handler.track_handler.set_track_mute(...)
# Command: set_track_mute(track_index, mute)
conn.send_command("set_track_mute", {"track_index": TRACK_IDX, "mute": False})

# Verify
info = conn.send_command("get_track_info", {"track_index": TRACK_IDX})
print(f"New Mute Status: {info.get('mute')}")
