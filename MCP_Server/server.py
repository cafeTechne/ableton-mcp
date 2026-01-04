# ableton_mcp_server.py
import json
import logging
import os
import shutil
import socket
import sys
from dataclasses import dataclass
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator, Dict, Any, List, Optional, Union

from mcp.server.fastmcp import FastMCP, Context

CACHE_DIR = Path(os.environ.get("ABLETON_MCP_CACHE_DIR", Path.cwd() / "cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "browser_devices.json"
PRESET_DIR = Path(os.environ.get("ABLETON_MCP_PRESET_DIR", Path.cwd() / "presets"))
PRESET_DIR.mkdir(parents=True, exist_ok=True)
HELPER_NAME = "SidechainHelper_Advanced.amxd"
HELPER_SOURCE = Path(__file__).resolve().parent.parent / "m4l" / HELPER_NAME

def _user_library_root() -> Path:
    """Best-effort resolve of Ableton's User Library root."""
    candidates = [
        Path.home() / "Music" / "Ableton" / "User Library",
        Path.home() / "Documents" / "Ableton" / "User Library",
        Path.cwd() / "User Library"
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return candidates[0]

def _install_sidechain_helper() -> Optional[Path]:
    """Copy the advanced sidechain helper into the User Library for loading."""
    try:
        if not HELPER_SOURCE.exists():
            return None
        target_dir = _user_library_root() / "Presets" / "Audio Effects" / "Max Audio Effect" / "AbletonMCP"
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / HELPER_SOURCE.name
        shutil.copy2(HELPER_SOURCE, target_path)
        return target_path
    except Exception as e:
        logger.warning(f"Could not install sidechain helper: {e}")
        return None

def _merge_parameter_lists(existing: Optional[List[Any]], incoming: Optional[List[Any]]) -> Optional[List[Any]]:
    """Merge two parameter lists, preserving the richest metadata available."""
    if not incoming:
        return existing
    if not existing:
        return incoming

    def _normalize(params: List[Any]) -> List[Dict[str, Any]]:
        normalized: List[Dict[str, Any]] = []
        for p in params:
            if isinstance(p, dict):
                normalized.append(dict(p))
            else:
                normalized.append({"name": str(p)})
        return normalized

    merged: Dict[str, Dict[str, Any]] = {}
    for param in _normalize(existing):
        key = str(param.get("name", "")).lower() or f"param_{len(merged)}"
        merged[key] = param
    for param in _normalize(incoming):
        key = str(param.get("name", "")).lower() or f"param_{len(merged)}"
        prior = merged.get(key, {})
        # Incoming values win when present, but keep prior data
        merged[key] = {**prior, **{k: v for k, v in param.items() if v is not None}}
    return list(merged.values())

def _update_cache_item(name: str, uri: str, category: Optional[str] = None, path: Optional[str] = None, parameters: Optional[List[Any]] = None):
    """Merge a device entry into the local cache."""
    try:
        if CACHE_FILE.exists():
            cache = json.loads(CACHE_FILE.read_text())
        else:
            cache = {"items": []}
        items = cache.get("items", [])
        # Replace or append
        updated = False
        for item in items:
            if item.get("uri") == uri:
                item["name"] = name
                if category:
                    item["category"] = category
                if path:
                    item["path"] = path
                if parameters:
                    item["parameters"] = _merge_parameter_lists(item.get("parameters"), parameters)
                updated = True
                break
        if not updated:
            entry = {"name": name, "uri": uri}
            if category:
                entry["category"] = category
            if path:
                entry["path"] = path
            if parameters:
                entry["parameters"] = parameters
            items.append(entry)
        cache["items"] = items
        CACHE_FILE.write_text(json.dumps(cache, indent=2))
    except Exception as e:
        logger.warning(f"Could not update device cache: {e}")


def _update_cache_parameters_by_name(name: str, parameters: Optional[List[Any]] = None):
    """Update cache entry parameters by matching name when URI is unknown."""
    if not parameters:
        return
    try:
        if not CACHE_FILE.exists():
            return
        cache = json.loads(CACHE_FILE.read_text())
        items = cache.get("items", [])
        for item in items:
            if item.get("name", "").lower() == name.lower():
                item["parameters"] = _merge_parameter_lists(item.get("parameters"), parameters)
                break
        cache["items"] = items
        CACHE_FILE.write_text(json.dumps(cache, indent=2))
    except Exception as e:
        logger.warning(f"Could not update device cache by name: {e}")


def _slugify(text: str) -> str:
    """Simple filesystem-safe slug generator."""
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in text.strip())
    return safe.strip("_") or "preset"


def _preset_path(name: str) -> Path:
    """Return preset file path for a given name."""
    return PRESET_DIR / f"{_slugify(name)}.json"


def setup_logging() -> Optional[Path]:
    """Configure logging to both stderr and a file in logs/."""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    handlers = [logging.StreamHandler(sys.stderr)]
    log_path: Optional[Path] = None

    try:
        # Prefer a user-configurable or CWD-based logs directory so files are easy to find.
        log_dir_env = os.environ.get("ABLETON_MCP_LOG_DIR")
        log_dir = Path(log_dir_env) if log_dir_env else (Path.cwd() / "logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / "ableton-mcp.log"
        handlers.append(logging.FileHandler(log_path, encoding="utf-8"))
    except Exception:
        # Fall back to stderr-only logging if the log file can't be created
        log_path = None

    logging.basicConfig(level=logging.INFO, format=log_format, handlers=handlers, force=True)
    return log_path


LOG_PATH = setup_logging()
logger = logging.getLogger("AbletonMCPServer")
if LOG_PATH:
    logger.info(f"File logging enabled at {LOG_PATH}")


@dataclass
class AbletonConnection:
    host: str
    port: int
    sock: socket.socket = None
    
    def connect(self) -> bool:
        """Connect to the Ableton Remote Script socket server"""
        if self.sock:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            logger.info(f"Connected to Ableton at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Ableton: {str(e)}")
            self.sock = None
            return False
    
    def disconnect(self):
        """Disconnect from the Ableton Remote Script"""
        if self.sock:
            try:
                self.sock.close()
            except Exception as e:
                logger.error(f"Error disconnecting from Ableton: {str(e)}")
            finally:
                self.sock = None

    def receive_full_response(self, sock, buffer_size=8192):
        """Receive the complete response, potentially in multiple chunks"""
        chunks = []
        sock.settimeout(15.0)  # Increased timeout for operations that might take longer
        
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise Exception("Connection closed before receiving any data")
                        break
                    
                    chunks.append(chunk)
                    
                    # Check if we've received a complete JSON object
                    try:
                        data = b''.join(chunks)
                        json.loads(data.decode('utf-8'))
                        logger.info(f"Received complete response ({len(data)} bytes)")
                        return data
                    except json.JSONDecodeError:
                        # Incomplete JSON, continue receiving
                        continue
                except socket.timeout:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error(f"Socket connection error during receive: {str(e)}")
                    raise
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise
            
        # If we get here, we either timed out or broke out of the loop
        if chunks:
            data = b''.join(chunks)
            logger.info(f"Returning data after receive completion ({len(data)} bytes)")
            try:
                json.loads(data.decode('utf-8'))
                return data
            except json.JSONDecodeError:
                raise Exception("Incomplete JSON response received")
        else:
            raise Exception("No data received")

    def send_command(self, command_type: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a command to Ableton and return the response"""
        if not self.sock and not self.connect():
            raise ConnectionError("Not connected to Ableton")
        
        command = {
            "type": command_type,
            "params": params or {}
        }
        
        # Check if this is a state-modifying command
        is_modifying_command = command_type in [
            "create_midi_track", "create_audio_track", "set_track_name",
            "delete_track", "duplicate_track",
            "set_track_io", "set_track_monitor", "set_track_arm", "set_track_solo",
            "set_track_mute", "set_track_volume", "set_track_panning", "set_send_level",
            "create_return_track", "delete_return_track", "set_return_track_name",
            "create_clip", "delete_clip", "duplicate_clip", "add_notes_to_clip", "set_clip_name",
            "set_clip_loop", "set_clip_length", "quantize_clip",
            "set_tempo", "set_time_signature",
            "fire_clip", "stop_clip", "set_device_parameter", "get_device_parameters",
            "start_playback", "stop_playback", "load_instrument_or_effect",
            "load_device", "set_device_sidechain_source", "save_device_snapshot",
            "apply_device_snapshot", "create_scene", "delete_scene", "duplicate_scene",
            "fire_scene", "stop_scene"
        ]
        
        try:
            logger.info(f"Sending command: {command_type} with params: {params}")
            
            # Send the command
            self.sock.sendall(json.dumps(command).encode('utf-8'))
            logger.info(f"Command sent, waiting for response...")
            
            # For state-modifying commands, add a small delay to give Ableton time to process
            if is_modifying_command:
                import time
                time.sleep(0.1)  # 100ms delay
            
            # Set timeout based on command type (longer for modifying/quantize)
            timeout = 30.0 if is_modifying_command else 12.0
            self.sock.settimeout(timeout)
            
            # Receive the response
            response_data = self.receive_full_response(self.sock)
            logger.info(f"Received {len(response_data)} bytes of data")
            
            # Parse the response
            response = json.loads(response_data.decode('utf-8'))
            logger.info(f"Response parsed, status: {response.get('status', 'unknown')}")
            
            if response.get("status") == "error":
                logger.error(f"Ableton error: {response.get('message')}")
                raise Exception(response.get("message", "Unknown error from Ableton"))
            
            # For state-modifying commands, add another small delay after receiving response
            if is_modifying_command:
                import time
                time.sleep(0.1)  # 100ms delay
            
            return response.get("result", {})
        except socket.timeout:
            logger.error("Socket timeout while waiting for response from Ableton")
            self.sock = None
            raise Exception("Timeout waiting for Ableton response")
        except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
            logger.error(f"Socket connection error: {str(e)}")
            self.sock = None
            raise Exception(f"Connection to Ableton lost: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response from Ableton: {str(e)}")
            if 'response_data' in locals() and response_data:
                logger.error(f"Raw response (first 200 bytes): {response_data[:200]}")
            self.sock = None
            raise Exception(f"Invalid response from Ableton: {str(e)}")
        except Exception as e:
            logger.error(f"Error communicating with Ableton: {str(e)}")
            self.sock = None
            raise Exception(f"Communication error with Ableton: {str(e)}")

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Manage server startup and shutdown lifecycle"""
    try:
        logger.info("AbletonMCP server starting up")
        
        try:
            ableton = get_ableton_connection()
            logger.info("Successfully connected to Ableton on startup")
        except Exception as e:
            logger.warning(f"Could not connect to Ableton on startup: {str(e)}")
            logger.warning("Make sure the Ableton Remote Script is running")
        
        yield {}
    finally:
        global _ableton_connection
        if _ableton_connection:
            logger.info("Disconnecting from Ableton on shutdown")
            _ableton_connection.disconnect()
            _ableton_connection = None
        logger.info("AbletonMCP server shut down")

# Create the MCP server with lifespan support
mcp = FastMCP(
    "AbletonMCP",
    instructions="Ableton Live integration through the Model Context Protocol",
    lifespan=server_lifespan
)

# Global connection for resources
_ableton_connection = None

def _connection_settings() -> tuple[str, int]:
    """Return host/port for the Ableton socket connection."""
    host = os.environ.get("ABLETON_MCP_HOST", "localhost")
    try:
        port = int(os.environ.get("ABLETON_MCP_PORT", "9877"))
    except ValueError:
        logger.warning("Invalid ABLETON_MCP_PORT value, falling back to 9877")
        port = 9877
    return host, port

def get_ableton_connection():
    """Get or create a persistent Ableton connection"""
    global _ableton_connection
    
    if _ableton_connection is not None:
        try:
            # Test the connection with a simple ping
            # We'll try to send an empty message, which should fail if the connection is dead
            # but won't affect Ableton if it's alive
            _ableton_connection.sock.settimeout(1.0)
            _ableton_connection.sock.sendall(b'')
            return _ableton_connection
        except Exception as e:
            logger.warning(f"Existing connection is no longer valid: {str(e)}")
            try:
                _ableton_connection.disconnect()
            except:
                pass
            _ableton_connection = None
    
    # Connection doesn't exist or is invalid, create a new one
    if _ableton_connection is None:
        # Try to connect up to 3 times with a short delay between attempts
        max_attempts = 3
        host, port = _connection_settings()
        for attempt in range(1, max_attempts + 1):
            try:
                logger.info(f"Connecting to Ableton at {host}:{port} (attempt {attempt}/{max_attempts})...")
                _ableton_connection = AbletonConnection(host=host, port=port)
                if _ableton_connection.connect():
                    logger.info("Created new persistent connection to Ableton")
                    
                    # Validate connection with a simple command
                    try:
                        # Get session info as a test
                        _ableton_connection.send_command("get_session_info")
                        logger.info("Connection validated successfully")
                        return _ableton_connection
                    except Exception as e:
                        logger.error(f"Connection validation failed: {str(e)}")
                        _ableton_connection.disconnect()
                        _ableton_connection = None
                        # Continue to next attempt
                else:
                    _ableton_connection = None
            except Exception as e:
                logger.error(f"Connection attempt {attempt} failed: {str(e)}")
                if _ableton_connection:
                    _ableton_connection.disconnect()
                    _ableton_connection = None
            
            # Wait before trying again, but only if we have more attempts left
            if attempt < max_attempts:
                import time
                time.sleep(1.0)
        
        # If we get here, all connection attempts failed
        if _ableton_connection is None:
            logger.error("Failed to connect to Ableton after multiple attempts")
            raise Exception("Could not connect to Ableton. Make sure the Remote Script is running.")
    
    return _ableton_connection


# Core Tool endpoints

@mcp.tool()
def get_session_info(ctx: Context) -> str:
    """Get detailed information about the current Ableton session"""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_session_info")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting session info from Ableton: {str(e)}")
        return f"Error getting session info: {str(e)}"

@mcp.tool()
def get_track_info(ctx: Context, track_index: int) -> str:
    """
    Get detailed information about a specific track in Ableton.
    
    Parameters:
    - track_index: The index of the track to get information about
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_track_info", {"track_index": track_index})
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting track info from Ableton: {str(e)}")
        return f"Error getting track info: {str(e)}"

@mcp.tool()
def create_midi_track(ctx: Context, index: int = -1) -> str:
    """
    Create a new MIDI track in the Ableton session.
    
    Parameters:
    - index: The index to insert the track at (-1 = end of list)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_midi_track", {"index": index})
        return f"Created new MIDI track: {result.get('name', 'unknown')}"
    except Exception as e:
        logger.error(f"Error creating MIDI track: {str(e)}")
        return f"Error creating MIDI track: {str(e)}"


@mcp.tool()
def create_audio_track(ctx: Context, index: int = -1) -> str:
    """Create a new audio track."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_audio_track", {"index": index})
        return f"Created new audio track: {result.get('name', 'unknown')}"
    except Exception as e:
        logger.error(f"Error creating audio track: {str(e)}")
        return f"Error creating audio track: {str(e)}"


@mcp.tool()
def delete_track(ctx: Context, track_index: int) -> str:
    """Delete a track by index."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_track", {"track_index": track_index})
        if result.get("deleted"):
            return f"Deleted track {track_index} ({result.get('name','unknown')})"
        return f"Track {track_index} not deleted"
    except Exception as e:
        logger.error(f"Error deleting track: {str(e)}")
        return f"Error deleting track: {str(e)}"


@mcp.tool()
def duplicate_track(ctx: Context, track_index: int, target_index: int = None) -> str:
    """Duplicate a track (optional target index is best-effort)."""
    try:
        ableton = get_ableton_connection()
        params: Dict[str, Any] = {"track_index": track_index}
        if target_index is not None:
            params["target_index"] = target_index
        result = ableton.send_command("duplicate_track", params)
        note = result.get("note")
        suffix = f" ({note})" if note else ""
        return f"Duplicated track {track_index} -> {result.get('index')} named {result.get('name')} {suffix}"
    except Exception as e:
        logger.error(f"Error duplicating track: {str(e)}")
        return f"Error duplicating track: {str(e)}"


@mcp.tool()
def set_track_io(
    ctx: Context,
    track_index: int,
    input_type: Optional[str] = None,
    input_channel: Optional[str] = None,
    output_type: Optional[str] = None,
    output_channel: Optional[str] = None
) -> str:
    """Set track input/output routing using names or indices."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_io", {
            "track_index": track_index,
            "input_type": input_type,
            "input_channel": input_channel,
            "output_type": output_type,
            "output_channel": output_channel
        })
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error setting track routing: {str(e)}")
        return f"Error setting track routing: {str(e)}"


@mcp.tool()
def set_track_monitor(ctx: Context, track_index: int, state: str = "auto") -> str:
    """Set monitoring state (in/auto/off)."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_monitor", {"track_index": track_index, "state": state})
        return f"Monitoring set to {result.get('monitoring_state')}"
    except Exception as e:
        logger.error(f"Error setting monitoring: {str(e)}")
        return f"Error setting monitoring: {str(e)}"


@mcp.tool()
def set_track_arm(ctx: Context, track_index: int, arm: bool = True) -> str:
    """Arm or disarm a track."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_arm", {"track_index": track_index, "arm": arm})
        return f"Track {track_index} arm={result.get('arm')}"
    except Exception as e:
        logger.error(f"Error arming track: {str(e)}")
        return f"Error arming track: {str(e)}"


@mcp.tool()
def set_track_solo(ctx: Context, track_index: int, solo: bool = True) -> str:
    """Solo or unsolo a track."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_solo", {"track_index": track_index, "solo": solo})
        return f"Track {track_index} solo={result.get('solo')}"
    except Exception as e:
        logger.error(f"Error soloing track: {str(e)}")
        return f"Error soloing track: {str(e)}"


