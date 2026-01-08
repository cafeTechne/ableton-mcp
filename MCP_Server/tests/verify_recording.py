
import logging
import time
from mcp_tooling.recording import set_record_mode, trigger_session_record, capture_midi, set_overdub
from mcp_tooling.connection import get_ableton_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_recording")

def test_recording():
    print("\n--- Testing Recording Tools ---")
    
    # Check connection first
    conn = get_ableton_connection()
    if not conn:
        print("FAILED: No connection to Ableton")
        return

    # 1. Test Global Record Mode
    print("\n1. Enabling Global Record...")
    if set_record_mode(True):
        print("SUCCESS: Enabled Record Mode")
    else:
        print("FAILED: Could not enable Record Mode")
    
    time.sleep(1)
    
    print("   Disabling Global Record...")
    if set_record_mode(False):
        print("SUCCESS: Disabled Record Mode")
    else:
        print("FAILED: Could not disable Record Mode")

    # 2. Test Session Overdub
    print("\n2. Enabling Session Overdub...")
    if set_overdub(True):
        print("SUCCESS: Enabled Overdub")
    else:
        print("FAILED: Could not enable Overdub")

    time.sleep(1)
    set_overdub(False) # Cleanup

    # 3. Test Capture MIDI (might do nothing if no notes played, but command should return success status)
    print("\n3. Testing Capture MIDI...")
    if capture_midi():
        print("SUCCESS: Verified Capture MIDI command")
    else:
        print("FAILED: Capture MIDI command failed")

    # 4. Trigger Session Record
    print("\n4. Triggering Session Record...")
    if trigger_session_record():
        print("SUCCESS: Triggered Session Record")
    else:
        print("FAILED: Trigger Session Record failed")

if __name__ == "__main__":
    test_recording()
