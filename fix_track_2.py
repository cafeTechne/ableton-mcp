"""
Fix Track 2 Volume (Load Valid Instrument)
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.devices import search_and_load_device
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

TRACK_IDX = 2

print(f"=== FIXING TRACK {TRACK_IDX} (Kick) ===")

# Load specific verified preset
target_name = "Low Dirty Kick"
print(f"Searching and loading '{target_name}'...")
result = search_and_load_device(TRACK_IDX, query=target_name, category="instruments")

print(f"Result: {result}")