@mcp.tool()
def set_track_mute(ctx: Context, track_index: int, mute: bool = True) -> str:
    """Mute or unmute a track."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_mute", {"track_index": track_index, "mute": mute})
        return f"Track {track_index} mute={result.get('mute')}"
    except Exception as e:
        logger.error(f"Error muting track: {str(e)}")
        return f"Error muting track: {str(e)}"


@mcp.tool()
def set_track_volume(ctx: Context, track_index: int, volume: float) -> str:
    """Set track volume (uses Live parameter min/max and clamps)."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_volume", {"track_index": track_index, "volume": volume})
        return f"Track {track_index} volume set to {result.get('volume')} (min {result.get('min')}, max {result.get('max')})"
    except Exception as e:
        logger.error(f"Error setting track volume: {str(e)}")
        return f"Error setting track volume: {str(e)}"


@mcp.tool()
def set_track_panning(ctx: Context, track_index: int, panning: float) -> str:
    """Set track panning (-1..1)."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_panning", {"track_index": track_index, "panning": panning})
        return f"Track {track_index} panning set to {result.get('panning')}"
    except Exception as e:
        logger.error(f"Error setting track panning: {str(e)}")
        return f"Error setting track panning: {str(e)}"


@mcp.tool()
def set_send_level(ctx: Context, track_index: int, send_index: int, level: float) -> str:
    """Set a send level for a track."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_send_level", {
            "track_index": track_index,
            "send_index": send_index,
            "level": level
        })
        return f"Track {track_index} send {send_index} -> {result.get('value')}"
    except Exception as e:
        logger.error(f"Error setting send level: {str(e)}")
        return f"Error setting send level: {str(e)}"


