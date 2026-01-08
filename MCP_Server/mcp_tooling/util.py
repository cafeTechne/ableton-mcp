from typing import Optional, List, Dict, Any
import logging
import json
import os
from pathlib import Path
from .connection import get_ableton_connection

logger = logging.getLogger("mcp_server.util")

# Path Configuration
CACHE_DIR = Path(os.environ.get("ABLETON_MCP_CACHE_DIR", Path.cwd() / "cache"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_FILE = CACHE_DIR / "browser_devices.json"
ROUTABLE_CACHE_FILE = CACHE_DIR / "routable_devices.json"
PRESET_DIR = Path(os.environ.get("ABLETON_MCP_PRESET_DIR", Path.cwd() / "presets"))
PRESET_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_CACHE_FILE = CACHE_DIR / "browser_samples.json"
CLIP_CACHE_FILE_FS = CACHE_DIR / "browser_clips_fs.json"
MODULE_CACHE_DIR = Path(__file__).resolve().parent.parent / "cache" # Relative to MCP_Server/mcp_tooling/../
MODULE_CACHE_FILE = MODULE_CACHE_DIR / "browser_devices.json"

def setup_trace_logger():
    """Setup profiling logger if env var is set."""
    if os.environ.get("ABLETON_MCP_TRACE"):
        l = logging.getLogger("mcp_trace")
        l.setLevel(logging.DEBUG)
        h = logging.StreamHandler()
        h.setFormatter(logging.Formatter('%(asctime)s - TRACE - %(message)s'))
        l.addHandler(h)
        return l
    return None

def _merge_parameter_lists(existing: Optional[List[Any]], incoming: Optional[List[Any]]) -> Optional[List[Any]]:
    """Merge two parameter lists, preserving the richest metadata available."""
    if not incoming: return existing
    if not existing: return incoming

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
        merged[key] = {**prior, **{k: v for k, v in param.items() if v is not None}}
    return list(merged.values())

def update_cache_item(name: str, uri: str, category: Optional[str] = None, path: Optional[str] = None, parameters: Optional[List[Any]] = None):
    """Merge a device entry into the local cache."""
    try:
        if CACHE_FILE.exists():
            cache = json.loads(CACHE_FILE.read_text())
        else:
            cache = {"items": []}
        items = cache.get("items", [])
        updated = False
        for item in items:
            if item.get("uri") == uri:
                item["name"] = name
                if category: item["category"] = category
                if path: item["path"] = path
                if parameters: item["parameters"] = _merge_parameter_lists(item.get("parameters"), parameters)
                updated = True
                break
        if not updated:
            entry = {"name": name, "uri": uri}
            if category: entry["category"] = category
            if path: entry["path"] = path
            if parameters: entry["parameters"] = parameters
            items.append(entry)
        cache["items"] = items
        CACHE_FILE.write_text(json.dumps(cache, indent=2))
    except Exception as e:
        logger.warning(f"Could not update device cache: {e}")

def update_cache_parameters_by_name(name: str, parameters: Optional[List[Any]] = None):
    """Update cache entry parameters by matching name when URI is unknown."""
    if not parameters: return
    try:
        if not CACHE_FILE.exists(): return
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

def search_cache(cache_file: Path, query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Search a local cache file for items matching query."""
    if not cache_file.exists():
        return []
    try:
        data = json.loads(cache_file.read_text("utf-8"))
        items = data.get("items", [])
        query_lower = query.lower()
        matches = []
        
        for item in items:
            name = str(item.get("name", ""))
            if query_lower in name.lower():
                matches.append(item)
                
        def score(item):
            n = str(item.get("name", "")).lower()
            if n == query_lower: return 0
            if n.startswith(query_lower): return 1
            return 2
            
        matches.sort(key=score)
        return matches[:limit]
    except Exception as e:
        logger.warning(f"Error searching cache {cache_file}: {e}")
        return []

def resolve_uri_by_name(query: str, category: str = "all", path: Optional[str] = None, max_items: int = 200) -> Optional[str]:
    """
    DEPRECATED: URIs are session-specific and become stale after Ableton restarts.
    Use load_device_by_name() instead, which uses live browser search.
    
    This function is kept for backwards compatibility but will return None
    and log a warning.
    """
    import warnings
    warnings.warn(
        "resolve_uri_by_name is deprecated. Use load_device_by_name() instead.",
        DeprecationWarning,
        stacklevel=2
    )
    logger.warning("resolve_uri_by_name is deprecated - URIs are unreliable. Use load_device_by_name() instead.")
    return None  # Force callers to update to the new approach


def get_best_device_name(query: str, category: str = "all") -> Optional[str]:
    """
    Search local cache for the best matching device name.
    Returns the full device name for use with search_and_load_device.
    """
    query_lower = query.lower()
    
    def _search_cache(cache_path: Path) -> Optional[str]:
        if not cache_path.exists():
            return None
        try:
            cached = json.loads(cache_path.read_text())
            items = cached.get("items", [])
            candidates = []
            for item in items:
                name = item.get("name", "")
                if query_lower in name.lower():
                    category_match = (
                        category == "all"
                        or not item.get("category")
                        or item.get("category") == category
                    )
                    if category_match:
                        candidates.append(item)
            
            if not candidates:
                return None
            
            # Score: exact > starts with > contains
            def score(item):
                name_lower = item.get("name", "").lower()
                if name_lower == query_lower:
                    return 0
                if name_lower.startswith(query_lower):
                    return 1
                return 2
            
            candidates.sort(key=score)
            return candidates[0].get("name")
        except Exception:
            return None
    
    # Try both cache locations
    result = _search_cache(CACHE_FILE)
    if not result and MODULE_CACHE_FILE != CACHE_FILE:
        result = _search_cache(MODULE_CACHE_FILE)
    return result

def load_device_by_name(track_index: int, query: str, category: str = "all") -> Dict[str, Any]:
    """
    Load a device onto a track using name-based search.
    Uses cache for discovery (finding best name match) and live browser search for loading.
    
    Args:
        track_index: Target track index
        query: Name or partial name to search for
        category: "all", "instruments", "sounds", "drums", "audio_effects", "midi_effects"
    Returns:
        Dict with loading result from Ableton
    """
    # First, try to find a better name match from cache
    cached_name = get_best_device_name(query, category)
    search_query = cached_name if cached_name else query
    
    # Use live browser search for actual loading (fail-proof)
    ableton = get_ableton_connection()
    result = ableton.send_command("search_and_load_device", {
        "track_index": track_index,
        "query": search_query,
        "category": category
    })
    
    return result

