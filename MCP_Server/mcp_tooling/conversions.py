import logging
from typing import Dict, Any, Optional

from .connection import get_ableton_connection

logger = logging.getLogger("mcp_server.conversions")

def sliced_simpler_to_drum_rack(track_index: int, device_index: Optional[int] = None) -> Dict[str, Any]:
    """
    Convert a Simpler device in Slicing mode to a Drum Rack.
    
    Args:
        track_index: Index of the track containing the Simpler
        device_index: Optional index of the Simpler device. If None, finds the first Simpler.
        
    Returns:
        Dict containing status and message
    """
    try:
        ableton = get_ableton_connection()
        return ableton.send_command("create_drum_rack_from_slices", {
            "track_index": track_index,
            "device_index": device_index
        })
    except Exception as e:
        logger.error(f"Error executing sliced_simpler_to_drum_rack: {e}")
        return {"status": "error", "message": str(e)}

def create_drum_rack_from_audio_clip(track_index: int, clip_index: int) -> Dict[str, Any]:
    """
    Create a new Drum Rack track from an audio clip.
    
    Args:
        track_index: Index of the track containing the audio clip
        clip_index: Index of the audio clip slot
        
    Returns:
        Dict containing status and message
    """
    try:
        ableton = get_ableton_connection()
        return ableton.send_command("create_drum_rack_from_audio_clip", {
            "track_index": track_index,
            "clip_index": clip_index
        })
    except Exception as e:
        logger.error(f"Error executing create_drum_rack_from_audio_clip: {e}")
        return {"status": "error", "message": str(e)}

def move_devices_to_drum_rack(track_index: int) -> Dict[str, Any]:
    """
    Move devices on a track to a new Drum Rack pad.
    
    This creates a new Drum Rack, moves the devices to a pad, and places the Drum Rack
    on the track.
    
    Args:
        track_index: Index of the track
        
    Returns:
        Dict containing status and message
    """
    try:
        ableton = get_ableton_connection()
        return ableton.send_command("move_devices_to_drum_rack", {
            "track_index": track_index
        })
    except Exception as e:
        logger.error(f"Error executing move_devices_to_drum_rack: {e}")
        return {"status": "error", "message": str(e)}

def audio_to_midi_clip(track_index: int, clip_index: int, conversion_type: str) -> Dict[str, Any]:
    """
    Convert an audio clip to MIDI (Drums, Harmony, or Melody).
    
    Args:
        track_index: Index of the track containing the audio clip
        clip_index: Index of the audio clip slot
        conversion_type: "drums", "harmony", or "melody"
        
    Returns:
        Dict containing status and message
    """
    try:
        command_map = {
            "drums": "audio_to_drums",
            "harmony": "audio_to_harmony",
            "melody": "audio_to_melody"
        }
        
        command = command_map.get(conversion_type.lower())
        if not command:
            return {"status": "error", "message": f"Invalid conversion type: {conversion_type}"}
            
        ableton = get_ableton_connection()
        return ableton.send_command(command, {
            "track_index": track_index,
            "clip_index": clip_index
        })
    except Exception as e:
        logger.error(f"Error executing audio_to_midi_clip: {e}")
        return {"status": "error", "message": str(e)}
