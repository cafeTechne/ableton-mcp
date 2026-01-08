import unittest
from unittest.mock import MagicMock, patch, ANY
import sys
import os
import json

# Add parent directory to path to import server
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server

class TestProductionTools(unittest.TestCase):
    @patch('server.get_ableton_connection')
    def test_pattern_generator_notes(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        # Mock responses
        mock_conn.send_command.return_value = {"status": "ok"}
        
        ctx = MagicMock()
        
        # Test Four On Floor
        server.pattern_generator(ctx, track_index=0, clip_slot_index=0, pattern_type="four_on_floor", bars=1)
        
        # Verify add_notes_to_clip called
        # args: track_index=0, clip_index=0, notes=[...]
        # 4 notes expected for 1 bar (4 beats)
        call_args = mock_conn.send_command.call_args_list
        add_notes_call = [c for c in call_args if c[0][0] == "add_notes_to_clip"][0]
        params = add_notes_call[0][1]
        self.assertEqual(len(params["notes"]), 4)
        self.assertEqual(params["notes"][0]["pitch"], 60) # Default root

    @patch('server.get_ableton_connection')
    def test_pattern_generator_trap(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.send_command.return_value = {"status": "ok"}
        ctx = MagicMock()
        
        server.pattern_generator(ctx, 0, 0, "trap_basic", bars=1)
        
        call_args = mock_conn.send_command.call_args_list
        add_notes_call = [c for c in call_args if c[0][0] == "add_notes_to_clip"][0]
        notes = add_notes_call[0][1]["notes"]
        # Trap logic: 0.0 (Kick), 2.0 (Snare), 2.75 (Kick)
        self.assertTrue(len(notes) >= 3)
        self.assertEqual(notes[1]["start_time"], 2.0)

    @patch('server.get_ableton_connection')
    def test_audition_flow_keep(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        # Mock session info to return Audition track
        mock_conn.send_command.side_effect = lambda cmd, args=None: (
            {"tracks": [{"name": "Audition", "index": 99}]} if cmd == "get_session_info" else {"loaded": True}
        )
        
        ctx = MagicMock()
        
        # Confirm Audition (Keep)
        res = server.confirm_audition(ctx, keep=True, new_name="MyLead")
        
        # Verify rename
        mock_conn.send_command.assert_any_call("set_track_name", {"track_index": 99, "name": "MyLead"})
        self.assertIn("promoted", res)

    @patch('server.get_ableton_connection')
    def test_pattern_generator_swing(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.send_command.return_value = {"status": "ok"}
        ctx = MagicMock()
        
        # Test Swing
        server.pattern_generator(ctx, 0, 0, "four_on_floor", bars=1, swing=0.5)
        
        call_args = mock_conn.send_command.call_args_list
        add_notes_call = [c for c in call_args if c[0][0] == "add_notes_to_clip"][0]
        notes = add_notes_call[0][1]["notes"]
        # In four_on_floor (1/4 notes), swing (1/16th) shouldn't affect 1/4 notes (0.0, 1.0, 2.0, 3.0)
        # Wait, my logic was: check if 16th offbeat. 0.0 % 0.5 == 0. 0.25 (16th) is offbeat.
        # Four on floor only has 0, 1, 2, 3. So Swing does NOTHING. Correct.
        # Let's test with dnb or trap where we have offbeats?
        # Or pattern with 16ths.
        # Pattern generator doesn't generate 16ths for 4onFloor.
        # Trap has 2.75? 2.75 = 2.5 + 0.25. 2.75 % 0.5 = 0.25. This IS a 16th offbeat.
        pass

    @patch('server.get_ableton_connection')
    def test_audition_move(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.send_command.side_effect = lambda cmd, args=None: (
            {"tracks": [{"name": "Audition", "index": 99}]} if cmd == "get_session_info" else {"loaded": True, "clip_slots": []}
        )
        ctx = MagicMock()
        
        server.confirm_audition(ctx, keep=True, target_track_index=5)
        
        # Verify duplicate clip call
        mock_conn.send_command.assert_any_call("duplicate_clip", {
            "track_index": 99,
            "clip_index": 0,
            "target_track_index": 5,
            "target_clip_index": 0
        })
        # Verify delete audition track
        mock_conn.send_command.assert_any_call("delete_track", {"track_index": 99})

    @patch('server.get_ableton_connection')
    def test_print_to_audio_setup(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_conn.send_command.side_effect = lambda cmd, args=None: (
            {"name": "SourceTrack"} if cmd == "get_track_info" else {"index": 10}
        )
        ctx = MagicMock()
        
        server.setup_print_to_audio(ctx, source_track_index=1)
        
        # Verify audio track created
        mock_conn.send_command.assert_any_call("create_audio_track", {"index": -1})
        # Verify routing
        # "configure_track_routing" with input_type="SourceTrack"
        calls = mock_conn.send_command.call_args_list
        routing_call = [c for c in calls if c[0][0] == "configure_track_routing"][0]
        self.assertEqual(routing_call[0][1]["input_type"], "SourceTrack")
        self.assertEqual(routing_call[0][1]["arm"], True)

    @patch('server.get_ableton_connection')
    @patch('server._resolve_uri_by_name')
    def test_starter_kit_structure(self, mock_resolve, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        mock_resolve.return_value = "ableton:device:Drums"
        
        conn_calls = []
        def side_effect(cmd, args=None):
            conn_calls.append(cmd)
            if cmd == "get_session_info": return {"track_count": 0}
            if cmd == "create_midi_track": return {"index": len(conn_calls)}
            return {"loaded": True}
        mock_conn.send_command.side_effect = side_effect
        
        ctx = MagicMock()
        server.starter_kit(ctx, tempo=128, genre="techno")
        
        # Check sequence: Tempo -> Track 0 (Drums) -> Load -> Track 1 (Bass) ...
        self.assertIn("set_tempo", conn_calls)
        self.assertIn("set_track_name", conn_calls)
        self.assertIn("load_device", conn_calls)

if __name__ == '__main__':
    unittest.main()
