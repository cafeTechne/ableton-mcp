"""
Check Devices Clean
"""
import sys
import os
import json
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()
info = conn.send_command("get_track_info", {"track_index": 2})
devs = info.get("devices", [])
print(json.dumps(devs, indent=2))
