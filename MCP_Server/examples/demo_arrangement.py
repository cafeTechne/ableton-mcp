import sys
import os
import time
from unittest.mock import MagicMock

# Append MCP_Server directory to path (current file is IN MCP_Server)
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from mcp_tooling import arrangement, connection
os.environ["ABLETON_MCP_TRACE"] = "1"

def demo_arrangement():
    print("--- 🏗️ Demo Arrangement 🏗️ ---")
    conn = connection.get_ableton_connection()
    if not conn.connect():
        print("❌ Connect to Ableton first.")
        return

    print("\n1. Generating Blueprint for 'House' in D Minor...")
    blueprint = arrangement.create_song_blueprint("house", "D", "minor")
    print(f"Blueprint JSON:\n{blueprint}")
    
    print("\n2. Constructing Song...")
    # This calls construct_song -> Calls Live -> create_midi_track, load_device (uses search), create_scene, etc.
    result = arrangement.construct_song(blueprint)
    print(f"\nConstruction Result:\n{result}")

if __name__ == "__main__":
    demo_arrangement()
