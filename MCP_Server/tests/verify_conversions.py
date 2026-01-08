
import logging
from mcp_tooling.connection import get_ableton_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_conversions")

def test_conversions():
    ableton = get_ableton_connection()
    track_index = 0 # Default test track
    
    print("\n--- Testing Conversion Tools ---")

    # 1. Test move_devices_to_drum_rack (Group Devices)
    # This is safe to try even if it fails due to no devices, as long as command exists.
    print("\n1. Testing 'move_devices_to_drum_rack'...")
    try:
        res = ableton.send_command("move_devices_to_drum_rack", {"track_index": track_index})
        print(f"Result: {res}")
    except Exception as e:
        print(f"FAILED: {e}")

    # 2. Test create_drum_rack_from_audio_clip
    print("\n2. Testing 'create_drum_rack_from_audio_clip'...")
    try:
        res = ableton.send_command("create_drum_rack_from_audio_clip", {"track_index": track_index, "clip_index": 0})
        print(f"Result: {res}")
    except Exception as e:
        print(f"FAILED: {e}")

    # 3. Test sliced_simpler_to_drum_rack
    print("\n3. Testing 'sliced_simpler_to_drum_rack'...")
    try:
        # We pass device_index=-1 to search for first simpler
        res = ableton.send_command("create_drum_rack_from_slices", {"track_index": track_index, "device_index": -1})
        print(f"Result: {res}")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_conversions()
