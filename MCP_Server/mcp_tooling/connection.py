import socket
import json
import logging
import time
import os
from typing import Dict, Any, Optional

logger = logging.getLogger("mcp_server")

class AbletonConnection:
    def __init__(self, host='localhost', port=9877): # Default port
        self.host = host
        self.port = port
        self.sock = None
        
    def connect(self):
        """Establish connection to Ableton"""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5.0)
            self.sock.connect((self.host, self.port))
            
            # Perform handshake
            try:
                # Wait for initial greeting
                greeting = self.sock.recv(1024).decode('utf-8')
                logger.info(f"Connected to Ableton: {greeting}")
            except socket.timeout:
                logger.warning("No greeting received from Ableton, creating new connection")
                
            return True
        except ConnectionRefusedError:
            logger.error(f"Connection refused at {self.host}:{self.port}. Is Ableton running with the Remote Script?")
            self.sock = None
            return False
        except Exception as e:
            logger.error(f"Error connecting to Ableton: {str(e)}")
            self.sock = None
            return False

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
            self.sock = None

    def receive_full_response(self, sock, timeout=None):
        """Receive full JSON response, handling fragmentation"""
        chunks = []
        depth = 0
        in_string = False
        escape = False
        started = False
        
        start_time = time.time()
        
        try:
            while True:
                # Check for overall timeout
                if timeout and (time.time() - start_time > timeout):
                    raise socket.timeout("Timed out waiting for full response")
                    
                chunk = sock.recv(4096)
                if not chunk:
                    break
                    
                chunks.append(chunk)
                text = chunk.decode('utf-8', errors='ignore')
                
                for char in text:
                    if not started:
                        if char == '{':
                            started = True
                            depth = 1
                        continue
                        
                    if escape:
                        escape = False
                        continue
                        
                    if char == '\\':
                        escape = True
                        continue
                        
                    if char == '"':
                        in_string = not in_string
                        continue
                        
                    if not in_string:
                        if char == '{':
                            depth += 1
                        elif char == '}':
                            depth -= 1
                            if depth == 0:
                                # We found the matching closing brace
                                full_data = b''.join(chunks)
                                # Find start and end exactly
                                s_idx = full_data.find(b'{')
                                # We need to be careful about finding the TRUE end.
                                # The loop logic is safest.
                                return full_data
        except socket.timeout:
            # If we have data, try to parse it anyway?
            if chunks:
                logger.warning("Socket timed out but data received, attempting parse...")
            else:
                raise
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise
            
        if chunks:
             return b''.join(chunks)
        raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Ableton and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Ableton")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        # Check if this is a state-modifying command (needs delays)
        is_modifying_command = command_type in [
            "create_midi_track", "create_audio_track", "set_track_name",
            "delete_track", "duplicate_track",
            "configure_track_routing",
            "set_track_io", "set_track_monitor", "set_track_arm", "set_track_solo",
            "set_track_mute", "set_track_volume", "set_track_panning", "set_send_level",
            "create_return_track", "delete_return_track", "set_return_track_name",
            "create_clip", "delete_clip", "duplicate_clip", "add_notes_to_clip", "set_clip_name",
            "set_clip_loop", "set_clip_length", "quantize_clip",
            "set_tempo", "set_time_signature",
            "fire_clip", "list_clips", "fire_clip_by_name", "trigger_test_midi", "stop_clip",
            "set_device_parameter", "set_device_parameters", "set_device_audio_input", "get_device_parameters",
            "start_playback", "stop_playback", "load_instrument_or_effect", "load_browser_item",
            "load_device", "set_device_sidechain_source", "save_device_snapshot",
            "apply_device_snapshot", "create_scene", "delete_scene", "duplicate_scene",
            "fire_scene", "fire_scene_by_name", "stop_scene",
            "pump_helper", "auto_test_suite", "ducking_tool", "lfo_pump_helper",
            "set_clip_envelope"
        ]
        
        try:
            logger.info(f"Sending command: {command_type} with params: {params}")
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            
            if is_modifying_command:
                time.sleep(0.1)
            
            long_ops = {"search_loadable_devices", "list_loadable_devices", "get_browser_items_at_path", "get_browser_tree"}
            long_timeout = float(os.environ.get("ABLETON_MCP_LONG_TIMEOUT", 120.0))
            
            if command_type in long_ops:
                self.sock.settimeout(long_timeout)
            else:
                self.sock.settimeout(30.0 if is_modifying_command else 12.0)
            
            response_data = self.receive_full_response(self.sock)
            response = json.loads(response_data.decode('utf-8'))
            
            if response.get("status") == "error":
                raise Exception(response.get("message", "Unknown error from Ableton"))
            
            if is_modifying_command:
                time.sleep(0.1)
            
            return response.get("result", {})
            
        except socket.timeout:
            logger.error("Socket timeout")
            self.sock = None
            raise Exception("Timeout waiting for Ableton response")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Ableton lost: {str(e)}")
        except Exception as e:
            self.sock = None
            raise e

# Singleton instance
_connection = None

def get_ableton_connection() -> AbletonConnection:
    global _connection
    if _connection is None:
        _connection = AbletonConnection()
    return _connection
