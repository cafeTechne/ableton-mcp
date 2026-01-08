"""
Drummer Module for Ableton MCP

This module provides drum pattern generation using the drum_patterns_library.json.
It integrates with mcp_tooling to create MIDI clips from patterns.

Usage:
    from mcp_tooling.drummer import (
        list_genres, list_patterns, get_pattern,
        generate_drum_pattern, generate_drum_pattern_by_name
    )
    
    # List available genres
    genres = list_genres()
    
    # List patterns in a genre
    patterns = list_patterns("latin")
    
    # Generate a pattern on a track
    result = generate_drum_pattern(
        track_index=0,
        clip_index=0,
        genre="latin",
        pattern_name="Afro-Cuban 1_measure_a",
        bars=4,
        velocity_scale=1.0
    )
"""

import json
import os
import logging
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union

logger = logging.getLogger("mcp_server.drummer")

# Load the drum patterns library
_LIBRARY_PATH = Path(__file__).parent / "drum_patterns_library.json"
_library_cache: Optional[Dict] = None


def _load_library() -> Dict:
    """Load and cache the drum patterns library."""
    global _library_cache
    if _library_cache is not None:
        return _library_cache
    
    try:
        with open(_LIBRARY_PATH, "r", encoding="utf-8") as f:
            _library_cache = json.load(f)
        logger.info(f"Loaded drum patterns library: {_library_cache['metadata']['total_patterns']} patterns")
        return _library_cache
    except Exception as e:
        logger.error(f"Failed to load drum patterns library: {e}")
        return {"metadata": {}, "genres": {}}


def get_metadata() -> Dict[str, Any]:
    """Get library metadata (version, total patterns, genre count)."""
    lib = _load_library()
    return lib.get("metadata", {})


def list_genres() -> List[str]:
    """List all available genres in the library."""
    lib = _load_library()
    return list(lib.get("genres", {}).keys())


def list_patterns(genre: str, variation: Optional[str] = None) -> List[Dict[str, str]]:
    """
    List all patterns in a genre.
    
    Args:
        genre: Genre name (e.g., "latin", "rock", "house")
        variation: Optional filter by variation type ("A", "B", "fill", etc.)
    
    Returns:
        List of dicts with 'name' and 'variation' keys
    """
    lib = _load_library()
    patterns = lib.get("genres", {}).get(genre.lower(), [])
    
    result = []
    for p in patterns:
        if variation is None or p.get("variation", "").lower() == variation.lower():
            result.append({
                "name": p.get("name", "Unknown"),
                "variation": p.get("variation", "")
            })
    return result


