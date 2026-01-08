
import logging
import json
from mcp_tooling.macros import get_rack_macros, set_rack_macro

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_macros")

def test_macros():
    track_index = 0
    device_index = 0
    
    print("\n--- Testing Macro Tools ---")

    # 1. Test get_rack_macros
    print(f"\n1. Getting macros for Track {track_index}, Device {device_index}...")
    macros = get_rack_macros(track_index, device_index)
    print(f"Result ({len(macros)} macros found):")
    for m in macros[:4]: # Print first few
        print(f"  - {m}")

    if not macros:
        print("NOTE: No macros found. Ensure a device is on Track 0.")
        return

    # 2. Test set_rack_macro
    target_macro = 1
    target_value = 0.55
    print(f"\n2. Setting Macro {target_macro} to {target_value}...")
    success = set_rack_macro(track_index, device_index, target_macro, target_value)
    if success:
        print("SUCCESS: Macro set command sent.")
    else:
        print("FAILED: Could not set macro.")

if __name__ == "__main__":
    test_macros()
