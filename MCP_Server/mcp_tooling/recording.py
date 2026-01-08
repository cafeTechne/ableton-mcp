
import logging
import json
from .connection import get_ableton_connection

logger = logging.getLogger("mcp_server.recording")

def set_record_mode(enabled: bool) -> bool:
    """Enable/Disable global arrangement record mode."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_record_mode", {"enabled": enabled})
        return res.get("status") == "success"
    except Exception as e:
        logger.error(f"Error executing set_record_mode: {e}")
        return False

def trigger_session_record(record_length: float = None) -> bool:
    """Trigger session recording (optionally for a fixed length)."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("trigger_session_record", {"record_length": record_length})
        return res.get("status") == "success"
    except Exception as e:
        logger.error(f"Error executing trigger_session_record: {e}")
        return False

def capture_midi(destination: int = 0) -> bool:
    """
    Capture MIDI from recent playing.
    Destination: 0=Session, 1=Arrangement (if supported)
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("capture_midi", {"destination": destination})
        return res.get("status") == "success"
    except Exception as e:
        logger.error(f"Error executing capture_midi: {e}")
        return False

def set_overdub(enabled: bool) -> bool:
    """Enable/Disable Session Overdub."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_overdub", {"enabled": enabled})
        return res.get("status") == "success"
    except Exception as e:
        logger.error(f"Error executing set_overdub: {e}")
        return False