@mcp.tool()
def create_return_track(ctx: Context, name: Optional[str] = None) -> str:
    """Create a return track and optionally name it."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_return_track", {"name": name})
        return f"Created return track {result.get('index')} named {result.get('name')}"
    except Exception as e:
        logger.error(f"Error creating return track: {str(e)}")
        return f"Error creating return track: {str(e)}"


@mcp.tool()
def delete_return_track(ctx: Context, index: int) -> str:
    """Delete a return track by index."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_return_track", {"index": index})
        if result.get("deleted"):
            return f"Deleted return track {index} ({result.get('name')})"
        return f"Return track {index} not deleted"
    except Exception as e:
        logger.error(f"Error deleting return track: {str(e)}")
        return f"Error deleting return track: {str(e)}"


@mcp.tool()
def set_return_track_name(ctx: Context, index: int, name: str) -> str:
    """Rename a return track."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_return_track_name", {"index": index, "name": name})
        return f"Return track {index} renamed to {result.get('name')}"
    except Exception as e:
        logger.error(f"Error renaming return track: {str(e)}")
        return f"Error renaming return track: {str(e)}"

@mcp.tool()
def set_track_name(ctx: Context, track_index: int, name: str) -> str:
    """
    Set the name of a track.
    
    Parameters:
    - track_index: The index of the track to rename
    - name: The new name for the track
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_track_name", {"track_index": track_index, "name": name})
        return f"Renamed track to: {result.get('name', name)}"
    except Exception as e:
        logger.error(f"Error setting track name: {str(e)}")
        return f"Error setting track name: {str(e)}"

