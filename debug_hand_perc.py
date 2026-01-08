"""
Debug Hand Perc (Track 1)
User reports gray meter, only audible when soloed.
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

TRK_IDX = 1

print(f"=== DEBUGGING TRACK {TRK_IDX} (Hand Perc) ===")

info = conn.send_command("get_track_info", {"track_index": TRK_IDX})
print(f"Name: {info.get('name')}")
print(f"Mute: {info.get('mute')} (True = Muted/Off)")
print(f"Solo: {info.get('solo')}")
print(f"Volume: {info.get('volume')}")
print(f"Arm: {info.get('arm')}")

# Routing Info (if available in get_track_info keys)
# output_routing_type, output_routing_channel
# If not, try get_track_routing command if exists?
# The keys list in Step 3251 showed: 'routing'.
print(f"Routing: {info.get('routing')}")

print("\nDone.")
