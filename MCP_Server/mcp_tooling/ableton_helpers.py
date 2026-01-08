
import logging
import time
from typing import Optional
from .connection import get_ableton_connection
from .util import load_device_by_name

logger = logging.getLogger("mcp_server.helpers")

def ensure_track_exists(track_index: Optional[int], prefer: str = "midi", allow_create: bool = True) -> int:
    """Ensure a track exists at the requested index; append a new track if needed."""
    return _ensure_track_exists(track_index, prefer, allow_create)

# Internal impl to match captured code style
def _ensure_track_exists(track_index: Optional[int], prefer: str = "midi", allow_create: bool = True) -> int:
    import time
    ableton = get_ableton_connection()
    # Use get_song_context instead of deprecated get_session_info
    context = ableton.send_command("get_song_context", {"include_clips": False})
    track_count = len(context.get("tracks", []))
    
    if track_index is not None and 0 <= track_index < track_count:
        return track_index
    if not allow_create:
        raise IndexError(f"Track index {track_index} out of range and creation disabled")
        
    if prefer == "audio":
        resp = ableton.send_command("create_audio_track", {"index": -1})
    else:
        resp = ableton.send_command("create_midi_track", {"index": -1})
    
    new_index = resp.get("index", track_count)
    
    # Verification loop: Wait for track to be visible to API
    for _ in range(10):
        try:
            ableton.send_command("get_track_info", {"track_index": new_index})
            return new_index
        except Exception:
            time.sleep(0.2)
            
    # One last try or return anyway
    return new_index

def ensure_clip_slot(track_index: int, clip_index: int, allow_create: bool = True) -> bool:
    """Ensure the clip slot exists; optionally extend scenes."""
    return _ensure_clip_slot(track_index, clip_index, allow_create)

def _ensure_clip_slot(track_index: int, clip_index: int, allow_create: bool = True) -> bool:
    if clip_index < 0:
        return False
    ableton = get_ableton_connection()
    try:
        track_info = ableton.send_command("get_track_info", {"track_index": track_index})
        existing = len(track_info.get("clip_slots", []))
        if clip_index < existing:
            return True
        if not allow_create:
            return False
        # Create needed scenes
        needed = clip_index - existing + 1
        for _ in range(needed):
            ableton.send_command("create_scene", {"index": -1})
        return True
    except Exception:
        return False

def ensure_device(ableton, track_index, class_name_fragment, slot_index=-1):
    """Check if a device exists on the track and return its index."""
    try:
        track_info = ableton.send_command("get_track_info", {"track_index": track_index})
        devices = track_info.get("devices", [])
        
        if slot_index >= 0 and slot_index < len(devices):
             dev = devices[slot_index]
             if class_name_fragment.lower() in dev.get("name", "").lower() or \
                class_name_fragment.lower() in dev.get("class_name", "").lower():
                 return slot_index
        
        for dev in devices:
             if class_name_fragment.lower() in dev.get("name", "").lower() or \
                class_name_fragment.lower() in dev.get("class_name", "").lower():
                 return dev.get("index")
    except Exception:
        pass
    return None

def load_sample_to_simpler(track_index: int, sample_query: str, backup_query: str = "Loop") -> bool:
    """
    Intelligently search for a sample and load it into a Simpler on the target track.
    
    Strategy:
    1. Search browser for 'sample_query' in 'samples'.
    2. Filter results for valid audio files (.wav, .aif).
    3. If not found, retry with 'backup_query'.
    4. Load the found URI directly via 'load_browser_item'.
       - On a MIDI track, this automatically creates a Simpler.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    conn = get_ableton_connection()

    def _find_audio_uri(query):
        if not query: return None
        search = conn.send_command("search_loadable_devices", {
            "query": query, 
            "category": "samples",
            "max_items": 50
        })
        if search and "items" in search:
            for item in search["items"]:
                name = item.get("name", "").lower()
                if name.endswith(".wav") or name.endswith(".aif"):
                    return item.get("uri")
        return None

    # 1. Search Primary
    print(f"   🔍 Searching for audio: '{sample_query}'...")
    target_uri = _find_audio_uri(sample_query)
    
    # 2. Search Backup
    if not target_uri and backup_query:
        print(f"   ⚠️ '{sample_query}' not found. Searching backup: '{backup_query}'...")
        target_uri = _find_audio_uri(backup_query)
        
    if not target_uri:
        print(f"   ❌ Could not find any audio samples for '{sample_query}' or '{backup_query}'.")
        return False
        
    # 3. Load
    try:
        print(f"   📥 Loading sample (auto-Simpler creation)...")
        conn.send_command("load_browser_item", {
            "track_index": track_index,
            "item_uri": target_uri
        })
        # Wait a moment for load
        time.sleep(2.0)
        
        # 4. Verify Simpler Existence
        # Sometimes get_simpler_info fails immediately after load due to indexing lag
        start_time = time.time()
        while time.time() - start_time < 5.0:
            info = conn.send_command("get_simpler_info", {"track_index": track_index})
            if info.get("status") != "error":
                return True
                
            # If specific call fails, check generic device count
            devs = conn.send_command("get_device_parameters", {"track_index": track_index, "device_index": 0})
            if devs.get("status") != "error" and devs.get("device_name"):
                 # A device exists, assume it's valid enough to proceed even if specific Simpler API is cranky
                 print(f"   ℹ️ Verified device '{devs.get('device_name')}' exists (Simpler API check pending)")
                 return True
                 
            time.sleep(0.5)
            
        print("   ⚠️ Warning: Sample loaded but Simpler device not fully verified by API.")
        return True # Return true anyway to attempt playback, as load command didn't error
        
    except Exception as e:
        print(f"   ❌ Error loading sample: {e}")
        return False