@mcp.tool()
def create_clip(ctx: Context, track_index: int, clip_index: int, length: float = 4.0) -> str:
    """
    Create a new MIDI clip in the specified track and clip slot.
    
    Parameters:
    - track_index: The index of the track to create the clip in
    - clip_index: The index of the clip slot to create the clip in
    - length: The length of the clip in beats (default: 4.0)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_clip", {
            "track_index": track_index, 
            "clip_index": clip_index, 
            "length": length
        })
        return f"Created new clip at track {track_index}, slot {clip_index} with length {length} beats"
    except Exception as e:
        logger.error(f"Error creating clip: {str(e)}")
        return f"Error creating clip: {str(e)}"


@mcp.tool()
def delete_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Delete a clip from a slot."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_index})
        if result.get("deleted"):
            return f"Deleted clip at track {track_index}, slot {clip_index}"
        return f"No clip to delete at track {track_index}, slot {clip_index} ({result.get('reason','unknown')})"
    except Exception as e:
        logger.error(f"Error deleting clip: {str(e)}")
        return f"Error deleting clip: {str(e)}"


@mcp.tool()
def duplicate_clip(
    ctx: Context,
    track_index: int,
    clip_index: int,
    target_track_index: Optional[int] = None,
    target_clip_index: Optional[int] = None
) -> str:
    """Duplicate a clip by copying its notes/loop to another slot."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("duplicate_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "target_track_index": target_track_index,
            "target_clip_index": target_clip_index
        })
        target = result.get("target", {})
        return (
            f"Duplicated clip to track {target.get('track_index', target_track_index or track_index)}, "
            f"slot {target.get('clip_index', target_clip_index or clip_index)} "
            f"(length {result.get('length')}, midi={result.get('is_midi')})"
        )
    except Exception as e:
        logger.error(f"Error duplicating clip: {str(e)}")
        return f"Error duplicating clip: {str(e)}"

@mcp.tool()
def add_notes_to_clip(
    ctx: Context, 
    track_index: int, 
    clip_index: int, 
    notes: List[Dict[str, Union[int, float, bool]]]
) -> str:
    """
    Add MIDI notes to a clip (supports optional probability/velocity deviation/release velocity when available).
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - notes: List of note dictionaries, each with pitch, start_time, duration, velocity, mute, and optionally probability, velocity_deviation, release_velocity
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("add_notes_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        })
        return f"Added {len(notes)} notes to clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error adding notes to clip: {str(e)}")
        return f"Error adding notes to clip: {str(e)}"


@mcp.tool()
def add_basic_drum_pattern(
    ctx: Context,
    track_index: int,
    clip_index: int,
    length: float = 4.0,
    velocity: int = 100,
    style: str = "four_on_floor"
) -> str:
    """Drop a simple 4-bar drum pattern (kick/snare/hat) into a clip."""
    try:
        ableton = get_ableton_connection()
        # Ensure clip exists
        try:
            ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": length})
        except Exception:
            pass

        style_lower = style.lower()
        notes: List[Dict[str, Union[int, float, bool]]] = []
        if style_lower == "trap":
            # Trap style: sparse kicks, snares on 3, rolling hats
            for bar in range(int(length / 1.0)):
                base = bar * 1.0
                notes.append({"pitch": 36, "start_time": base, "duration": 0.2, "velocity": velocity, "mute": False})
                notes.append({"pitch": 36, "start_time": base + 0.75, "duration": 0.2, "velocity": velocity - 10, "mute": False})
                notes.append({"pitch": 38, "start_time": base + 0.5, "duration": 0.2, "velocity": velocity + 5, "mute": False})
                # Hi-hat rolls every 1/8th with a 1/32 roll before snare
                for step in range(8):
                    notes.append({"pitch": 42, "start_time": base + (step * 0.125), "duration": 0.1, "velocity": velocity - 20, "mute": False})
                notes.append({"pitch": 42, "start_time": base + 0.48, "duration": 0.05, "velocity": velocity - 25, "mute": False})
                notes.append({"pitch": 42, "start_time": base + 0.52, "duration": 0.05, "velocity": velocity - 25, "mute": False})
        else:
            # Default four-on-the-floor
            bars = int(length / 1.0)
            for bar in range(bars):
                base = bar * 1.0
                for beat in range(4):
                    notes.append({"pitch": 36, "start_time": base + beat * 0.25, "duration": 0.2, "velocity": velocity, "mute": False})
                notes.append({"pitch": 38, "start_time": base + 0.5, "duration": 0.2, "velocity": velocity + 5, "mute": False})
                notes.append({"pitch": 38, "start_time": base + 1.5, "duration": 0.2, "velocity": velocity + 5, "mute": False})
                for step in range(8):
                    notes.append({"pitch": 42, "start_time": base + (step * 0.125), "duration": 0.1, "velocity": velocity - 20, "mute": False})

        result = ableton.send_command("add_notes_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        })
        return f"Added {len(notes)} drum notes with style '{style_lower}' (result: {result})"
    except Exception as e:
        logger.error(f"Error adding drum pattern: {str(e)}")
        return f"Error adding drum pattern: {str(e)}"


@mcp.tool()
def add_chord_stack(
    ctx: Context,
    track_index: int,
    clip_index: int,
    root_midi: int = 60,
    quality: str = "major",
    bars: int = 4,
    chord_length: float = 1.0
) -> str:
    """Generate a repeating chord stack in the target clip."""
    try:
        ableton = get_ableton_connection()
        try:
            ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": float(bars)})
        except Exception:
            pass

        quality_map = {
            "major": [0, 4, 7],
            "minor": [0, 3, 7],
            "sus2": [0, 2, 7],
            "sus4": [0, 5, 7],
            "7": [0, 4, 7, 10],
            "maj7": [0, 4, 7, 11],
            "min7": [0, 3, 7, 10]
        }
        intervals = quality_map.get(quality.lower(), quality_map["major"])

        notes = []
        for bar in range(bars):
            start = float(bar)
            for interval in intervals:
                notes.append({
                    "pitch": root_midi + interval,
                    "start_time": start,
                    "duration": chord_length,
                    "velocity": 100,
                    "mute": False
                })

        result = ableton.send_command("add_notes_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        })
        return f"Added {len(notes)} chord notes ({quality}) to clip: {result}"
    except Exception as e:
        logger.error(f"Error adding chord stack: {str(e)}")
        return f"Error adding chord stack: {str(e)}"

@mcp.tool()
def set_clip_name(ctx: Context, track_index: int, clip_index: int, name: str) -> str:
    """
    Set the name of a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    - name: The new name for the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_clip_name", {
            "track_index": track_index,
            "clip_index": clip_index,
            "name": name
        })
        return f"Renamed clip at track {track_index}, slot {clip_index} to '{name}'"
    except Exception as e:
        logger.error(f"Error setting clip name: {str(e)}")
        return f"Error setting clip name: {str(e)}"


