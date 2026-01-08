"""
Debug Track 2 (Kick)
Investigate why volume is not playing.
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

TRK_IDX = 2

print(f"=== DEBUGGING TRACK {TRK_IDX} ===")

# 1. Track Status (Mute, Solo, Volume)
try:
    info = conn.send_command("get_track_info", {"track_index": TRK_IDX})
    print(f"Name: {info.get('name')}")
    print(f"Mute: {info.get('mute')}")
    print(f"Solo: {info.get('solo')}")
    print(f"Volume: {info.get('volume')}") 
    # Note: 'volume' might be 0.0-1.0 or dB depending on API.
except Exception as e:
    print(f"Track Info Error: {e}")

# 2. Device Status (Is instrument loaded?)
try:
    # 'get_track_devices' or similiar?
    # Interface.py map?
    # No direct 'get_devices'. But 'get_track_info' might return devices?
    # Or 'list_devices'?
    # Let's try to get simplified device list if possible.
    pass
except Exception as e:
    print(f"Device Info Error: {e}")

# 3. Clip Status (Are there notes?)
# Check Scene 1 (Drop)
SCENE_IDX = 1
try:
    resp = conn.send_command("get_notes", {"track_index": TRK_IDX, "clip_index": SCENE_IDX})
    notes = resp.get("notes", [])
    print(f"\nScene {SCENE_IDX} Clip Notes: {len(notes)}")
    if notes:
        print(f"First Note: {notes[0]}")
except Exception as e:
    print(f"Clip Info Error: {e}")
    
# 4. Check Volume Parameter specifically
# get_track_volume command?
try:
    vol = conn.send_command("get_track_volume", {"track_index": TRK_IDX})
    print(f"Volume (Specific): {vol}")
except: pass

# 5. Global Solo Check
try:
    print("\n--- Global Solo Check ---")
    any_solo = False
    for i in range(20):
        try:
            t_info = conn.send_command("get_track_info", {"track_index": i})
            if t_info.get("status") == "error": break
            if t_info.get("solo"):
                print(f"TRACK {i} ({t_info.get('name')}) IS SOLOED!")
                any_solo = True
        except: break
    if not any_solo:
        print("No tracks are soloed.")
except: pass

# 6. Device Count Check
try:
    print("\n--- Device Check ---")
    # Try getting device parameter to see if device exists?
    # Or just try loading if missing?
    # I'll try list_devices logic (from server.py tool but direct)
    # Actually, server.py uses `search_cache` or `send_command("search_loadable_devices")`.
    # I want `get_track_devices`.
    # Let's try `get_track_info` again, maybe it has device count?
    # Inspecting output from Step 3245... it didn't print raw info.
    # Let's print raw info keys.
    info = conn.send_command("get_track_info", {"track_index": TRK_IDX})
    print(f"Devices: {info.get('devices')}")
except: pass

print("\nDone.")
