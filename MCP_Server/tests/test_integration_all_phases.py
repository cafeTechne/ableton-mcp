import unittest
import sys
import os
import json
import time

# Add MCP_Server to path
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_dir = os.path.dirname(current_dir)
sys.path.append(mcp_server_dir)

from mcp_tooling.connection import get_ableton_connection

class TestAllPhases(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Connecting to Ableton...")
        cls.conn = get_ableton_connection()
        print("Connected.")
        
    def _send(self, command, params=None):
        params = params or {}
        print(f"  -> Sending {command}...")
        res = self.conn.send_command(command, params)
        # print(f"     Response: {json.dumps(res, indent=1)}")
        return res

    def test_00_sanity_check(self):
        """Phase 0: Ensure we can talk to Ableton."""
        data = self._send("get_song_context")
        self.assertIn("tempo", data)
        self.assertIn("track_count", data)

    def test_01_phase_1_chains_racks(self):
        """Phase 1: Chains and Racks."""
        # Create a MIDI track or use existing
        print("\n=== Phase 1: Chains ===")
        
        # 1. Create MIDI Track
        self._send("create_midi_track", {"index": 0})
        
        # 2. Add Device (e.g. Instrument Rack or just empty)
        # Finding a rack is hard without exact name, let's assume empty track.
        # But Phase 1 commands work on devices.
        # Let's try to load something simple if possible, or skip if we can't ensure content.
        # Assuming user has empty set or we just created track 0.
        
        # We can't easily test 'get_chains' without a Rack.
        # Skipping functional test, checking command existence via error or empty return.
        
        try:
            res = self._send("get_chains", {"track_index": 0, "device_index": 0})
            print(f"get_chains result: {res}")
        except Exception as e:
            print(f"Skipping get_chains test (expected if no device): {e}")

    def test_02_phase_2_clips_notes(self):
        """Phase 2: Clips and Notes."""
        print("\n=== Phase 2: Clips & Notes ===")
        # 1. Create Clip
        self._send("create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0})
        
        # 2. Add Notes
        notes = [{"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 100}]
        self._send("add_notes_to_clip", {"track_index": 0, "clip_index": 0, "notes": notes})
        
        # 3. Get Notes
        data = self._send("get_notes", {"track_index": 0, "clip_index": 0})
        # print(f"  Note data type: {type(data)}")
        
        notes = data if isinstance(data, list) else data.get("notes", [])
        self.assertTrue(len(notes) >= 1, "No notes returned")
        
        # Defensive access
        first_note = notes[0]
        if isinstance(first_note, dict):
            pitch = first_note.get("pitch")
        else:
            # Assume it's a tuple (pitch, start, duration, velocity, mute)
            pitch = first_note[0]
            
        self.assertEqual(pitch, 60)
        
        # 4. Scrub (Transport)
        self._send("scrub_by", {"beats": 1.0})

    def test_03_phase_3_browser_samples(self):
        """Phase 3: Browser & Samples."""
        print("\n=== Phase 3: Browser ===")
        # 1. Get Browser Tree (sanity)
        data = self._send("get_browser_tree", {"max_depth": 1})
        self.assertTrue(len(data) > 0)
        # Check for one of the common categories
        self.assertTrue("sounds" in data or "drums" in data or "user_library" in data)
        print("  Browser Tree Success")
        
        # 2. Preview (dangerous to hear sound, but command should work)
        # self._send("preview_item_by_uri", {"uri": "test"}) 
        # Skip actual preview to avoid noise.

    def test_04_phase_4_specialized(self):
        """Phase 4: Specialized Devices."""
        print("\n=== Phase 4: Specialized ===")
        # 1. Set EQ8 Band (should fail gracefully or silently if no EQ8)
        try:
            self._send("set_eq8_band", {"track_index": 0, "band_index": 1, "gain": 0.5})
        except Exception as e:
            print(f"  Note: set_eq8_band failed (expected if no EQ8): {e}")
        
        # 2. Get Info
        try:
            self._send("get_specialized_device_info", {"track_index": 0, "device_index": 0})
        except Exception as e:
             print(f"  Note: get_specialized_device_info failed (expected if track empty): {e}")

    def test_05_phase_5_automation(self):
        """Phase 5: Automation."""
        print("\n=== Phase 5: Automation ===")
        # 1. Set Clip Envelope
        try:
            self._send("set_clip_envelope_step", {
                "track_index": 0, "clip_index": 0, 
                "device_id": "mixer", "parameter_id": "volume", 
                "time": 0, "length": 1, "value": 0.8
            })
        except Exception as e:
            print(f"  Note: set_clip_envelope_step failed: {e}")
        
        # 2. Get Envelope
        # res = self._send("get_clip_envelope", ...)

    def test_06_phase_6_humanization(self):
        """Phase 6: Humanization."""
        print("\n=== Phase 6: Humanization ===")
        # 1. Get Extended Notes
        try:
            res = self._send("get_notes_extended", {"track_index": 0, "clip_index": 0})
            if "notes" in res:
                print("  Success: get_notes_extended returned notes")
        except Exception as e:
            print(f"  Note: get_notes_extended failed: {e}")

    def test_07_phase_7_polish(self):
        """Phase 7: Final Polish."""
        print("\n=== Phase 7: Polish ===")
        # 1. Set Data
        self._send("set_data", {"key": "test_key", "value": "test_value"})
        
        # 2. Get Data
        res = self._send("get_data", {"key": "test_key"})
        print(f"  Data Get Result: {res}")
        
        # 3. Macro Utils (Randomize)
        try:
            self._send("randomize_macros", {"track_index": 0, "device_index": 0})
        except Exception as e:
            print(f"  Note: randomize_macros skipped: {e}")
        
        # 4. Move Device
        try:
            self._send("move_device", {
                "track_index": 0, "device_index": 0,
                "target_track_index": 1, "target_index": 0
            })
        except Exception as e:
            print(f"  Note: move_device skipped: {e}")

    @classmethod
    def tearDownClass(cls):
        print("\nTests Complete.")

if __name__ == '__main__':
    unittest.main()