@mcp.tool()
def set_clip_loop(
    ctx: Context,
    track_index: int,
    clip_index: int,
    start: Optional[float] = None,
    end: Optional[float] = None,
    loop_on: bool = True
) -> str:
    """Set loop start/end and toggle looping for a clip."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_clip_loop", {
            "track_index": track_index,
            "clip_index": clip_index,
            "start": start,
            "end": end,
            "loop_on": loop_on
        })
        return (
            f"Clip {track_index}:{clip_index} loop_start={result.get('loop_start')} "
            f"loop_end={result.get('loop_end')} looping={result.get('looping')}"
        )
    except Exception as e:
        logger.error(f"Error setting clip loop: {str(e)}")
        return f"Error setting clip loop: {str(e)}"


@mcp.tool()
def set_clip_length(ctx: Context, track_index: int, clip_index: int, length: float) -> str:
    """Resize a clip loop length."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_clip_length", {
            "track_index": track_index,
            "clip_index": clip_index,
            "length": length
        })
        return (
            f"Clip {track_index}:{clip_index} length set to {result.get('length')} "
            f"(loop_end={result.get('loop_end')})"
        )
    except Exception as e:
        logger.error(f"Error setting clip length: {str(e)}")
        return f"Error setting clip length: {str(e)}"


@mcp.tool()
def quantize_clip(ctx: Context, track_index: int, clip_index: int, grid: int = 16, amount: float = 1.0) -> str:
    """Quantize MIDI clip notes to a grid (e.g., grid=16 => 1/16th notes)."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("quantize_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "grid": grid,
            "amount": amount
        })
        return (
            f"Quantized {result.get('note_count', 0)} notes to grid {result.get('grid')} "
            f"(amount {result.get('amount')})"
        )
    except Exception as e:
        logger.error(f"Error quantizing clip: {str(e)}")
        return f"Error quantizing clip: {str(e)}"

@mcp.tool()
def set_tempo(ctx: Context, tempo: float) -> str:
    """
    Set the tempo of the Ableton session.
    
    Parameters:
    - tempo: The new tempo in BPM
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_tempo", {"tempo": tempo})
        return f"Set tempo to {tempo} BPM"
    except Exception as e:
        logger.error(f"Error setting tempo: {str(e)}")
        return f"Error setting tempo: {str(e)}"


@mcp.tool()
def set_time_signature(ctx: Context, numerator: int = 4, denominator: int = 4) -> str:
    """Set the global time signature."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_time_signature", {
            "numerator": numerator,
            "denominator": denominator
        })
        return f"Time signature set to {result.get('signature_numerator')}/{result.get('signature_denominator')}"
    except Exception as e:
        logger.error(f"Error setting time signature: {str(e)}")
        return f"Error setting time signature: {str(e)}"


@mcp.tool()
def load_instrument_or_effect(ctx: Context, track_index: int, uri: str) -> str:
    """
    Load an instrument or effect onto a track using its URI.
    
    Parameters:
    - track_index: The index of the track to load the instrument on
    - uri: The URI of the instrument or effect to load (e.g., 'query:Synths#Instrument%20Rack:Bass:FileId_5116')
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": uri
        })
        
        # Check if the instrument was loaded successfully
        if result.get("loaded", False):
            new_devices = result.get("new_devices", [])
            if new_devices:
                return f"Loaded instrument with URI '{uri}' on track {track_index}. New devices: {', '.join(new_devices)}"
            else:
                devices = result.get("devices_after", [])
                return f"Loaded instrument with URI '{uri}' on track {track_index}. Devices on track: {', '.join(devices)}"
        else:
            return f"Failed to load instrument with URI '{uri}'"
    except Exception as e:
        logger.error(f"Error loading instrument by URI: {str(e)}")
        return f"Error loading instrument by URI: {str(e)}"

@mcp.tool()
def load_device(ctx: Context, track_index: int, device_uri: str, device_slot: int = -1) -> str:
    """
    Load a device onto a track using its browser URI.
    
    Parameters:
    - track_index: The index of the track to load on
    - device_uri: Browser URI for the device (e.g., 'Audio Effects/Compressor')
    - device_slot: Optional slot position (-1 appends)
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("load_device", {
            "track_index": track_index,
            "device_uri": device_uri,
            "device_slot": device_slot
        })
        if result.get("loaded", False):
            parameter_meta: Any = result.get("parameters")
            device_name: Optional[str] = result.get("item_name", device_uri)
            try:
                device_index = max(result.get("device_count", 1) - 1, 0)
                meta_resp = ableton.send_command("get_device_parameters", {
                    "track_index": track_index,
                    "device_index": device_index
                })
                device_name = meta_resp.get("device_name", device_name)
                parameter_meta = meta_resp.get("parameters", parameter_meta)
            except Exception as meta_err:
                logger.warning(f"Could not fetch parameter metadata after load: {meta_err}")
            _update_cache_item(
                name=result.get("item_name", device_uri),
                uri=device_uri,
                category=None,
                path=None,
                parameters=parameter_meta
            )
            try:
                if device_name and parameter_meta:
                    _update_cache_parameters_by_name(device_name, parameter_meta)
            except Exception as cache_err:
                logger.warning(f"Could not merge parameter metadata into cache: {cache_err}")
            return (
                f"Loaded device '{result.get('item_name', device_uri)}' on track "
                f"{track_index} (devices now: {result.get('device_count')})"
            )
        return f"Failed to load device '{device_uri}' on track {track_index}"
    except Exception as e:
        logger.error(f"Error loading device: {str(e)}")
        return f"Error loading device: {str(e)}"

@mcp.tool()
def set_device_parameter(ctx: Context, track_index: int, device_index: int, parameter: str, value: Any) -> str:
    """
    Set a device parameter by name or index (numeric or human-friendly values like '50%' or '-12 dB').
    
    Parameters:
    - track_index: Track index containing the device
    - device_index: Device index on that track
    - parameter: Parameter name (case-insensitive) or numeric index
    - value: Target value
    """
    try:
        ableton = get_ableton_connection()
        param_spec: Any = parameter
        if isinstance(parameter, str) and parameter.strip().lstrip("-").isdigit():
            param_spec = int(parameter)
        result = ableton.send_command("set_device_parameter", {
            "track_index": track_index,
            "device_index": device_index,
            "parameter": param_spec,
            "value": value
        })
        param_name = result.get("name") or result.get("parameter")
        return (
            f"Set {param_name} on device '{result.get('device_name')}' "
            f"from {result.get('before')} to {result.get('after')} "
            f"(range {result.get('min')}..{result.get('max')}, quantized={result.get('is_quantized')})"
        )
    except Exception as e:
        logger.error(f"Error setting device parameter: {str(e)}")
        return f"Error setting device parameter: {str(e)}"


@mcp.tool()
def get_device_parameters(ctx: Context, track_index: int, device_index: int) -> str:
    """Return parameter metadata for a device."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_device_parameters", {
            "track_index": track_index,
            "device_index": device_index
        })
        # Cache enrichment by device name if possible
        try:
            params = result.get("parameters", [])
            device_name = result.get("device_name")
            if device_name and params:
                _update_cache_parameters_by_name(device_name, params)
        except Exception as cache_err:
            logger.warning(f"Could not enrich cache with parameters: {cache_err}")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error getting device parameters: {str(e)}")
        return f"Error getting device parameters: {str(e)}"


