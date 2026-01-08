import logging
import json
from typing import Optional, Dict, List, Any
from .connection import get_ableton_connection

logger = logging.getLogger("mcp_server.macros")

def get_rack_macros(track_index: int, device_index: int = 0) -> List[Dict[str, Any]]:
    """
    Get the macro controls for a Rack device.
    
    Args:
        track_index (int): Track index.
        device_index (int): Device index.
        
    Returns:
        list: List of macros [{'name': 'Macro 1', 'value': 0.5, 'index': 1}, ...]
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("get_rack_macros", {
            "track_index": track_index,
            "device_index": device_index
        })
        
        if res.get("status") == "error":
            logger.error(f"Error getting macros: {res.get('error')}")
            return []
            
        macros = res.get("macros", [])
        return macros
        
    except Exception as e:
        logger.error(f"Error executing get_rack_macros: {e}")
        return []

def set_rack_macro(track_index: int, device_index: int, macro_index: int, value: float) -> bool:
    """
    Set a macro control value.
    
    Args:
        track_index (int): Track index.
        device_index (int): Device index.
        macro_index (int): Parameter index of the macro (as returned by get_rack_macros).
        value (float): Value (0.0 - 1.0).
        
    Returns:
        bool: True if successful.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_device_parameter", {
            "track_index": track_index,
            "device_index": device_index,
            "parameter": macro_index,
            "value": value
        })
        
        if res.get("status") == "success":
            return True
        else:
            logger.error(f"Failed to set macro: {res.get('message')}")
            return False
            
    except Exception as e:
        logger.error(f"Error executing set_rack_macro: {e}")
        return False

def add_macro(track_index: int, device_index: int = 0) -> bool:
    """
    Add a visible macro to the Rack.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("add_macro", {
            "track_index": track_index,
            "device_index": device_index
        })
        return res.get("status") == "success"
    except Exception as e:
        logger.error(f"Error executing add_macro: {e}")
        return False

def remove_macro(track_index: int, device_index: int = 0) -> bool:
    """
    Remove a visible macro from the Rack.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("remove_macro", {
            "track_index": track_index,
            "device_index": device_index
        })
        return res.get("status") == "success"
    except Exception as e:
        logger.error(f"Error executing remove_macro: {e}")
        return False

def randomize_macros(track_index: int, device_index: int = 0) -> bool:
    """
    Randomize macro values.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("randomize_macros", {
            "track_index": track_index,
            "device_index": device_index
        })
        return res.get("status") == "success"
    except Exception as e:
        logger.error(f"Error executing randomize_macros: {e}")
        return False

def get_rack_chains(track_index: int, device_index: int = 0) -> Dict[str, Any]:
    """
    Get chains and drum pads info.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("get_rack_chains", {
            "track_index": track_index,
            "device_index": device_index
        })
        if res.get("status") == "error":
             return {}
        return res
    except Exception as e:
        logger.error(f"Error executing get_rack_chains: {e}")
        return {}