def search_patterns(query: str, genre: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Search for patterns by name.
    
    Args:
        query: Search query (partial match, case-insensitive)
        genre: Optional genre filter
        limit: Maximum results to return
    
    Returns:
        List of matching patterns with genre info
    """
    lib = _load_library()
    query_lower = query.lower()
    results = []
    
    genres_to_search = [genre.lower()] if genre else lib.get("genres", {}).keys()
    
    for g in genres_to_search:
        patterns = lib.get("genres", {}).get(g, [])
        for p in patterns:
            name = p.get("name", "")
            if query_lower in name.lower():
                results.append({
                    "genre": g,
                    "name": name,
                    "variation": p.get("variation", "")
                })
                if len(results) >= limit:
                    return results
    
    return results


def get_pattern(genre: str, pattern_name: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific pattern by genre and name.
    
    Args:
        genre: Genre name
        pattern_name: Pattern name (exact match)
    
    Returns:
        Pattern dict or None if not found
    """
    lib = _load_library()
    patterns = lib.get("genres", {}).get(genre.lower(), [])
    
    for p in patterns:
        if p.get("name", "").lower() == pattern_name.lower():
            return p
    
    return None


def get_random_pattern(
    genre: Optional[str] = None, 
    variation: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    Get a random pattern, optionally filtered by genre/variation.
    
    Args:
        genre: Optional genre filter
        variation: Optional variation filter ("A", "B", "fill")
    
    Returns:
        Random pattern dict or None if no matches
    """
    lib = _load_library()
    candidates = []
    
    genres_to_search = [genre.lower()] if genre else lib.get("genres", {}).keys()
    
    for g in genres_to_search:
        patterns = lib.get("genres", {}).get(g, [])
        for p in patterns:
            if variation is None or p.get("variation", "").lower() == variation.lower():
                candidates.append({"genre": g, "pattern": p})
    
    if candidates:
        selected = random.choice(candidates)
        return selected
    return None


def pattern_to_notes(
    pattern_data: Dict[str, Any],
    bars: int = 1,
    velocity_scale: float = 1.0,
    humanize: float = 0.0,
    swing: float = 0.0
) -> Tuple[List[Dict[str, Any]], float]:
    """
    Convert a pattern dict to MIDI notes.
    
    Args:
        pattern_data: The 'pattern' sub-dict from a library entry
        bars: Number of bars to generate (pattern repeats)
        velocity_scale: Velocity multiplier (0.5 = half velocity)
        humanize: Timing randomization amount (0.0-1.0)
        swing: Swing amount (0.0-1.0, affects offbeat 16ths)
    
    Returns:
        Tuple of (notes_list, clip_length_beats)
    """
    import random as rnd
    from .humanization import apply_humanization, HumanizeProfile
    
    tracks = pattern_data.get("tracks", {})
    length_steps = pattern_data.get("length_steps", 16)
    
    # Convert steps to beats (16 steps = 4 beats for 4/4)
    step_duration = 4.0 / length_steps  # 0.25 beats per 16th step
    pattern_length_beats = 4.0  # 1 bar
    
    notes = []
    
    for bar in range(bars):
        bar_offset = bar * pattern_length_beats
        
        for track_name, track_data in tracks.items():
            midi_note = track_data.get("midi_note", 36)
            steps = track_data.get("steps", [])
            
            for step_info in steps:
                step_num = step_info.get("step", 0)
                velocity = step_info.get("velocity", 100)
                
                # Apply velocity scaling
                velocity = int(velocity * velocity_scale)
                velocity = max(1, min(127, velocity))
                
                # Calculate time
                base_time = bar_offset + (step_num * step_duration)
                
                # Manual Swing (if not using Humanize profile swing)
                if swing > 0 and step_num % 2 == 1:
                     base_time += step_duration * swing * 0.5

                notes.append({
                    "pitch": midi_note,
                    "start_time": max(0.0, base_time),
                    "duration": step_duration * 0.9,
                    "velocity": velocity
                })
    
    # Apply Central Humanization
    if humanize > 0:
        # Determine profile based on swing? 
        # For now use 'human' as base, but if swing > 0 maybe mix?
        # Actually, let's just use 'human' profile with 'amount' = humanize.
        profile = HumanizeProfile.get_preset("human")
        apply_humanization(notes, profile, amount=humanize)
        
    clip_length = bars * pattern_length_beats
    return notes, clip_length


def generate_drum_pattern(
    track_index: int,
    clip_index: int,
    genre: str,
    pattern_name: Optional[str] = None,
    variation: Optional[str] = None,
    bars: int = 4,
    velocity_scale: float = 1.0,
    humanize: float = 0.1,
    swing: float = 0.0,
    clear_existing: bool = True
) -> str:
    """
    Generate a drum pattern on a track.
    
    This is the main entry point for creating drum clips.
    
    Args:
        track_index: Target track index
        clip_index: Target clip slot index
        genre: Genre to use (e.g., "latin", "rock", "house")
        pattern_name: Specific pattern name (optional - random if None)
        variation: Filter by variation ("A", "B", "fill") if pattern_name is None
        bars: Number of bars to generate
        velocity_scale: Velocity multiplier
        humanize: Timing/velocity humanization (0.0-1.0)
        swing: Swing amount (0.0-1.0)
        clear_existing: Delete existing clip before creating
    
    Returns:
        Status message describing what was generated
    """
    from .connection import get_ableton_connection
    
    try:
        conn = get_ableton_connection()
        
        # Find pattern
        if pattern_name:
            pattern_entry = get_pattern(genre, pattern_name)
            if not pattern_entry:
                return f"Error: Pattern '{pattern_name}' not found in genre '{genre}'"
        else:
            result = get_random_pattern(genre, variation)
            if not result:
                return f"Error: No patterns found for genre '{genre}'"
            pattern_entry = result["pattern"]
        
        pattern_data = pattern_entry.get("pattern", {})
        actual_name = pattern_entry.get("name", "Unknown")
        actual_variation = pattern_entry.get("variation", "")
        
        # Convert to notes
        notes, clip_length = pattern_to_notes(
            pattern_data,
            bars=bars,
            velocity_scale=velocity_scale,
            humanize=humanize,
            swing=swing
        )
        
        # Clear existing clip if requested
        if clear_existing:
            try:
                conn.send_command("delete_clip", {
                    "track_index": track_index,
                    "clip_index": clip_index
                })
            except:
                pass  # May not exist
        
        # Create clip
        conn.send_command("create_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "length": clip_length
        })
        
        # Add notes
        conn.send_command("add_notes_to_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "notes": notes
        })
        
        return (f"Generated drum pattern: {actual_name} ({actual_variation}) "
                f"| {genre} | {bars} bars | {len(notes)} notes")
    
    except Exception as e:
        logger.error(f"Error generating drum pattern: {e}")
        return f"Error: {e}"


def generate_drum_fill(
    track_index: int,
    clip_index: int,
    genre: str,
    bars: int = 1
) -> str:
    """
    Convenience function to generate a drum fill.
    
    Automatically selects a pattern with variation="fill".
    """
    return generate_drum_pattern(
        track_index=track_index,
        clip_index=clip_index,
        genre=genre,
        variation="fill",
        bars=bars,
        velocity_scale=1.1  # Fills typically louder
    )


def generate_drum_section(
    track_index: int,
    clip_indices: List[int],
    genre: str,
    include_fill: bool = True,
    bars_per_clip: int = 4
) -> str:
    """
    Generate a multi-clip drum section with variations.
    
    Creates A/B variations across clips, optionally ending with a fill.
    
    Args:
        track_index: Target track
        clip_indices: List of clip slots to fill
        genre: Genre to use
        include_fill: Add a fill at the end
        bars_per_clip: Bars per clip
    
    Returns:
        Status summary
    """
    if not clip_indices:
        return "Error: No clip indices provided"
    
    results = []
    variations = ["A", "B"]
    
    for i, clip_idx in enumerate(clip_indices):
        if include_fill and i == len(clip_indices) - 1:
            # Last clip is a fill
            result = generate_drum_fill(track_index, clip_idx, genre, bars=bars_per_clip)
        else:
            # Alternate A/B variations
            var = variations[i % len(variations)]
            result = generate_drum_pattern(
                track_index=track_index,
                clip_index=clip_idx,
                genre=genre,
                variation=var,
                bars=bars_per_clip
            )
        results.append(result)
    
    return f"Generated {len(results)} clips for {genre}: " + "; ".join(results)


# Convenience exports
__all__ = [
    "get_metadata",
    "list_genres",
    "list_patterns",
    "search_patterns",
    "get_pattern",
    "get_random_pattern",
    "pattern_to_notes",
    "generate_drum_pattern",
    "generate_drum_fill",
    "generate_drum_section",
]