@mcp.tool()
def save_device_preset(ctx: Context, track_index: int, device_index: int, name: str) -> str:
    """Save a device snapshot to disk for later reuse."""
    try:
        ableton = get_ableton_connection()
        snapshot = ableton.send_command("save_device_snapshot", {
            "track_index": track_index,
            "device_index": device_index
        })
        path = _preset_path(name)
        payload = {
            "name": name,
            "track_index": track_index,
            "device_index": device_index,
            "device_name": snapshot.get("device_name"),
            "track_name": snapshot.get("track_name"),
            "snapshot": snapshot.get("snapshot", {})
        }
        path.write_text(json.dumps(payload, indent=2))
        return f"Saved preset '{name}' for device {snapshot.get('device_name')} to {path}"
    except Exception as e:
        logger.error(f"Error saving device preset: {str(e)}")
        return f"Error saving device preset: {str(e)}"


@mcp.tool()
def load_device_preset(ctx: Context, track_index: int, device_index: int, name: str) -> str:
    """Apply a saved preset to a device."""
    try:
        path = _preset_path(name)
        if not path.exists():
            return f"Preset '{name}' not found at {path}"
        preset = json.loads(path.read_text())
        snapshot = preset.get("snapshot", {})
        ableton = get_ableton_connection()
        result = ableton.send_command("apply_device_snapshot", {
            "track_index": track_index,
            "device_index": device_index,
            "snapshot": snapshot
        })
        applied = result.get("applied", [])
        success = [a for a in applied if "error" not in a]
        errors = [a for a in applied if "error" in a]
        summary = f"Applied {len(success)} params"
        if errors:
            summary += f", {len(errors)} errors: {errors}"
        return summary
    except Exception as e:
        logger.error(f"Error loading device preset: {str(e)}")
        return f"Error loading device preset: {str(e)}"

@mcp.tool()
def set_device_sidechain_source(
    ctx: Context,
    track_index: int,
    device_index: int,
    source_track_index: int,
    pre_fx: bool = True,
    mono: bool = True
) -> str:
    """
    Enable sidechain and set the source track on a device (e.g., Compressor).
    
    Parameters:
    - track_index: Track with the device
    - device_index: Device index
    - source_track_index: Track to use as sidechain source
    - pre_fx: Use pre-FX tap if available
    - mono: Use mono sidechain if available
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("set_device_sidechain_source", {
            "track_index": track_index,
            "device_index": device_index,
            "source_track_index": source_track_index,
            "pre_fx": pre_fx,
            "mono": mono
        })
        return (
            f"Sidechain set for device '{result.get('device_name')}' "
            f"from track {source_track_index} (mono={result.get('mono_set')}, pre_fx={result.get('pre_fx_set')})"
        )
    except Exception as e:
        logger.error(f"Error setting device sidechain source: {str(e)}")
        return f"Error setting device sidechain source: {str(e)}"


@mcp.tool()
def load_sidechain_helper(
    ctx: Context,
    track_index: int,
    source_track_index: int,
    target_device_index: int = 0,
    fallback_param_index: int = 0
) -> str:
    """
    Load the SidechainHelper_Advanced Max device onto a track and prefill routing values.
    
    Parameters:
    - track_index: Track to load the helper onto
    - source_track_index: Sidechain source track (0-based)
    - target_device_index: Target device index on the track (e.g., Compressor)
    - fallback_param_index: Parameter index to write if routing properties are hidden
    """
    try:
        helper_path = _install_sidechain_helper()
        ableton = get_ableton_connection()
        uri = _resolve_uri_by_name("SidechainHelper_Advanced", category="audio_effects", path="Max Audio Effect", max_items=400)
        if not uri:
            uri = _resolve_uri_by_name("SidechainHelper_Advanced", category="all", path=None, max_items=400)
        if not uri:
            location_hint = f"Copy located at {helper_path}" if helper_path else "Ensure the helper is available in your User Library under Presets/Audio Effects/Max Audio Effect"
            return f"Could not locate SidechainHelper_Advanced in the browser. {location_hint}"

        load_result = ableton.send_command("load_device", {
            "track_index": track_index,
            "device_uri": uri,
            "device_slot": -1
        })
        if not load_result.get("loaded", False):
            return f"Failed to load SidechainHelper_Advanced (uri: {uri})"

        helper_device_index = max(load_result.get("device_count", 1) - 1, 0)
        params_to_set = [
            ("Source Track", source_track_index),
            ("Target Track", track_index),
            ("Target Device", target_device_index),
            ("Parameter Index", fallback_param_index)
        ]
        applied: List[str] = []
        for name, value in params_to_set:
            try:
                ableton.send_command("set_device_parameter", {
                    "track_index": track_index,
                    "device_index": helper_device_index,
                    "parameter": name,
                    "value": value
                })
                applied.append(name)
            except Exception as param_err:
                logger.warning(f"Could not set helper parameter {name}: {param_err}")

        summary = (
            f"Loaded SidechainHelper_Advanced on track {track_index} (device {helper_device_index}) "
            f"and pointed source track to {source_track_index}, target device {target_device_index}."
        )
        if applied:
            summary += f" Parameters set: {', '.join(applied)}."
        if helper_path:
            summary += f" Device file: {helper_path}"
        return summary
    except Exception as e:
        logger.error(f"Error loading sidechain helper: {str(e)}")
        return f"Error loading sidechain helper: {str(e)}"

@mcp.tool()
def fire_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Start playing a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("fire_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Started playing clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error firing clip: {str(e)}")
        return f"Error firing clip: {str(e)}"

@mcp.tool()
def stop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Stop playing a clip.
    
    Parameters:
    - track_index: The index of the track containing the clip
    - clip_index: The index of the clip slot containing the clip
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return f"Stopped clip at track {track_index}, slot {clip_index}"
    except Exception as e:
        logger.error(f"Error stopping clip: {str(e)}")
        return f"Error stopping clip: {str(e)}"

@mcp.tool()
def start_playback(ctx: Context) -> str:
    """Start playing the Ableton session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("start_playback")
        return "Started playback"
    except Exception as e:
        logger.error(f"Error starting playback: {str(e)}")
        return f"Error starting playback: {str(e)}"

