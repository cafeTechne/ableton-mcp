import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import json

# Ensure we can import server and mcp_tooling
# Append MCP_Server directory to path
current_dir = os.path.dirname(os.path.abspath(__file__)) # MCP_Server/tests
mcp_server_dir = os.path.dirname(current_dir) # MCP_Server
sys.path.append(mcp_server_dir)
# Append MCP_Server directory to path
current_dir = os.path.dirname(os.path.abspath(__file__)) # MCP_Server/tests
mcp_server_dir = os.path.dirname(current_dir) # MCP_Server
sys.path.append(mcp_server_dir)

# Import tooling directly to test logic, bypassing FastMCP decorators
from mcp_tooling import devices, util

class TestServerRefactor(unittest.TestCase):
    @patch('mcp_tooling.devices.get_ableton_connection')
    def test_load_simpler_with_sample(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        def side_effect(cmd, args=None):
            if cmd == "get_track_info":
                return {"devices": [{"name": "Simpler", "class_name": "OriginalSimpler", "index": 0}]}
            if cmd == "get_browser_items_at_path":
                if args and args.get("path") == "Samples":
                    return {"items": [
                        {"name": "Kick 707", "is_loadable": True, "uri": "query:Samples#Kick 707"},
                        {"name": "Snare", "is_loadable": True, "uri": "query:Samples#Snare"}
                    ]}
                return {"items": []}
            if cmd == "hotswap_browser_item":
                return {"hotswapped": True, "item_name": "Kick 707"}
            if cmd == "load_device":
                return {"loaded": True}
            if cmd == "search_loadable_devices": # resolve_uri_by_name calls this
                return {"items": [{"name": "Simpler", "uri": "query:Simpler"}]}
            return {}

        mock_conn.send_command.side_effect = side_effect
        
        mock_conn.send_command.side_effect = side_effect
        
        ctx = MagicMock()
        result = devices.load_simpler_with_sample_logic(track_index=0, file_path="Kick 707")
        
        self.assertIn("Loaded sample into Simpler", result)

    @patch('mcp_tooling.devices.get_ableton_connection')
    def test_load_sampler_resolution(self, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        state = {"devices": []}

        def side_effect(cmd, args=None):
            if cmd == "get_track_info":
                return {"devices": state["devices"]}
            if cmd == "load_device":
                state["devices"] = [{"name": "Sampler", "class_name": "MultiSampler", "index": 0}]
                return {"loaded": True, "new_devices": ["Sampler"]}
            if cmd == "get_browser_items_at_path":
                 return {"items": [{"name": "Bass.wav", "is_loadable": True, "uri": "query:Samples#Bass.wav"}]}
            if cmd == "hotswap_browser_item":
                return {"hotswapped": True, "item_name": "Bass.wav"}
            if cmd == "search_loadable_devices":
                 return {"items": [{"name": "Sampler", "uri": "query:Instruments#Sampler", "is_loadable": True}]}
            return {}

        mock_conn.send_command.side_effect = side_effect

        ctx = MagicMock()
        result = devices.load_sampler_with_sample_logic(track_index=1, file_path="Bass.wav")
        self.assertIn("Loaded sample into Sampler", result)

    @patch('mcp_tooling.devices.get_ableton_connection')
    @patch('mcp_tooling.devices._resolve_sample_uri_by_name')
    def test_resolve_variant_stem(self, mock_resolve_name, mock_get_conn):
        mock_conn = MagicMock()
        mock_get_conn.return_value = mock_conn
        
        def side_effect_full(cmd, args=None):
             if cmd == "get_track_info": 
                 return {"devices": [{"name": "Simpler", "class_name": "OriginalSimpler", "index": 0}]}
             if cmd == "load_device": return {"loaded": True}
             if cmd == "hotswap_browser_item": return {"hotswapped": True, "item_name": "Kick.wav"}
             # Resolve Simpler uri
             if cmd == "search_loadable_devices": return {"items": [{"name": "Simpler", "uri": "uri:Simpler"}]}
             return {}
             
        mock_conn.send_command.side_effect = side_effect_full
        
        def side_effect_resolve(name, **kwargs):
            if name == "kick":
                return {"uri": "ableton:samples:Kick", "name": "Kick.wav"}
            return None
        mock_resolve_name.side_effect = side_effect_resolve
        
        ctx = MagicMock()
        # "Kick_128bpm" -> _clean_stem_variants -> "kick"
        result = devices.load_simpler_with_sample_logic(track_index=0, file_path="C:/Samples/Kick_128bpm.wav")
        
        self.assertIn("Loaded sample into Simpler", result)
        calls = mock_resolve_name.call_args_list
        found_kick = any(c[0] and c[0][0] == "kick" for c in calls)
        self.assertTrue(found_kick, f"Did not resolve 'kick'. Calls: {calls}")

    def test_trace_logging_default_off(self):
        with patch.dict(os.environ, {}, clear=True):
             pass
        with patch.dict(os.environ):
             if "ABLETON_MCP_TRACE" in os.environ:
                 del os.environ["ABLETON_MCP_TRACE"]
             # Checking util.setup_trace_logger
             logger = util.setup_trace_logger()
             self.assertIsNone(logger)

    @patch('mcp_tooling.devices.resolve_uri_by_name')
    @patch('mcp_tooling.util.search_cache') # Used by plan_load_device sample check? No, plan_load_device uses explicit cache read or resolve.
    # Actually plan_load_device_logic in devices.py reads SAMPLE_CACHE_FILE directly?
    def test_plan_load_device(self, mock_search_cache, mock_resolve_uri):
        ctx = MagicMock()
        
        # 1. Device Success
        mock_resolve_uri.return_value = "ableton:device:Simpler"
        res_json = devices.plan_load_device_logic(query="Simpler")
        res = json.loads(res_json)
        self.assertEqual(res["resolved_device_uri"], "ableton:device:Simpler")
        self.assertTrue(res["found"])
        
        # 2. Sample Search (Offline)
        mock_resolve_uri.return_value = None
        res_json = devices.plan_load_device_logic(query="NonExistent")
        res = json.loads(res_json)
        self.assertFalse(res["found"])

if __name__ == '__main__':
    unittest.main()
