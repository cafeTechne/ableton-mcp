"""
Debug Notes Structure
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

# Scene 1, Track 1 (Hand Perc) - should have notes
resp = conn.send_command("get_notes", {"track_index": 1, "clip_index": 1})
notes = resp.get("notes", [])
print(f"Count: {len(notes)}")
if notes:
    print(f"Type: {type(notes[0])}")
    print(f"First Note: {notes[0]}")
    