@mcp.tool()
def stop_playback(ctx: Context) -> str:
    """Stop playing the Ableton session."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_playback")
        return "Stopped playback"
    except Exception as e:
        logger.error(f"Error stopping playback: {str(e)}")
        return f"Error stopping playback: {str(e)}"


@mcp.tool()
def create_scene(ctx: Context, index: int = -1, name: Optional[str] = None) -> str:
    """Create a new scene."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("create_scene", {"index": index, "name": name})
        return f"Created scene {result.get('index')} named {result.get('name')}"
    except Exception as e:
        logger.error(f"Error creating scene: {str(e)}")
        return f"Error creating scene: {str(e)}"


@mcp.tool()
def delete_scene(ctx: Context, index: int) -> str:
    """Delete a scene by index."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("delete_scene", {"index": index})
        if result.get("deleted"):
            return f"Deleted scene {index} ({result.get('name')})"
        return f"Scene {index} not deleted"
    except Exception as e:
        logger.error(f"Error deleting scene: {str(e)}")
        return f"Error deleting scene: {str(e)}"


@mcp.tool()
def duplicate_scene(ctx: Context, index: int) -> str:
    """Duplicate a scene."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("duplicate_scene", {"index": index})
        return f"Duplicated scene {index} -> {result.get('index')} ({result.get('name')})"
    except Exception as e:
        logger.error(f"Error duplicating scene: {str(e)}")
        return f"Error duplicating scene: {str(e)}"


@mcp.tool()
def fire_scene(ctx: Context, index: int) -> str:
    """Launch a scene."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("fire_scene", {"index": index})
        return f"Fired scene {index} ({result.get('name')})"
    except Exception as e:
        logger.error(f"Error firing scene: {str(e)}")
        return f"Error firing scene: {str(e)}"


@mcp.tool()
def stop_scene(ctx: Context, index: int) -> str:
    """Stop all clips in a scene."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("stop_scene", {"index": index})
        return f"Stopped scene {index} ({result.get('name')})"
    except Exception as e:
        logger.error(f"Error stopping scene: {str(e)}")
        return f"Error stopping scene: {str(e)}"

@mcp.tool()
def get_browser_tree(ctx: Context, category_type: str = "all") -> str:
    """
    Get a hierarchical tree of browser categories from Ableton.
    
    Parameters:
    - category_type: Type of categories to get ('all', 'instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects')
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_browser_tree", {
            "category_type": category_type
        })
        
        # Check if we got any categories
        if "available_categories" in result and len(result.get("categories", [])) == 0:
            available_cats = result.get("available_categories", [])
            return (f"No categories found for '{category_type}'. "
                   f"Available browser categories: {', '.join(available_cats)}")
        
        # Format the tree in a more readable way
        total_folders = result.get("total_folders", 0)
        formatted_output = f"Browser tree for '{category_type}' (showing {total_folders} folders):\n\n"
        
        def format_tree(item, indent=0):
            output = ""
            if item:
                prefix = "  " * indent
                name = item.get("name", "Unknown")
                path = item.get("path", "")
                has_more = item.get("has_more", False)
                
                # Add this item
                output += f"{prefix}• {name}"
                if path:
                    output += f" (path: {path})"
                if has_more:
                    output += " [...]"
                output += "\n"
                
                # Add children
                for child in item.get("children", []):
                    output += format_tree(child, indent + 1)
            return output
        
        # Format each category
        for category in result.get("categories", []):
            formatted_output += format_tree(category)
            formatted_output += "\n"
        
        return formatted_output
    except Exception as e:
        error_msg = str(e)
        if "Browser is not available" in error_msg:
            logger.error(f"Browser is not available in Ableton: {error_msg}")
            return f"Error: The Ableton browser is not available. Make sure Ableton Live is fully loaded and try again."
        elif "Could not access Live application" in error_msg:
            logger.error(f"Could not access Live application: {error_msg}")
            return f"Error: Could not access the Ableton Live application. Make sure Ableton Live is running and the Remote Script is loaded."
        else:
            logger.error(f"Error getting browser tree: {error_msg}")
            return f"Error getting browser tree: {error_msg}"

@mcp.tool()
def list_loadable_devices(ctx: Context, category: str = "all", max_items: int = 200) -> str:
    """List loadable devices from the Live browser."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("list_loadable_devices", {
            "category": category,
            "max_items": max_items
        })
        # Cache results for reuse
        try:
            CACHE_FILE.write_text(json.dumps(result, indent=2))
        except Exception:
            logger.warning("Could not write device cache; continuing without cache")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error listing loadable devices: {str(e)}")
        return f"Error listing loadable devices: {str(e)}"

@mcp.tool()
def search_loadable_devices(ctx: Context, query: str, category: str = "all", max_items: int = 50) -> str:
    """Search loadable devices by name substring."""
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("search_loadable_devices", {
            "query": query,
            "category": category,
            "max_items": max_items
        })
        try:
            CACHE_FILE.write_text(json.dumps(result, indent=2))
        except Exception:
            logger.warning("Could not write device cache; continuing without cache")
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Error searching loadable devices: {str(e)}")
        return f"Error searching loadable devices: {str(e)}"

def _resolve_uri_by_name(query: str, category: str = "all", path: Optional[str] = None, max_items: int = 200) -> Optional[str]:
    """Try to resolve a device URI by name/path using cache or an expanded live search."""
    query_lower = query.lower()
    best_match = None
    try:
        if CACHE_FILE.exists():
            cached = json.loads(CACHE_FILE.read_text())
            items = cached.get("items", [])
            candidates = []
            for item in items:
                name = item.get("name", "")
                if query_lower in name.lower():
                    if category == "all" or item.get("category") == category:
                        if path is None or (item.get("path") and path.lower() in item.get("path", "").lower()):
                            candidates.append(item)
            def score(item):
                name_lower = item.get("name", "").lower()
                if name_lower == query_lower:
                    return 0
                if name_lower.startswith(query_lower):
                    return 1
                return 2
            if candidates:
                candidates.sort(key=score)
                best_match = candidates[0].get("uri")
    except Exception as cache_err:
        logger.debug(f"Cache lookup failed: {cache_err}")
    if best_match:
        return best_match

    # Fallback: live search with larger horizon
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("search_loadable_devices", {
            "query": query,
            "category": category,
            "max_items": max_items
        })
        items = result.get("items", [])
        if items:
            try:
                # merge into cache rather than overwrite to preserve prior categories
                existing = {"items": []}
                if CACHE_FILE.exists():
                    existing = json.loads(CACHE_FILE.read_text())
                merged = {"items": existing.get("items", [])}
                merged["items"].extend(items)
                CACHE_FILE.write_text(json.dumps(merged, indent=2))
            except Exception:
                logger.warning("Could not write device cache; continuing without cache")
            if path:
                for item in items:
                    if path.lower() in item.get("path", "").lower():
                        return item.get("uri")
            return items[0].get("uri")
    except Exception as e:
        logger.error(f"Error resolving URI by name: {str(e)}")
    return None

@mcp.tool()
def load_device_by_name(ctx: Context, track_index: int, name: str, category: str = "audio_effects", path: Optional[str] = None) -> str:
    """
    Load a device by name substring without specifying URI.
    
    Parameters:
    - track_index: Track to load onto
    - name: Name substring to match (case-insensitive)
    - category: Browser category to search (default 'audio_effects')
    - path: Optional browser path hint (e.g., 'Audio Effects/Dynamics')
    """
    try:
        uri = _resolve_uri_by_name(name, category, path, max_items=200)
        if not uri:
            return f"No device found matching '{name}' in category '{category}'"
        ableton = get_ableton_connection()
        result = ableton.send_command("load_device", {
            "track_index": track_index,
            "device_uri": uri,
            "device_slot": -1
        })
        if result.get("loaded", False):
            parameter_meta: Any = result.get("parameters")
            device_name: Optional[str] = result.get("item_name", name)
            try:
                device_index = max(result.get("device_count", 1) - 1, 0)
                meta_resp = ableton.send_command("get_device_parameters", {
                    "track_index": track_index,
                    "device_index": device_index
                })
                device_name = meta_resp.get("device_name", device_name)
                parameter_meta = meta_resp.get("parameters", parameter_meta)
            except Exception as meta_err:
                logger.warning(f"Could not fetch parameter metadata after load: {meta_err}")
            _update_cache_item(
                name=result.get("item_name", name),
                uri=uri,
                category=category,
                path=None,
                parameters=parameter_meta
            )
            try:
                if device_name and parameter_meta:
                    _update_cache_parameters_by_name(device_name, parameter_meta)
            except Exception as cache_err:
                logger.warning(f"Could not merge parameter metadata into cache: {cache_err}")
            return (
                f"Loaded device '{result.get('item_name', name)}' on track "
                f"{track_index} (devices now: {result.get('device_count')})"
            )
        return f"Failed to load device '{name}' (uri: {uri})"
    except Exception as e:
        logger.error(f"Error loading device by name: {str(e)}")
        return f"Error loading device by name: {str(e)}"

@mcp.tool()
def get_browser_items_at_path(ctx: Context, path: str) -> str:
    """
    Get browser items at a specific path in Ableton's browser.
    
    Parameters:
    - path: Path in the format "category/folder/subfolder"
            where category is one of the available browser categories in Ableton
    """
    try:
        ableton = get_ableton_connection()
        result = ableton.send_command("get_browser_items_at_path", {
            "path": path
        })
        
        # Check if there was an error with available categories
        if "error" in result and "available_categories" in result:
            error = result.get("error", "")
            available_cats = result.get("available_categories", [])
            return (f"Error: {error}\n"
                   f"Available browser categories: {', '.join(available_cats)}")
        
        return json.dumps(result, indent=2)
    except Exception as e:
        error_msg = str(e)
        if "Browser is not available" in error_msg:
            logger.error(f"Browser is not available in Ableton: {error_msg}")
            return f"Error: The Ableton browser is not available. Make sure Ableton Live is fully loaded and try again."
        elif "Could not access Live application" in error_msg:
            logger.error(f"Could not access Live application: {error_msg}")
            return f"Error: Could not access the Ableton Live application. Make sure Ableton Live is running and the Remote Script is loaded."
        elif "Unknown or unavailable category" in error_msg:
            logger.error(f"Invalid browser category: {error_msg}")
            return f"Error: {error_msg}. Please check the available categories using get_browser_tree."
        elif "Path part" in error_msg and "not found" in error_msg:
            logger.error(f"Path not found: {error_msg}")
            return f"Error: {error_msg}. Please check the path and try again."
        else:
            logger.error(f"Error getting browser items at path: {error_msg}")
            return f"Error getting browser items at path: {error_msg}"

@mcp.tool()
def load_drum_kit(ctx: Context, track_index: int, rack_uri: str, kit_path: str) -> str:
    """
    Load a drum rack and then load a specific drum kit into it.
    
    Parameters:
    - track_index: The index of the track to load on
    - rack_uri: The URI of the drum rack to load (e.g., 'Drums/Drum Rack')
    - kit_path: Path to the drum kit inside the browser (e.g., 'drums/acoustic/kit1')
    """
    try:
        ableton = get_ableton_connection()
        
        # Step 1: Load the drum rack
        result = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": rack_uri
        })
        
        if not result.get("loaded", False):
            return f"Failed to load drum rack with URI '{rack_uri}'"
        
        # Step 2: Get the drum kit items at the specified path
        kit_result = ableton.send_command("get_browser_items_at_path", {
            "path": kit_path
        })
        
        if "error" in kit_result:
            return f"Loaded drum rack but failed to find drum kit: {kit_result.get('error')}"
        
        # Step 3: Find a loadable drum kit
        kit_items = kit_result.get("items", [])
        loadable_kits = [item for item in kit_items if item.get("is_loadable", False)]
        
        if not loadable_kits:
            return f"Loaded drum rack but no loadable drum kits found at '{kit_path}'"
        
        # Step 4: Load the first loadable kit
        kit_uri = loadable_kits[0].get("uri")
        load_result = ableton.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": kit_uri
        })
        
        return f"Loaded drum rack and kit '{loadable_kits[0].get('name')}' on track {track_index}"
    except Exception as e:
        logger.error(f"Error loading drum kit: {str(e)}")
        return f"Error loading drum kit: {str(e)}"

# Main execution
def main():
    """Run the MCP server"""
    mcp.run()

if __name__ == "__main__":
    main()
