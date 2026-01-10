import logging
import json
import os
from typing import Optional, Dict, Any, List, Union

from fastmcp import FastMCP, Context
from mcp_tooling.connection import get_ableton_connection, AbletonConnection
from mcp_tooling.util import search_cache, CACHE_FILE
from mcp_tooling.devices import (
    load_device_logic, load_simpler_with_sample_logic, load_sampler_with_sample_logic,
    load_sample_by_name_logic, load_drum_kit_logic, load_clip_by_name_logic,
    _resolve_sample_uri_by_name, plan_load_device_logic
)
from mcp_tooling.generators import (
    generate_chord_progression as gen_chords,
    generate_chord_progression_advanced as gen_chords_advanced,
    generate_bassline as gen_bass,
    generate_bassline_advanced_wrapper as gen_bass_advanced,
    generate_strings_advanced_wrapper as gen_strings_advanced,
    generate_woodwinds_advanced_wrapper as gen_winds_advanced,
    generate_brass_advanced_wrapper as gen_brass_advanced,
    generate_rhythmic_comp as gen_rhythmic_comp,
    pattern_generator as gen_pattern
)
from mcp_tooling.arrangement import create_song_blueprint as gen_blueprint, construct_song as do_construct
from mcp_tooling.automation import apply_automation_logic
from mcp_tooling.conversions import (
    sliced_simpler_to_drum_rack as do_slice_simpler,
    create_drum_rack_from_audio_clip as do_create_drum_rack,
    move_devices_to_drum_rack as do_move_devices,
    audio_to_midi_clip as do_audio_to_midi
)
from mcp_tooling.macros import (
    get_rack_macros, set_rack_macro, add_macro, remove_macro, 
    randomize_macros, get_rack_chains
)
from mcp_tooling.recording import set_record_mode, trigger_session_record, capture_midi, set_overdub
from mcp_tooling.drummer import (
    list_genres as drummer_list_genres,
    list_patterns as drummer_list_patterns,
    search_patterns as drummer_search_patterns,
    generate_drum_pattern as gen_drum_pattern,
    generate_drum_fill as gen_drum_fill,
    generate_drum_section as gen_drum_section,
    get_metadata as drummer_get_metadata
)

# Setup Logging
logger = logging.getLogger("mcp_server")
logging.basicConfig(level=logging.INFO)

# Initialize FastMCP
mcp = FastMCP("Ableton Live Context")

# ═══════════════════════════════════════════════════════════════════════════════
# EQ EIGHT PARAMETER CONVERSION UTILITIES
# ═══════════════════════════════════════════════════════════════════════════════
# These functions convert between human-readable units and Ableton's normalized 0.0-1.0 values

import math

EQ8_MIN_FREQ = 10.0       # Hz
EQ8_MAX_FREQ = 22000.0    # Hz
EQ8_MIN_GAIN_DB = -15.0   # dB
EQ8_MAX_GAIN_DB = 15.0    # dB

def hz_to_normalized(freq_hz: float) -> float:
    """
    Convert frequency in Hz to normalized 0.0-1.0 value for EQ Eight.
    
    Formula: norm = log(freq_hz / 10) / log(2200)
    
    Examples:
        hz_to_normalized(100)  -> 0.299  (high pass for rhythm)
        hz_to_normalized(180)  -> 0.376  (high pass for vocals)
        hz_to_normalized(1000) -> 0.597  (1 kHz reference)
        hz_to_normalized(3000) -> 0.756  (presence)
    """
    if freq_hz <= EQ8_MIN_FREQ:
        return 0.0
    if freq_hz >= EQ8_MAX_FREQ:
        return 1.0
    return math.log(freq_hz / EQ8_MIN_FREQ) / math.log(EQ8_MAX_FREQ / EQ8_MIN_FREQ)

def normalized_to_hz(normalized: float) -> float:
    """
    Convert normalized 0.0-1.0 value to frequency in Hz.
    
    Formula: freq_hz = 10 * (2200 ^ norm)
    """
    if normalized <= 0.0:
        return EQ8_MIN_FREQ
    if normalized >= 1.0:
        return EQ8_MAX_FREQ
    return EQ8_MIN_FREQ * math.pow(EQ8_MAX_FREQ / EQ8_MIN_FREQ, normalized)

def db_to_normalized(db: float) -> float:
    """
    Convert dB to normalized 0.0-1.0 value for EQ Eight gain.
    
    Formula: norm = (db + 15) / 30
    
    Examples:
        db_to_normalized(-3)  -> 0.4   (gentle cut)
        db_to_normalized(0)   -> 0.5   (unity)
        db_to_normalized(3)   -> 0.6   (gentle boost)
    """
    if db <= EQ8_MIN_GAIN_DB:
        return 0.0
    if db >= EQ8_MAX_GAIN_DB:
        return 1.0
    return (db - EQ8_MIN_GAIN_DB) / (EQ8_MAX_GAIN_DB - EQ8_MIN_GAIN_DB)

def normalized_to_db(normalized: float) -> float:
    """
    Convert normalized 0.0-1.0 value to dB.
    
    Formula: db = (norm * 30) - 15
    """
    if normalized <= 0.0:
        return EQ8_MIN_GAIN_DB
    if normalized >= 1.0:
        return EQ8_MAX_GAIN_DB
    return EQ8_MIN_GAIN_DB + normalized * (EQ8_MAX_GAIN_DB - EQ8_MIN_GAIN_DB)

# ═══════════════════════════════════════════════════════════════════════════════

# --- TOOLS ---

@mcp.tool()
def list_loadable_devices(category: str = "all", max_items: int = 50) -> str:
    """List loadable devices from cache or Live."""
    try:
        matches = search_cache(CACHE_FILE, "", limit=max_items)
        # Filter by category if needed (basic string check)
        if category != "all":
            matches = [m for m in matches if m.get("category") == category]
        
        return json.dumps({"items": matches[:max_items]}, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def search_loadable_devices(query: str, category: str = "all", max_items: int = 50) -> str:
    """
    Search for available devices/presets by name.
    Returns names for discovery only - use search_and_load_device to actually load.
    """
    try:
        # Try cache first
        matches = search_cache(CACHE_FILE, query, limit=max_items)
        if matches:
            # Return only names for discovery (URIs are session-specific and unreliable)
            return json.dumps({"items": [{"name": m.get("name"), "category": m.get("category"), "path": m.get("path")} for m in matches]}, indent=2)
        
        # Fallback to Live
        ableton = get_ableton_connection()
        res = ableton.send_command("search_loadable_devices", {"query": query, "category": category, "max_items": max_items})
        items = res.get("items", [])
        return json.dumps({"items": [{"name": i.get("name"), "category": i.get("category"), "path": i.get("path")} for i in items]}, indent=2)
    except Exception as e:
        return f"Error: {e}"

# NOTE: load_device by URI was removed - use search_and_load_device instead
# URIs are session-specific and become stale when Ableton restarts


@mcp.tool()
def load_simpler_with_sample(ctx: Context, track_index: int, file_path: str, device_slot: int = -1) -> str:
    """Load Simpler and set sample."""
    return load_simpler_with_sample_logic(track_index, file_path, device_slot)

@mcp.tool()
def load_sampler_with_sample(ctx: Context, track_index: int, file_path: str, device_slot: int = -1) -> str:
    """Load Sampler and set sample."""
    return load_sampler_with_sample_logic(track_index, file_path, device_slot)

@mcp.tool()
def load_sample_by_name(ctx: Context, sample_name: str, track_index: Optional[int] = None, clip_index: int = 0, category: str = "sounds", fire: bool = False) -> str:
    """Load sample by name (best effort)."""
    return load_sample_by_name_logic(sample_name, track_index, clip_index, category, fire)

@mcp.tool()
def load_clip_by_name(ctx: Context, clip_name: str, track_index: Optional[int] = None, clip_index: int = 0, category: str = "all", fire: bool = False) -> str:
    """Load clip by name."""
    return load_clip_by_name_logic(clip_name, track_index, clip_index, category, fire)

@mcp.tool()
def load_drum_kit(ctx: Context, track_index: int, rack_uri: str, kit_path: str) -> str:
    """Load drum kit into rack."""
    return load_drum_kit_logic(track_index, rack_uri, kit_path)

@mcp.tool()
def generate_chord_progression(ctx: Context, track_index: int, clip_index: int, key: str = "C", scale: str = "major", genre_progression: str = "pop_1", instrument_name: Optional[str] = None) -> str:
    """Generate chord progression from preset."""
    return gen_chords(track_index, clip_index, key, scale, genre_progression, instrument_name)

@mcp.tool()
def generate_chord_progression_advanced(
    ctx: Context,
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Optional[str] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    rhythm_style: str = "whole",
    voice_lead: bool = False,
    velocity: int = 90,
    octave: int = 4,
    instrument_name: Optional[str] = None
) -> str:
    """
    Advanced chord progression with 176+ progressions, voice leading, and flexible timing.
    
    progression: "pop_1" | "I V vi IV" | None
    mood: "romantic", "hopeful", "dark", "mysterious", "triumphant", etc.
    total_bars: Target length (4, 8, 12, 16) - adjusts chord timing to fit
    rhythm_style: "whole", "quarter", "syncopated", "arpeggio"
    voice_lead: If True, use inversions for smooth transitions
    """
    # Parse progression if it's a JSON list string
    prog = progression
    if progression and progression.startswith("["):
        try:
            prog = json.loads(progression)
        except:
            pass
    return gen_chords_advanced(
        track_index, clip_index, key, scale, prog, mood,
        beats_per_chord, total_bars, rhythm_style, voice_lead, velocity, octave, instrument_name
    )

@mcp.tool()
def generate_bassline_advanced(
    ctx: Context,
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Optional[str] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "walking",
    velocity: int = 100,
    octave: int = 2,
    instrument_name: Optional[str] = None
) -> str:
    """
    Advanced bassline generator using music theory to follow chords.
    
    progression: "pop_1" | "I V vi IV" | None
    mood: "romantic", "jazz", "blues", etc.
    style: "walking", "root", "pulse", "arpeggio", "syncopated"
    """
    # Parse progression if it's a JSON list string
    prog = progression
    if progression and progression.startswith("["):
        try:
            prog = json.loads(progression)
        except:
            pass
            
    return gen_bass_advanced(
        track_index, clip_index, key, scale, prog, mood,
        beats_per_chord, total_bars, style, velocity, octave, instrument_name
    )

@mcp.tool()
def generate_strings_advanced(
    ctx: Context,
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Optional[str] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "pop",
    velocity: int = 90,
    octave: int = 4, # C4 default = mid range strings
    instrument_name: Optional[str] = None
) -> str:
    """
    Advanced strings generator using music theory to follow chords.
    
    progression: "pop_1" | "I V vi IV" | None
    mood: "pop", "rock", "disco", "jazz", "reggae"
    style: "pop", "rock", "disco", "jazz", "reggae"
    """
    # Parse progression if it's a JSON list string
    prog = progression
    if progression and progression.startswith("["):
        try:
            prog = json.loads(progression)
        except:
            pass
            
    return gen_strings_advanced(
        track_index, clip_index, key, scale, prog, mood,
        beats_per_chord, total_bars, style, velocity, octave, instrument_name
    )

@mcp.tool()
def generate_woodwinds_advanced(
    ctx: Context,
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Optional[str] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "pop",
    velocity: int = 90,
    octave: int = 4,
    instrument_name: Optional[str] = None
) -> str:
    """
    Advanced woodwinds generator using role-based orchestration.
    
    progression: "pop_1" | "I V vi IV" | None
    mood: "pop", "classical", "jazz", "rock", "reggae"
    style: "pop", "classical", "jazz", "rock", "reggae"
    """
    prog = progression
    if progression and progression.startswith("["):
        try:
            prog = json.loads(progression)
        except:
            pass
            
    return gen_winds_advanced(
        track_index, clip_index, key, scale, prog, mood,
        beats_per_chord, total_bars, style, velocity, octave, instrument_name
    )

@mcp.tool()
def generate_brass_advanced(
    ctx: Context,
    track_index: int,
    clip_index: int,
    key: str = "C",
    scale: str = "major",
    progression: Optional[str] = None,
    mood: Optional[str] = None,
    beats_per_chord: float = 4.0,
    total_bars: Optional[int] = None,
    style: str = "pop",
    velocity: int = 100,
    octave: int = 3,
    instrument_name: Optional[str] = None
) -> str:
    """
    Advanced brass generator using impact-first logic.
    
    style: "pop", "rock", "metal", "jazz", "ska", "reggae", "gospel", "edm", "classical"
    """
    prog = progression
    if progression and progression.startswith("["):
        try:
            prog = json.loads(progression)
        except:
            pass
            
    return gen_brass_advanced(
        track_index, clip_index, key, scale, prog, mood,
        beats_per_chord, total_bars, style, velocity, octave, instrument_name
    )

@mcp.tool()
def generate_bassline(ctx: Context, track_index: int, clip_index: int, key: str = "C", scale: str = "major", genre_progression: str = "pop_1", style: str = "follow", instrument_name: Optional[str] = None) -> str:
    """Generate bassline."""
    return gen_bass(track_index, clip_index, key, scale, genre_progression, style, instrument_name)

@mcp.tool()
def pattern_generator(ctx: Context, track_index: int, clip_slot_index: int, pattern_type: str = "four_on_floor", bars: int = 1, root_note: int = 60, velocity: int = 100, swing: float = 0.0, humanize: float = 0.0, fill: bool = False) -> str:
    """Generate MIDI pattern (drums/rhythm)."""
    return gen_pattern(track_index, clip_slot_index, pattern_type, bars, root_note, velocity, swing, humanize, fill)

@mcp.tool()
def create_song_blueprint(genre: str = "pop", key: str = "C", scale: str = "major") -> str:
    """Generate song blueprint JSON."""
    return gen_blueprint(genre, key, scale)

@mcp.tool()
def construct_song(ctx: Context, blueprint_json: str) -> str:
    """Construct song from blueprint."""
    return do_construct(blueprint_json)

@mcp.tool()
def apply_automation(ctx: Context, track_index: int, clip_index: int, parameter_name: str, start_val: float, end_val: float, duration_bars: int = 4, curve: str = "linear") -> str:
    """Apply automation ramp."""
    return apply_automation_logic(track_index, clip_index, parameter_name, start_val, end_val, duration_bars, curve)

# NOTE: plan_load_device was removed - URIs are unreliable
# Use search_and_load_device directly instead

@mcp.tool()
def create_midi_track(ctx: Context, index: int = -1) -> str:
    """Create a new MIDI track at the specified index (-1 for end)."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("create_midi_track", {"index": index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def create_audio_track(ctx: Context, index: int = -1) -> str:
    """Create a new Audio track at the specified index (-1 for end)."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("create_audio_track", {"index": index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def delete_track(ctx: Context, track_index: int) -> str:
    """Delete a track by index."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("delete_track", {"track_index": track_index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def get_browser_items_at_path(ctx: Context, path: str) -> str:
    """Get browser items at path."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("get_browser_items_at_path", {"path": path})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_song_context(ctx: Context, include_clips: bool = False) -> str:
    """
    Get a comprehensive snapshot of the current song state.
    Returns tracks (name, type, devices, has_clips), scenes, tempo, and transport state.
    Use this to understand the current session before making changes.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("get_song_context", {"include_clips": include_clips})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def search_and_load_device(ctx: Context, track_index: int, query: str, category: str = "all") -> str:
    """
    Search for a device/instrument by name and load it onto a track.
    Uses live browser traversal - no cached URIs needed.
    
    Args:
        track_index: Target track index
        query: Name or partial name to search for (e.g., "Grand Piano", "Compressor", "909")
        category: "all", "instruments", "sounds", "drums", "audio_effects", "midi_effects"
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("search_and_load_device", {
            "track_index": track_index,
            "query": query,
            "category": category
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_eq8_band(ctx: Context, track_index: int, band_index: int, enabled: Optional[bool] = None, freq: Optional[float] = None, gain: Optional[float] = None, q: Optional[float] = None, filter_type: Optional[int] = None, device_index: Optional[int] = None) -> str:
    """
    Set parameters for a specific band in EQ Eight.
    
    ⚠️ CRITICAL: All values are NORMALIZED (0.0-1.0), NOT real units!
    
    ═══════════════════════════════════════════════════════════════════
    CONVERSION FORMULAS
    ═══════════════════════════════════════════════════════════════════
    
    FREQUENCY (logarithmic scale, 10 Hz - 22 kHz):
        hz_to_norm = log(freq_hz / 10) / log(2200)
        norm_to_hz = 10 * (2200 ^ normalized)
    
    GAIN (linear scale, -15 dB to +15 dB):
        db_to_norm = (db + 15) / 30
        norm_to_db = (normalized * 30) - 15
    
    Q/RESONANCE (logarithmic scale, 0.1 to 18):
        q_to_norm ≈ log(q / 0.1) / log(180)
    
    ═══════════════════════════════════════════════════════════════════
    PRODUCTION QUICK REFERENCE - FREQUENCY
    ═══════════════════════════════════════════════════════════════════
    
    Normalized | Hz     | Production Use
    -----------|--------|----------------------------------------
    0.150      | 30     | Sub bass fundamental
    0.180      | 50     | Bass body
    0.210      | 80     | Kick punch / Bass upper harmonics
    0.240      | 100    | High pass for rhythm instruments
    0.299      | 180    | High pass for vocals/synths
    0.359      | 300    | Mud cut zone
    0.441      | 500    | Lower mids / honk
    0.524      | 800    | Boxy / nasal removal
    0.597      | 1000   | Mid reference point (1 kHz)
    0.658      | 1500   | Presence begins
    0.710      | 2000   | Vocal clarity
    0.756      | 3000   | Presence peak / harshness
    0.795      | 4000   | Upper clarity
    0.829      | 5000   | Sibilance zone begins
    0.882      | 8000   | Sibilance peak
    0.899      | 10000  | Air / brilliance
    0.932      | 14000  | Super air
    0.959      | 18000  | Extreme top
    
    ═══════════════════════════════════════════════════════════════════
    PRODUCTION QUICK REFERENCE - GAIN
    ═══════════════════════════════════════════════════════════════════
    
    Normalized | dB   | Use
    -----------|------|---------------------------
    0.000      | -15  | Maximum cut
    0.200      | -9   | Strong cut
    0.333      | -5   | Moderate cut
    0.400      | -3   | Gentle cut
    0.500      | 0    | Unity (no change)
    0.567      | +2   | Subtle boost
    0.600      | +3   | Gentle boost
    0.667      | +5   | Moderate boost
    0.800      | +9   | Strong boost
    1.000      | +15  | Maximum boost
    
    ═══════════════════════════════════════════════════════════════════
    FILTER TYPE REFERENCE
    ═══════════════════════════════════════════════════════════════════
    
    0 = Low Cut 12 dB/oct (high pass gentle)
    1 = Low Cut 48 dB/oct (high pass steep)
    2 = Low Shelf
    3 = Bell (parametric)
    4 = High Shelf  
    5 = Notch
    6 = High Cut 12 dB/oct (low pass gentle)
    7 = High Cut 48 dB/oct (low pass steep)
    
    ═══════════════════════════════════════════════════════════════════
    COMMON INSTRUMENT PRESETS
    ═══════════════════════════════════════════════════════════════════
    
    KICK:
        Band 1: HP 40Hz    -> freq=0.180, filter_type=0
        Band 2: Boost 60Hz -> freq=0.210, gain=0.60, q=0.4, filter_type=3
        Band 3: Cut 300Hz  -> freq=0.359, gain=0.35, q=0.5, filter_type=3
        
    SNARE:
        Band 1: HP 100Hz   -> freq=0.299, filter_type=0
        Band 2: Body 200Hz -> freq=0.330, gain=0.57, filter_type=3
        Band 3: Snap 3kHz  -> freq=0.756, gain=0.60, filter_type=3
        
    BASS:
        Band 1: HP 30Hz    -> freq=0.150, filter_type=0
        Band 2: Boost 80Hz -> freq=0.240, gain=0.57, filter_type=3
        
    VOCALS:
        Band 1: HP 80-120Hz -> freq=0.240-0.270, filter_type=1
        Band 2: Cut mud 300 -> freq=0.359, gain=0.40, filter_type=3
        Band 3: Presence 3k -> freq=0.756, gain=0.57, filter_type=3
        Band 8: Air 10kHz   -> freq=0.899, gain=0.57, filter_type=4
        
    PIANO/KEYS:
        Band 1: HP 100Hz    -> freq=0.299, filter_type=0
        Band 8: Air 10kHz   -> freq=0.899, gain=0.55, filter_type=4
    
    Args:
        track_index: Track index
        band_index: Band index (1-8)
        enabled: Enable/disable band (True/False)
        freq: Frequency (NORMALIZED 0.0-1.0) - see table above
        gain: Gain (NORMALIZED 0.0-1.0) - see table above  
        q: Resonance (NORMALIZED 0.0-1.0) - 0.0=wide, 0.5=medium, 1.0=narrow
        filter_type: Integer 0-7 (see filter type reference)
        device_index: Index of EQ8 device if multiple on track
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_eq8_band", {
            "track_index": track_index,
            "band_index": band_index,
            "enabled": enabled,
            "freq": freq,
            "gain": gain,
            "q": q,
            "filter_type": filter_type,
            "device_index": device_index
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def set_compressor_sidechain(ctx: Context, track_index: int, enabled: Optional[bool] = None, source_track_index: Optional[int] = None, gain: Optional[float] = None, mix: Optional[float] = None, device_index: Optional[int] = None) -> str:
    """
    Set Compressor sidechain parameters.
    """
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_compressor_sidechain", {
        "track_index": track_index, "enabled": enabled, "source_track_index": source_track_index,
        "gain": gain, "mix": mix, "device_index": device_index
    }), indent=2)

@mcp.tool()
def get_wavetable_oscillator(ctx: Context, track_index: int, osc_index: int, device_index: int = 0) -> str:
    """Get Wavetable oscillator status (0 or 1)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_wavetable_oscillator", {
        "track_index": track_index, "osc_index": osc_index, "device_index": device_index
    }), indent=2)

@mcp.tool()
def get_wavetable_modulation(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """Get Wavetable modulation matrix info."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_wavetable_modulation", {
        "track_index": track_index, "device_index": device_index
    }), indent=2)

@mcp.tool()
def get_hybrid_reverb_ir(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """Get Hybrid Reverb IR file info."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_hybrid_reverb_ir", {
        "track_index": track_index, "device_index": device_index
    }), indent=2)

@mcp.tool()
def get_specialized_device_info(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """Get info about a specialized device (type, known params)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_specialized_device_info", {
        "track_index": track_index, "device_index": device_index
    }), indent=2)

@mcp.tool()
def toggle_device_active(ctx: Context, track_index: int, device_index: int, active: bool) -> str:
    """Toggle a device on/off."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("toggle_device_active", {
        "track_index": track_index, "device_index": device_index, "active": active
    }), indent=2)

@mcp.tool()
def set_device_parameter(ctx: Context, track_index: int, device_index: int, parameter_name: str, value: float) -> str:
    """
    Set a specific generic parameter on a device.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_device_parameter", {
            "track_index": track_index,
            "device_index": device_index,
            "parameter": parameter_name, 
            "value": value
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_device_parameters(ctx: Context, track_index: int, device_index: int) -> str:
    """
    Get all parameters for a device.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("get_device_parameters", {
            "track_index": track_index,
            "device_index": device_index
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# MIXER TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def set_track_volume(ctx: Context, track_index: int, volume: float) -> str:
    """Set track volume. 0.0=silence, 0.85=0dB, 1.0=+6dB."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_track_volume", {"track_index": track_index, "volume": volume})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_track_panning(ctx: Context, track_index: int, panning: float) -> str:
    """Set track panning. -1.0=left, 0.0=center, 1.0=right."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_track_panning", {"track_index": track_index, "panning": panning})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_send_level(ctx: Context, track_index: int, send_index: int, level: float) -> str:
    """Set send level. send_index: 0=A, 1=B. level: 0.0-1.0."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_send_level", {"track_index": track_index, "send_index": send_index, "level": level})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_track_mute(ctx: Context, track_index: int, mute: bool) -> str:
    """Mute or unmute a track."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_track_mute", {"track_index": track_index, "mute": mute})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_track_solo(ctx: Context, track_index: int, solo: bool) -> str:
    """Solo or unsolo a track."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_track_solo", {"track_index": track_index, "solo": solo})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_track_arm(ctx: Context, track_index: int, arm: bool) -> str:
    """Arm or disarm a track for recording."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_track_arm", {"track_index": track_index, "arm": arm})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_track_name(ctx: Context, track_index: int, name: str) -> str:
    """Set the name of a track."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_track_name", {"track_index": track_index, "name": name})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# TRANSPORT TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def set_tempo(ctx: Context, tempo: float) -> str:
    """Set song tempo in BPM (20-999)."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_tempo", {"tempo": tempo})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def start_playback(ctx: Context) -> str:
    """Start playback."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("start_playback", {})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def stop_playback(ctx: Context) -> str:
    """Stop playback."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("stop_playback", {})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# SCENE TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def create_scene(ctx: Context, index: int = -1, name: Optional[str] = None) -> str:
    """Create a new scene. index=-1 for end."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("create_scene", {"index": index, "name": name})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def fire_scene(ctx: Context, index: int) -> str:
    """Fire (trigger) a scene to play all clips in that row."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("fire_scene", {"index": index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def delete_scene(ctx: Context, index: int) -> str:
    """Delete a scene by index."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("delete_scene", {"index": index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# CLIP TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def create_clip(ctx: Context, track_index: int, clip_index: int, length: float = 4.0) -> str:
    """Create empty MIDI clip. length in beats (4.0 = 1 bar)."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("create_clip", {"track_index": track_index, "clip_index": clip_index, "length": length})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def add_notes_to_clip(ctx: Context, track_index: int, clip_index: int, notes: List[Dict[str, Any]]) -> str:
    """Add MIDI notes. notes=[{pitch:60, start:0.0, duration:1.0, velocity:100}]"""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": notes})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def fire_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Fire (trigger) a clip to play."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("fire_clip", {"track_index": track_index, "clip_index": clip_index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# CONVERSION TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def sliced_simpler_to_drum_rack(ctx: Context, track_index: int, device_index: int = -1) -> str:
    """
    Convert a Sliced Simpler to a Drum Rack.
    
    Args:
        track_index: The index of the track containing the Simpler.
        device_index: Optional device index (default: -1, searches for first Simpler).
    """
    idx = device_index if device_index >= 0 else None
    if do_slice_simpler(track_index, idx):
        return "Successfully converted Simpler to Drum Rack."
    else:
        return "Failed to convert Simpler to Drum Rack. Check logs."

@mcp.tool()
def create_drum_rack_from_audio_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Create a new Drum Rack track from an Audio Clip.
    
    Args:
        track_index: The index of the track containing the clip.
        clip_index: The index of the clip slot.
    """
    if do_create_drum_rack(track_index, clip_index):
        return "Successfully created Drum Rack from Audio Clip."
    else:
        return "Failed to create Drum Rack. Check logs."

@mcp.tool()
def move_devices_to_drum_rack(ctx: Context, track_index: int) -> str:
    """
    Move all devices on a track to a new Drum Rack pad.
    
    Args:
        track_index: The index of the source track.
    """
    result = do_move_devices(track_index)
    if result and result.get("success"):
        return f"Successfully moved devices to Drum Rack. Result: {json.dumps(result)}"
    else:
        return 'Failed to move devices to Drum Rack. Check logs.'

# ═══════════════════════════════════════════════════════════════════════════════
# MACRO CONTROL TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_rack_macros(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """
    Get the macro controls (first 16 parameters) for a Rack device.
    
    Args:
        track_index: The track index.
        device_index: The device index (default 0).
    """
    macros = get_rack_macros(track_index, device_index)
    return json.dumps(macros, indent=2)

@mcp.tool()
def set_rack_macro(ctx: Context, track_index: int, device_index: int, macro_index: int, value: float) -> str:
    """
    Set a macro control value.
    
    Args:
        track_index: The track index.
        device_index: The device index.
        macro_index: The macro index (1-based, e.g. 1 for "Macro 1").
        value: The value to set (0.0 to 1.0).
    """
    if set_rack_macro(track_index, device_index, macro_index, value):
        return f"Successfully set Macro {macro_index} to {value}"
    else:
        return f"Failed to set Macro {macro_index}. Check logs."

# ═══════════════════════════════════════════════════════════════════════════════
# RECORDING TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def set_global_record_mode(ctx: Context, enabled: bool) -> str:
    """Enable or disable the global Arrangement Record button."""
    if set_record_mode(enabled):
        return f"Global Record Mode set to {enabled}"
    return "Failed to set record mode."

@mcp.tool()
def trigger_session_record_button(ctx: Context) -> str:
    """Trigger the Session Record button (New Clip or Overdub depending on context)."""
    if trigger_session_record():
        return "Session Record Triggered"
    return "Failed to trigger session record."

@mcp.tool()
def capture_midi_command(ctx: Context) -> str:
    """Capture recently played MIDI notes (Capture MIDI)."""
    if capture_midi():
        return "MIDI Captured"
    return "Failed to capture MIDI."

@mcp.tool()
def set_session_overdub(ctx: Context, enabled: bool) -> str:
    """Enable or disable Session Overdub (OVR)."""
    if set_overdub(enabled):
        return f"Session Overdub set to {enabled}"
    return "Failed to set overdub."

@mcp.tool()
def stop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Stop a playing clip."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("stop_clip", {"track_index": track_index, "clip_index": clip_index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def delete_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Delete a clip from a slot."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("delete_clip", {"track_index": track_index, "clip_index": clip_index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_clip_name(ctx: Context, track_index: int, clip_index: int, name: str) -> str:
    """Set the name of a clip."""
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_clip_name", {"track_index": track_index, "clip_index": clip_index, "name": name})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# ADVANCED CLIP TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def quantize_clip(ctx: Context, track_index: int, clip_index: int, grid: int = 5, amount: float = 1.0) -> str:
    """
    Quantize MIDI notes in a clip to a grid.
    
    Args:
        track_index: Track index
        clip_index: Clip slot index
        grid: Quantization grid:
            0 = 1/4 (quarter notes)
            1 = 1/8 (eighth notes)
            2 = 1/8T (eighth note triplets)
            3 = 1/8 + 1/8T
            4 = 1/16 (sixteenth notes)
            5 = 1/16T (sixteenth note triplets) - default
            6 = 1/16 + 1/16T
            7 = 1/32
        amount: Quantize strength (0.0 = no change, 1.0 = full quantize)
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("quantize_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "grid": grid,
            "amount": amount
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_clip_notes(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Read all MIDI notes from a clip.
    
    Returns a list of notes with pitch, start, duration, velocity, and mute.
    Useful for analyzing existing content before transposing or modifying.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("get_clip_notes", {
            "track_index": track_index,
            "clip_index": clip_index
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def transpose_clip(ctx: Context, track_index: int, clip_index: int, semitones: int) -> str:
    """
    Transpose all MIDI notes in a clip by semitones.
    
    Args:
        track_index: Track index
        clip_index: Clip slot index
        semitones: Semitones to shift (positive = up, negative = down)
            12 = up one octave
            -12 = down one octave
            7 = up a fifth
    
    Example:
        # Transpose a clip up one octave
        transpose_clip(0, 0, 12)
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("transpose_clip", {
            "track_index": track_index,
            "clip_index": clip_index,
            "semitones": semitones
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def apply_legato(ctx: Context, track_index: int, clip_index: int, preserve_gaps_below: float = 0.0) -> str:
    """
    Apply legato articulation by extending each note to touch the next note.
    
    Useful for smoothing generated MIDI content or creating sustained pads.
    
    Args:
        track_index: Track index
        clip_index: Clip slot index
        preserve_gaps_below: Don't extend notes if gap is smaller than this value in beats
            0.0 = always extend (default)
            0.25 = preserve gaps smaller than 1/16th note
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("apply_legato", {
            "track_index": track_index,
            "clip_index": clip_index,
            "preserve_gaps_below": preserve_gaps_below
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# ROUTING TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def create_return_track(ctx: Context, name: Optional[str] = None) -> str:
    """
    Create a new return track (e.g., for reverb/delay sends).
    
    Args:
        name: Optional name for the return track (e.g., "Reverb", "Delay")
    
    Returns:
        Index of the newly created return track
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("create_return_track", {"name": name})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def get_routing_options(ctx: Context, track_index: int) -> str:
    """
    Get available input and output routing options for a track.
    
    Returns input_types, output_types, input_channels, output_channels.
    Use this to discover valid routing destinations before using set_track_output.
    
    Common output types: "Master", "Sends Only", other track names
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("get_routing_options", {"track_index": track_index})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_track_output(ctx: Context, track_index: int, output_name: str) -> str:
    """
    Set the output routing for a track.
    
    Args:
        track_index: Track index
        output_name: Output destination name (e.g., "Master", "Sends Only", track name)
    
    Use get_routing_options first to see available destinations.
    
    Example:
        # Route track 1 to only sends (no direct output)
        set_track_output(1, "Sends Only")
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_track_output", {
            "track_index": track_index,
            "output_name": output_name
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"


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
    Route audio from one track to a device's sidechain input (e.g., for compression ducking).
    
    Common use case: Route kick drum to a compressor on bass to create ducking.
    
    Args:
        track_index: Track containing the device (e.g., bass track)
        device_index: Compressor/gate device index on that track
        source_track_index: Track to use as sidechain source (e.g., kick track)
        pre_fx: If True, use pre-FX audio from source
        mono: If True, sum to mono for sidechain
    
    Example:
        # Duck bass with kick
        set_device_sidechain_source(bass_track, 0, kick_track)
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_device_sidechain_source", {
            "track_index": track_index,
            "device_index": device_index,
            "source_track_index": source_track_index,
            "pre_fx": pre_fx,
            "mono": mono
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

# ═══════════════════════════════════════════════════════════════════════════════
# ARRANGEMENT TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_arrangement_info(ctx: Context) -> str:
    """
    Get information about the arrangement view.
    
    Returns:
        - is_playing: bool
        - current_song_time: float (beats)
        - loop_start, loop_length, loop: loop region info
        - cue_points: [{index, name, time}, ...]
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("get_arrangement_info", {})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def create_cue_point(ctx: Context, time: float, name: Optional[str] = None) -> str:
    """
    Create a cue point (locator/marker) in the arrangement.
    
    Args:
        time: Position in beats (e.g., 0.0 = bar 1, 16.0 = bar 5)
        name: Name for the cue point (e.g., "Verse", "Chorus", "Drop")
    
    Use this to mark song sections for navigation and arrangement.
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("create_cue_point", {"time": time, "name": name})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_arrangement_loop(ctx: Context, start: float, length: float, enable: bool = True) -> str:
    """
    Set the arrangement loop region.
    
    Args:
        start: Loop start position in beats
        length: Loop length in beats
        enable: Enable/disable looping
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_arrangement_loop", {
            "start": start,
            "length": length,
            "enable": enable
        })
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def set_song_time(ctx: Context, time: float) -> str:
    """
    Set the playhead position in the arrangement.
    
    Args:
        time: Position in beats (e.g., 0.0 = bar 1, 16.0 = bar 5)
    """
    try:
        ableton = get_ableton_connection()
        res = ableton.send_command("set_song_time", {"time": time})
        return json.dumps(res, indent=2)
    except Exception as e:
        return f"Error: {e}"


# ═══════════════════════════════════════════════════════════════════════════════
# CONVERSION TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def sliced_simpler_to_drum_rack(ctx: Context, track_index: int, device_index: Optional[int] = None) -> str:
    """
    Convert a Simpler device in Slicing mode to a Drum Rack.
    Each slice becomes a pad in the new Drum Rack.
    """
    return json.dumps(do_slice_simpler(track_index, device_index), indent=2)

@mcp.tool()
def create_drum_rack_from_audio_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """
    Create a new Drum Rack track from an Audio Clip.
    The audio clip is sliced to a new Drum Rack track.
    """
    return json.dumps(do_create_drum_rack(track_index, clip_index), indent=2)

@mcp.tool()
def move_devices_to_drum_rack(ctx: Context, track_index: int) -> str:
    """
    Move devices on a track to a new Drum Rack pad.
    The devices are moved into a new Drum Rack on the same track.
    """
    return json.dumps(do_move_devices(track_index), indent=2)



# ═══════════════════════════════════════════════════════════════════════════════
# MACRO TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_rack_macros_tool(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """Get macro controls for a Rack Device."""
    return json.dumps(get_rack_macros(track_index, device_index), indent=2)

@mcp.tool()
def set_rack_macro_tool(ctx: Context, track_index: int, device_index: int, macro_index: int, value: float) -> str:
    """
    Set a macro control value.
    macro_index is the parameter index of the macro (use get_rack_macros to find it).
    """
    if set_rack_macro(track_index, device_index, macro_index, value):
        return "Macro updated"
    return "Failed to update macro"

@mcp.tool()
def add_macro_tool(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """Add a visible macro control to the Rack."""
    if add_macro(track_index, device_index):
        return "Macro added"
    return "Failed to add macro"

@mcp.tool()
def remove_macro_tool(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """Remove a visible macro control from the Rack."""
    if remove_macro(track_index, device_index):
        return "Macro removed"
    return "Failed to remove macro"

@mcp.tool()
def randomize_macros_tool(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """Randomize all macro values on the Rack."""
    if randomize_macros(track_index, device_index):
        return "Macros randomized"
    return "Failed to randomize macros"

@mcp.tool()
def get_rack_chains_tool(ctx: Context, track_index: int, device_index: int = 0) -> str:
    """Get chains and drum pads info for a Rack Device."""
    return json.dumps(get_rack_chains(track_index, device_index), indent=2)



# ═══════════════════════════════════════════════════════════════════════════════
# RECORDING TOOLS
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def set_record_mode_tool(ctx: Context, enabled: bool) -> str:
    """Set the global arrangement record mode."""
    if set_record_mode(enabled):
        return f"Record mode {'enabled' if enabled else 'disabled'}"
    return "Failed to set record mode"

@mcp.tool()
def trigger_session_record_tool(ctx: Context, record_length: float = 0.0) -> str:
    """Trigger session recording (or toggle)."""
    if trigger_session_record(record_length):
        return "Session record triggered"
    return "Failed to trigger session record"

@mcp.tool()
def capture_midi_tool(ctx: Context, destination: int = 0) -> str:
    """Capture MIDI from recent playing. Destination 0=Session, 1=Arrangement."""
    if capture_midi(destination):
        return "MIDI Captured"
    return "Failed to capture MIDI"

@mcp.tool()
def set_overdub_tool(ctx: Context, enabled: bool) -> str:
    """Set the global Overdub (OVR) arrangement record state."""
    if set_overdub(enabled):
        return f"Overdub {'enabled' if enabled else 'disabled'}"
    return "Failed to set overdub"

@mcp.tool()
def audio_to_midi_clip_tool(ctx: Context, track_index: int, clip_index: int, conversion_type: str = "drums") -> str:
    """
    Convert an Audio Clip to MIDI (Drums, Harmony, or Melody).
    conversion_type: "drums", "harmony", or "melody".
    Note: Native Live API support for this is limited; the tool will inform if manual action is required.
    """
    return json.dumps(do_audio_to_midi(track_index, clip_index, conversion_type), indent=2)

@mcp.tool()
def set_master_volume(ctx: Context, volume: float) -> str:
    """Set the master track volume (0.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_master_volume", {"volume": volume}), indent=2)

@mcp.tool()
def set_master_pan(ctx: Context, pan: float) -> str:
    """Set the master track panning (-1.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_master_pan", {"pan": pan}), indent=2)

@mcp.tool()
def set_cue_volume(ctx: Context, volume: float) -> str:
    """Set the cue (pre-listen) volume (0.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_cue_volume", {"volume": volume}), indent=2)

@mcp.tool()
def set_crossfader(ctx: Context, value: float) -> str:
    """Set the crossfader position (-1.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_crossfader", {"value": value}), indent=2)

@mcp.tool()
def set_track_crossfade_assign(ctx: Context, track_index: int, assign: int) -> str:
    """Assign track to crossfader: 0=A, 1=None, 2=B."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_track_crossfade_assign", {"track_index": track_index, "assign": assign}), indent=2)

@mcp.tool()
def set_track_send(ctx: Context, track_index: int, send_index: int, value: float) -> str:
    """Set send level for a track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_track_send", {"track_index": track_index, "send_index": send_index, "value": value}), indent=2)

@mcp.tool()
def set_return_volume(ctx: Context, return_index: int, volume: float) -> str:
    """Set volume for a return track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_return_volume", {"index": return_index, "volume": volume}), indent=2)

@mcp.tool()
def set_return_pan(ctx: Context, return_index: int, pan: float) -> str:
    """Set panning for a return track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_return_pan", {"index": return_index, "pan": pan}), indent=2)

@mcp.tool()
def mute_return(ctx: Context, return_index: int, muted: bool = True) -> str:
    """Mute or unmute a return track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("mute_return", {"index": return_index, "mute": muted}), indent=2)

@mcp.tool()
def solo_return(ctx: Context, return_index: int, soloed: bool = True) -> str:
    """Solo or unsolo a return track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("solo_return", {"index": return_index, "solo": soloed}), indent=2)

@mcp.tool()
def get_mixer_overview(ctx: Context) -> str:
    """Get a high-level overview of the entire mixer (Master, Returns, Tracks)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_mixer_overview", {}), indent=2)

@mcp.tool()
def set_scene_tempo(ctx: Context, scene_index: int, tempo: float) -> str:
    """Set the tempo for a scene."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_scene_tempo", {"scene_index": scene_index, "tempo": tempo}), indent=2)

@mcp.tool()
def set_scene_time_signature(ctx: Context, scene_index: int, numerator: int, denominator: int) -> str:
    """Set the time signature for a scene."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_scene_time_signature", {"scene_index": scene_index, "numerator": numerator, "denominator": denominator}), indent=2)

@mcp.tool()
def fire_scene_by_index(ctx: Context, scene_index: int, force_legato: bool = False) -> str:
    """Fire a scene by index."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("fire_scene_by_index", {"scene_index": scene_index, "force_legato": force_legato}), indent=2)

@mcp.tool()
def select_scene(ctx: Context, scene_index: int) -> str:
    """Select a scene."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("select_scene", {"scene_index": scene_index}), indent=2)

@mcp.tool()
def move_scene(ctx: Context, scene_index: int, target_index: int) -> str:
    """Move a scene to a new position."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("move_scene", {"scene_index": scene_index, "target_index": target_index}), indent=2)

@mcp.tool()
def create_scene(ctx: Context, index: int = -1, name: Optional[str] = None) -> str:
    """Create a new scene."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("create_scene", {"index": index, "name": name}), indent=2)

@mcp.tool()
def get_scene_info(ctx: Context, scene_index: int) -> str:
    """Get detailed information about a scene."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_scene_info", {"scene_index": scene_index}), indent=2)

@mcp.tool()
def get_scene_overview(ctx: Context) -> str:
    """Get overview of all scenes."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_scene_overview", {}), indent=2)

@mcp.tool()
def get_available_views(ctx: Context) -> str:
    """Get list of all available application views."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_available_views", {}), indent=2)

@mcp.tool()
def show_view(ctx: Context, view_name: str) -> str:
    """Show a specific application view."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("show_view", {"view_name": view_name}), indent=2)

@mcp.tool()
def hide_view(ctx: Context, view_name: str) -> str:
    """Hide a specific application view."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("hide_view", {"view_name": view_name}), indent=2)

@mcp.tool()
def is_view_visible(ctx: Context, view_name: str, main_window_only: bool = True) -> str:
    """Check if a specific view is visible."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("is_view_visible", {"view_name": view_name, "main_window_only": main_window_only}), indent=2)

@mcp.tool()
def get_focused_document_view(ctx: Context) -> str:
    """Get the currently focused document view."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_focused_document_view", {}), indent=2)

@mcp.tool()
def scroll_view(ctx: Context, direction: int, view_name: str, animate: bool = True) -> str:
    """Scroll a specific view. 0=Up, 1=Down, 2=Left, 3=Right."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("scroll_view", {"direction": direction, "view_name": view_name, "animate": animate}), indent=2)

@mcp.tool()
def get_application_overview(ctx: Context) -> str:
    """Get a high-level overview of the Live application state."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_application_overview", {}), indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# CHAIN & RACK TOOLS (Phase 1)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_chains(ctx: Context, track_index: int, device_index: int) -> str:
    """Get list of chains in a Rack device."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_chains", {"track_index": track_index, "device_index": device_index}), indent=2)

@mcp.tool()
def get_chain_mixer(ctx: Context, track_index: int, device_index: int, chain_index: int) -> str:
    """Get mixer status (vol, pan, sends) for a specific chain."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_chain_mixer", {"track_index": track_index, "device_index": device_index, "chain_index": chain_index}), indent=2)

@mcp.tool()
def set_chain_volume(ctx: Context, track_index: int, device_index: int, chain_index: int, volume: float) -> str:
    """Set volume for a chain (0.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_chain_volume", {"track_index": track_index, "device_index": device_index, "chain_index": chain_index, "volume": volume}), indent=2)

@mcp.tool()
def set_chain_pan(ctx: Context, track_index: int, device_index: int, chain_index: int, pan: float) -> str:
    """Set panning for a chain (-1.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_chain_pan", {"track_index": track_index, "device_index": device_index, "chain_index": chain_index, "pan": pan}), indent=2)

@mcp.tool()
def set_chain_mute_solo(ctx: Context, track_index: int, device_index: int, chain_index: int, mute: Optional[bool] = None, solo: Optional[bool] = None) -> str:
    """Set mute and/or solo state for a chain."""
    conn = get_ableton_connection()
    res = {}
    if mute is not None:
        res["mute"] = conn.send_command("set_chain_mute", {"track_index": track_index, "device_index": device_index, "chain_index": chain_index, "mute": mute})
    if solo is not None:
        res["solo"] = conn.send_command("set_chain_solo", {"track_index": track_index, "device_index": device_index, "chain_index": chain_index, "solo": solo})
    return json.dumps(res, indent=2)

@mcp.tool()
def set_chain_name(ctx: Context, track_index: int, device_index: int, chain_index: int, name: str) -> str:
    """Set the name of a specific chain in a Rack."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_chain_name", {"track_index": track_index, "device_index": device_index, "chain_index": chain_index, "name": name}), indent=2)

@mcp.tool()
def set_chain_color(ctx: Context, track_index: int, device_index: int, chain_index: int, color_index: int) -> str:
    """Set the color of a specific chain in a Rack."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_chain_color", {"track_index": track_index, "device_index": device_index, "chain_index": chain_index, "color": color_index}), indent=2)

@mcp.tool()
def delete_chain_device(ctx: Context, track_index: int, device_index: int, chain_index: int, chain_device_index: int) -> str:
    """Delete a device from a specific chain."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("delete_chain_device", {"track_index": track_index, "device_index": device_index, "chain_index": chain_index, "chain_device_index": chain_device_index}), indent=2)

@mcp.tool()
def get_specialized_device_info(ctx: Context, track_index: int, device_index: int) -> str:
    """Get detailed parameters for specialized devices (Max, Wavetable, HybridReverb, etc.)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_specialized_device_info", {"track_index": track_index, "device_index": device_index}), indent=2)

@mcp.tool()
def set_eq8_band(ctx: Context, track_index: int, band_index: int, enabled: Optional[bool] = None, freq: Optional[float] = None, gain: Optional[float] = None, q: Optional[float] = None, filter_type: Optional[int] = None, device_index: Optional[int] = None) -> str:
    """Control EQ8 band parameters."""
    conn = get_ableton_connection()
    params = {"track_index": track_index, "band_index": band_index, "enabled": enabled, "freq": freq, "gain": gain, "q": q, "filter_type": filter_type, "device_index": device_index}
    params = {k: v for k, v in params.items() if v is not None}
    return json.dumps(conn.send_command("set_eq8_band", params), indent=2)

@mcp.tool()
def set_compressor_sidechain(ctx: Context, track_index: int, enabled: Optional[bool] = None, source_track_index: Optional[int] = None, gain: Optional[float] = None, mix: Optional[float] = None, device_index: Optional[int] = None) -> str:
    """Control Compressor sidechain settings."""
    conn = get_ableton_connection()
    params = {"track_index": track_index, "enabled": enabled, "source_track_index": source_track_index, "gain": gain, "mix": mix, "device_index": device_index}
    params = {k: v for k, v in params.items() if v is not None}
    return json.dumps(conn.send_command("set_compressor_sidechain", params), indent=2)

@mcp.tool()
def set_return_track_name(ctx: Context, index: int, name: str) -> str:
    """Set the name of a return track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_return_track_name", {"index": index, "name": name}), indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# SONG & TRANSPORT EXTENSIONS (Phase 2)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def scrub_song(ctx: Context, beats: float) -> str:
    """Jump forward or backward in the song by a number of beats."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("scrub_by", {"beats": beats}), indent=2)

@mcp.tool()
def set_groove_amount(ctx: Context, amount: float) -> str:
    """Set the global groove amount (0.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_groove_amount", {"amount": amount}), indent=2)

@mcp.tool()
def duplicate_track(ctx: Context, track_index: int, target_index: Optional[int] = None) -> str:
    """Duplicate a track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("duplicate_track", {"track_index": track_index, "target_index": target_index}), indent=2)

@mcp.tool()
def delete_track(ctx: Context, track_index: int) -> str:
    """Delete a track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("delete_track", {"track_index": track_index}), indent=2)

@mcp.tool()
def tap_tempo(ctx: Context) -> str:
    """Trigger tap tempo."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("tap_tempo", {}), indent=2)

@mcp.tool()
def nudge_tempo(ctx: Context, direction: str = "up", active: bool = True) -> str:
    """Nudge tempo up or down. direction: 'up' or 'down'."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("nudge_tempo", {"direction": direction, "active": active}), indent=2)

@mcp.tool()
def set_swing_amount(ctx: Context, amount: float) -> str:
    """Set the global groove swing amount (0.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_swing_amount", {"amount": amount}), indent=2)

@mcp.tool()
def play_selection(ctx: Context) -> str:
    """Play the current selection."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("play_selection", {}), indent=2)

@mcp.tool()
def stop_all_clips(ctx: Context, quantized: bool = True) -> str:
    """Stop all playing clips."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("stop_all_clips", {"quantized": quantized}), indent=2)

@mcp.tool()
def jump_by(ctx: Context, beats: float) -> str:
    """Jump playhead by a relative amount of beats."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("jump_by", {"beats": beats}), indent=2)

@mcp.tool()
def jump_to_next_cue(ctx: Context) -> str:
    """Jump to the next cue point."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("jump_to_next_cue", {}), indent=2)

@mcp.tool()
def jump_to_prev_cue(ctx: Context) -> str:
    """Jump to the previous cue point."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("jump_to_prev_cue", {}), indent=2)

@mcp.tool()
def set_or_delete_cue(ctx: Context) -> str:
    """Set or delete a cue point at the current playhead."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_or_delete_cue", {}), indent=2)

@mcp.tool()
def set_loop(ctx: Context, enabled: Optional[bool] = None, start: Optional[float] = None, length: Optional[float] = None) -> str:
    """Set global arrangement loop settings."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_loop", {"enabled": enabled, "start": start, "length": length}), indent=2)

@mcp.tool()
def get_loop(ctx: Context) -> str:
    """Get global arrangement loop settings."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_loop", {}), indent=2)

@mcp.tool()
def undo(ctx: Context) -> str:
    """Undo the last action in Live."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("undo", {}), indent=2)

@mcp.tool()
def redo(ctx: Context) -> str:
    """Redo the last undone action in Live."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("redo", {}), indent=2)

@mcp.tool()
def get_undo_state(ctx: Context) -> str:
    """Get the current undo/redo history status."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_undo_state", {}), indent=2)

@mcp.tool()
def get_metronome(ctx: Context) -> str:
    """Check if the metronome is enabled."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_metronome", {}), indent=2)

@mcp.tool()
def set_metronome(ctx: Context, enabled: bool) -> str:
    """Set the metronome state."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_metronome", {"enabled": enabled}), indent=2)

@mcp.tool()
def get_song_state(ctx: Context) -> str:
    """Get high-level song state (tempo, signature, playback status)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_song_state", {}), indent=2)

@mcp.tool()
def capture_and_insert_scene(ctx: Context) -> str:
    """Capture currently playing clips and insert them as a new scene."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("capture_and_insert_scene", {}), indent=2)

@mcp.tool()
def create_midi_track(ctx: Context, index: int = -1) -> str:
    """Create a new MIDI track. index: -1 for end."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("create_midi_track", {"index": index}), indent=2)

@mcp.tool()
def create_audio_track(ctx: Context, index: int = -1) -> str:
    """Create a new Audio track. index: -1 for end."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("create_audio_track", {"index": index}), indent=2)

@mcp.tool()
def set_track_name(ctx: Context, track_index: int, name: str) -> str:
    """Set the name of a track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_track_name", {"track_index": track_index, "name": name}), indent=2)

@mcp.tool()
def set_track_monitor(ctx: Context, track_index: int, state: str) -> str:
    """Set track monitor state. state: 'auto', 'in', or 'off'."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_track_monitor", {"track_index": track_index, "state": state}), indent=2)

@mcp.tool()
def set_track_color(ctx: Context, track_index: int, color_index: int) -> str:
    """Set the color of a track using an index."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_track_color", {"track_index": track_index, "color_index": color_index}), indent=2)

@mcp.tool()
def set_track_fold_state(ctx: Context, track_index: int, folded: bool) -> str:
    """Fold or unfold a track (if it's a group track)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_track_fold_state", {"track_index": track_index, "folded": folded}), indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# CLIP OPERATIONS (Phase 2)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def set_clip_audio_properties(ctx: Context, track_index: int, clip_index: int, warp_mode: Optional[int] = None, warping: Optional[bool] = None, gain: Optional[float] = None, pitch_coarse: Optional[int] = None) -> str:
    """Set audio clip properties (Warp Mode, Warping, Gain, Pitch)."""
    conn = get_ableton_connection()
    params = {
        "track_index": track_index, "clip_index": clip_index,
        "warp_mode": warp_mode, "warping": warping, "gain": gain, "pitch_coarse": pitch_coarse
    }
    # Remove None values
    params = {k: v for k, v in params.items() if v is not None}
    return json.dumps(conn.send_command("set_clip_audio_properties", params), indent=2)

@mcp.tool()
def get_notes(ctx: Context, track_index: int, clip_index: int, start_time: float = 0, time_span: float = 100) -> str:
    """Get MIDI notes from a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_notes", {"track_index": track_index, "clip_index": clip_index, "start_time": start_time, "time_span": time_span}), indent=2)

@mcp.tool()
def replace_notes(ctx: Context, track_index: int, clip_index: int, notes: str) -> str:
    """Replace notes in a clip. 'notes' should be a JSON string of tuples/lists."""
    conn = get_ableton_connection()
    try:
        notes_data = json.loads(notes)
    except:
        return "Error: notes must be a valid JSON string"
    return json.dumps(conn.send_command("replace_selected_notes", {"track_index": track_index, "clip_index": clip_index, "notes": notes_data}), indent=2)


@mcp.tool()
def quantize_clip(ctx: Context, track_index: int, clip_index: int, grid: int = 5, amount: float = 1.0) -> str:
    """
    Quantize MIDI clip.
    grid: 1=1/4, 2=1/8, 3=1/16, 4=1/32, 5=1/16T
    amount: 0.0-1.0 (Strength)
    """
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("quantize_clip", {
        "track_index": track_index, "clip_index": clip_index, "grid": grid, "amount": amount
    }), indent=2)

@mcp.tool()
def crop_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Crop clip to loop selection."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("crop_clip", {"track_index": track_index, "clip_index": clip_index}), indent=2)

@mcp.tool()
def clear_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Clear all notes/content from a clip slot."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("clear_clip", {"track_index": track_index, "clip_index": clip_index}), indent=2)

@mcp.tool()
def get_cue_points(ctx: Context) -> str:
    """Get all cue points (markers) in the arrangement."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_cue_points", {}), indent=2)

@mcp.tool()
def set_clip_name(ctx: Context, track_index: int, clip_index: int, name: str) -> str:
    """Set the name of a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_name", {"track_index": track_index, "clip_index": clip_index, "name": name}), indent=2)

@mcp.tool()
def set_clip_color(ctx: Context, track_index: int, clip_index: int, color_index: int) -> str:
    """Set the color of a clip using an index."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_color", {"track_index": track_index, "clip_index": clip_index, "color_index": color_index}), indent=2)

@mcp.tool()
def set_clip_loop(ctx: Context, track_index: int, clip_index: int, looping: bool, start: Optional[float] = None, end: Optional[float] = None) -> str:
    """Set clip looping and loop boundaries."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_loop", {"track_index": track_index, "clip_index": clip_index, "looping": looping, "loop_start": start, "loop_end": end}), indent=2)

@mcp.tool()
def set_clip_launch_mode(ctx: Context, track_index: int, clip_index: int, mode: int) -> str:
    """Set clip launch mode: 0=Trigger, 1=Gate, 2=Toggle, 3=Repeat."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_launch_mode", {"track_index": track_index, "clip_index": clip_index, "mode": mode}), indent=2)

@mcp.tool()
def set_clip_launch_quantization(ctx: Context, track_index: int, clip_index: int, quantization: int) -> str:
    """Set clip launch quantization (e.g., 0=None, 1=8 Bars, 4=1 Bar)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_launch_quantization", {"track_index": track_index, "clip_index": clip_index, "quantization": quantization}), indent=2)

@mcp.tool()
def set_clip_legato(ctx: Context, track_index: int, clip_index: int, legato: bool) -> str:
    """Set clip legato launch setting."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_legato", {"track_index": track_index, "clip_index": clip_index, "legato": legato}), indent=2)

@mcp.tool()
def set_clip_markers(ctx: Context, track_index: int, clip_index: int, start: Optional[float] = None, end: Optional[float] = None) -> str:
    """Set clip start and end markers."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_markers", {"track_index": track_index, "clip_index": clip_index, "start_marker": start, "end_marker": end}), indent=2)

@mcp.tool()
def duplicate_loop(ctx: Context, track_index: int, clip_index: int) -> str:
    """Duplicate the loop in a MIDI clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("duplicate_loop", {"track_index": track_index, "clip_index": clip_index}), indent=2)

@mcp.tool()
def transpose_clip(ctx: Context, track_index: int, clip_index: int, semitones: int) -> str:
    """Transpose all MIDI notes in a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("transpose_clip", {"track_index": track_index, "clip_index": clip_index, "semitones": semitones}), indent=2)

@mcp.tool()
def apply_legato(ctx: Context, track_index: int, clip_index: int) -> str:
    """Apply legato to MIDI notes in a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("apply_legato", {"track_index": track_index, "clip_index": clip_index}), indent=2)

@mcp.tool()
def scrub_clip(ctx: Context, track_index: int, clip_index: int, position: float) -> str:
    """Scrub to a position within a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("scrub_clip", {"track_index": track_index, "clip_index": clip_index, "position": position}), indent=2)

@mcp.tool()
def stop_scrub_clip(ctx: Context, track_index: int, clip_index: int) -> str:
    """Stop scrubbing/auditioning a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("stop_scrub", {"track_index": track_index, "clip_index": clip_index}), indent=2)

@mcp.tool()
def get_track_groups(ctx: Context) -> str:
    """Get list of track groups and their structure."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_all_groups", {}), indent=2)

@mcp.tool()
def fire_clip_by_name(ctx: Context, clip_pattern: str, track_pattern: Optional[str] = None, match_mode: str = "contains", first_only: bool = True) -> str:
    """Fire a clip by searching for its name."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("fire_clip_by_name", {"clip_pattern": clip_pattern, "track_pattern": track_pattern, "match_mode": match_mode, "first_only": first_only}), indent=2)

@mcp.tool()
def fire_scene_by_name(ctx: Context, pattern: str, match_mode: str = "contains", first_only: bool = True) -> str:
    """Fire a scene by searching for its name."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("fire_scene_by_name", {"pattern": pattern, "match_mode": match_mode, "first_only": first_only}), indent=2)

@mcp.tool()
def fire_slot(ctx: Context, track_index: int, slot_index: int, force_legato: bool = False) -> str:
    """Fire a clip slot."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("fire_slot", {"track_index": track_index, "slot_index": slot_index, "force_legato": force_legato}), indent=2)

@mcp.tool()
def stop_slot(ctx: Context, track_index: int, slot_index: int) -> str:
    """Stop a clip slot."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("stop_slot", {"track_index": track_index, "slot_index": slot_index}), indent=2)

@mcp.tool()
def create_clip_in_slot(ctx: Context, track_index: int, slot_index: int, length: float = 4.0) -> str:
    """Create a blank MIDI clip in a slot."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("create_clip_in_slot", {"track_index": track_index, "slot_index": slot_index, "length": length}), indent=2)

@mcp.tool()
def delete_clip_in_slot(ctx: Context, track_index: int, slot_index: int) -> str:
    """Delete a clip from a slot."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("delete_clip_in_slot", {"track_index": track_index, "slot_index": slot_index}), indent=2)

@mcp.tool()
def duplicate_clip_to_slot(ctx: Context, from_track: int, from_slot: int, to_track: int, to_slot: int) -> str:
    """Duplicate a clip to another slot."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("duplicate_clip_to_slot", {"from_track": from_track, "from_slot": from_slot, "to_track": to_track, "to_slot": to_slot}), indent=2)

@mcp.tool()
def set_slot_stop_button(ctx: Context, track_index: int, slot_index: int, enabled: bool) -> str:
    """Enable or disable the stop button in a slot."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_slot_stop_button", {"track_index": track_index, "slot_index": slot_index, "enabled": enabled}), indent=2)

@mcp.tool()
def set_clip_groove(ctx: Context, track_index: int, clip_index: int, groove_index: int) -> str:
    """Apply a groove from the pool to a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_groove", {"track_index": track_index, "clip_index": clip_index, "groove_index": groove_index}), indent=2)

@mcp.tool()
def commit_groove(ctx: Context, track_index: int, clip_index: int) -> str:
    """Commit the applied groove to the clip's notes."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("commit_groove", {"track_index": track_index, "clip_index": clip_index}), indent=2)

@mcp.tool()
def get_drum_rack_info(ctx: Context, track_index: int, device_index: Optional[int] = None, include_empty: bool = False) -> str:
    """Get info about drum pads and chains in a Drum Rack."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_drum_rack_info", {"track_index": track_index, "device_index": device_index, "include_empty": include_empty}), indent=2)

@mcp.tool()
def set_drum_pad_choke_group(ctx: Context, track_index: int, note: int, choke_group: int, device_index: Optional[int] = None) -> str:
    """Set choke group for a drum pad."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_drum_pad_choke_group", {"track_index": track_index, "note": note, "choke_group": choke_group, "device_index": device_index}), indent=2)

@mcp.tool()
def mute_drum_pad(ctx: Context, track_index: int, note: int, mute: bool = True, device_index: Optional[int] = None) -> str:
    """Mute or unmute a drum pad."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("mute_drum_pad", {"track_index": track_index, "note": note, "mute": mute, "device_index": device_index}), indent=2)

@mcp.tool()
def solo_drum_pad(ctx: Context, track_index: int, note: int, solo: bool = True, device_index: Optional[int] = None) -> str:
    """Solo or unsolo a drum pad."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("solo_drum_pad", {"track_index": track_index, "note": note, "solo": solo, "device_index": device_index}), indent=2)

@mcp.tool()
def get_group_info(ctx: Context, track_index: int) -> str:
    """Get info about a track group."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_group_info", {"track_index": track_index}), indent=2)

@mcp.tool()
def fold_group(ctx: Context, track_index: int) -> str:
    """Fold a track group."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("fold_group", {"track_index": track_index}), indent=2)

@mcp.tool()
def unfold_group(ctx: Context, track_index: int) -> str:
    """Unfold a track group."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("unfold_group", {"track_index": track_index}), indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# BROWSER & SAMPLE TOOLS (Phase 3)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def preview_browser_item(ctx: Context, uri: str) -> str:
    """Preview a browser item by URI."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("preview_item_by_uri", {"uri": uri}), indent=2)

@mcp.tool()
def sample_to_beat_time(ctx: Context, track_index: int, sample_time: float = 0.0, clip_index: Optional[int] = None, device_index: Optional[int] = None) -> str:
    """Convert sample time (seconds) to beat time (bars.beats.ticks)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("sample_to_beat_time", {"track_index": track_index, "sample_time": sample_time, "clip_index": clip_index, "device_index": device_index}), indent=2)

@mcp.tool()
def reverse_simpler_sample(ctx: Context, track_index: int, device_index: int) -> str:
    """Reverse the sample in a Simpler device."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("reverse_simpler_sample", {"track_index": track_index, "device_index": device_index}), indent=2)

@mcp.tool()
def crop_simpler_sample(ctx: Context, track_index: int, device_index: int) -> str:
    """Crop the sample in a Simpler device."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("crop_simpler_sample", {"track_index": track_index, "device_index": device_index}), indent=2)

@mcp.tool()
def set_simpler_playback_mode(ctx: Context, track_index: int, device_index: int, mode: int) -> str:
    """Set Simpler playback mode: 0=Classic, 1=One-Shot, 2=Slicing."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_simpler_playback_mode", {"track_index": track_index, "device_index": device_index, "mode": mode}), indent=2)

@mcp.tool()
def set_simpler_sample_markers(ctx: Context, track_index: int, device_index: int, start: float, end: float) -> str:
    """Set Simpler sample start and end markers (0.0 to 1.0)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_simpler_sample_markers", {"track_index": track_index, "device_index": device_index, "start": start, "end": end}), indent=2)

@mcp.tool()
def warp_simpler_sample(ctx: Context, track_index: int, device_index: int, enabled: bool) -> str:
    """Enable or disable warping for a Simpler sample."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("warp_simpler_sample", {"track_index": track_index, "device_index": device_index, "enabled": enabled}), indent=2)

@mcp.tool()
def get_sample_details(ctx: Context, track_index: int, clip_index: Optional[int] = None, device_index: Optional[int] = None) -> str:
    """Get detailed info about a sample (Clip or Simpler)."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_sample_details", {"track_index": track_index, "clip_index": clip_index, "device_index": device_index}), indent=2)

@mcp.tool()
def slice_sample(ctx: Context, track_index: int, action: str, slice_time: float = 0.0, clip_index: Optional[int] = None, device_index: Optional[int] = None) -> str:
    """
    Manage sample slices.
    action: "get", "insert", "remove", "clear", "reset"
    """
    conn = get_ableton_connection()
    params = {"track_index": track_index, "clip_index": clip_index, "device_index": device_index}
    
    if action == "get":
        return json.dumps(conn.send_command("get_slices", params), indent=2)
    elif action == "insert":
        params["slice_time"] = slice_time
        return json.dumps(conn.send_command("insert_slice", params), indent=2)
    elif action == "remove":
        params["slice_time"] = slice_time
        return json.dumps(conn.send_command("remove_slice", params), indent=2)
    elif action == "clear":
        return json.dumps(conn.send_command("clear_slices", params), indent=2)
    elif action == "reset":
        return json.dumps(conn.send_command("reset_slices", params), indent=2)
    else:
        return f"Unknown action: {action}"

@mcp.tool()
def get_browser_category(ctx: Context, category_name: str = "sounds", max_items: int = 50) -> str:
    """Get items from a specific browser category."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_browser_category", {"category_name": category_name, "max_items": max_items}), indent=2)

@mcp.tool()
def get_browser_state(ctx: Context) -> str:
    """Get current browser visibility and focus state."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_browser_state", {}), indent=2)

@mcp.tool()
def filter_browser(ctx: Context, filter_type: int) -> str:
    """Set browser filter type."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("filter_browser", {"filter_type": filter_type}), indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# AUTOMATION TOOLS (Phase 5)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_clip_envelope(ctx: Context, track_index: int, clip_index: int, device_id: str = "mixer", parameter_id: Union[int, str] = 0) -> str:
    """
    Get automation envelope status for a parameter.
    device_id: "mixer" or device index (e.g. 0).
    parameter_id: Parameter index or name (e.g. "Volume").
    """
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_clip_envelope", {
        "track_index": track_index, "clip_index": clip_index, "device_id": device_id, "parameter_id": parameter_id
    }), indent=2)

@mcp.tool()
def insert_envelope_step(ctx: Context, track_index: int, clip_index: int, time: float, length: float, value: float, device_id: str = "mixer", parameter_id: Union[int, str] = 0) -> str:
    """
    Insert a flat automation step.
    device_id: "mixer" or device index.
    parameter_id: parameter index or name.
    """
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_clip_envelope_step", {
        "track_index": track_index, "clip_index": clip_index, "device_id": device_id, "parameter_id": parameter_id,
        "time": time, "length": length, "value": value
    }), indent=2)

@mcp.tool()
def clear_clip_envelope(ctx: Context, track_index: int, clip_index: int, device_id: str = "mixer", parameter_id: Union[int, str] = 0) -> str:
    """Clear automation for a parameter."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("clear_clip_envelope", {
        "track_index": track_index, "clip_index": clip_index, "device_id": device_id, "parameter_id": parameter_id
    }), indent=2)

    return json.dumps(conn.send_command("clear_clip_envelope", {
        "track_index": track_index, "clip_index": clip_index, "device_id": device_id, "parameter_id": parameter_id
    }), indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# HUMANIZATION TOOLS (Phase 6)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_notes_extended(ctx: Context, track_index: int, clip_index: int, start_time: float = 0.0, time_span: float = 1000.0) -> str:
    """
    Get notes with advanced properties (ID, Probability, Deviation).
    Use this for humanization/randomization tasks.
    Returns JSON list of note objects.
    """
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_notes_extended", {
        "track_index": track_index, "clip_index": clip_index, 
        "start_time": start_time, "time_span": time_span
    }), indent=2)

@mcp.tool()
def update_notes(ctx: Context, track_index: int, clip_index: int, notes_json: str) -> str:
    """
    Update specific notes by ID.
    Used for setting Probability, Velocity Deviation, or surgical edits.
    notes_json: JSON string of list of dicts. Must include "note_id".
    Example: '[{"note_id": 123, "probability": 0.5}, {"note_id": 124, "velocity": 90}]'
    """
    conn = get_ableton_connection()
    try:
        notes_data = json.loads(notes_json)
    except:
        return "Error: notes_json must be a valid JSON string"
        
    return json.dumps(conn.send_command("update_notes", {
        "track_index": track_index, "clip_index": clip_index, 
        "notes": notes_data
    }), indent=2)

    return json.dumps(conn.send_command("update_notes", {
        "track_index": track_index, "clip_index": clip_index, 
        "notes": notes_data
    }), indent=2)

# ═══════════════════════════════════════════════════════════════════════════════
# FINAL POLISH TOOLS (Phase 7)
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_song_data(ctx: Context, key: str) -> str:
    """Get persistent string data from the song."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_data", {"key": key}), indent=2)

@mcp.tool()
def set_song_data(ctx: Context, key: str, value: str) -> str:
    """Set persistent string data in the song."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("set_data", {"key": key, "value": value}), indent=2)

@mcp.tool()
def move_device(ctx: Context, track_index: int, device_index: int, target_track_index: int, target_index: int = -1) -> str:
    """
    Move a device from one track to another.
    target_index: 0 for beginning, -1 for end.
    """
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("move_device", {
        "track_index": track_index, "device_index": device_index,
        "target_track_index": target_track_index, "target_index": target_index
    }), indent=2)

@mcp.tool()
def store_variation(ctx: Context, track_index: int, device_index: int) -> str:
    """Store a new macro variation."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("store_variation", {
        "track_index": track_index, "device_index": device_index
    }), indent=2)

@mcp.tool()
def recall_variation(ctx: Context, track_index: int, device_index: int) -> str:
    """Recall the selected variation."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("recall_variation", {
        "track_index": track_index, "device_index": device_index
    }), indent=2)

@mcp.tool()
def delete_variation(ctx: Context, track_index: int, device_index: int) -> str:
    """Delete the selected variation."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("delete_variation", {
        "track_index": track_index, "device_index": device_index
    }), indent=2)

@mcp.tool()
def randomize_macros(ctx: Context, track_index: int, device_index: int) -> str:
    """Randomize macros on a Rack."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("randomize_macros", {
        "track_index": track_index, "device_index": device_index
    }), indent=2)

@mcp.tool()
def copy_drum_pad(ctx: Context, track_index: int, device_index: int, from_note: int, to_note: int) -> str:
    """Copy a drum pad."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("copy_pad", {
        "track_index": track_index, "device_index": device_index,
        "from_note": from_note, "to_note": to_note
    }), indent=2)

@mcp.tool()
def add_notes_to_clip_tool(ctx: Context, track_index: int, clip_index: int, notes_json: str) -> str:
    """Add multiple notes to a clip using JSON array of note objects."""
    conn = get_ableton_connection()
    try:
        notes_data = json.loads(notes_json)
    except:
        return "Error: notes_json must be a valid JSON string"
    return json.dumps(conn.send_command("add_notes_to_clip", {"track_index": track_index, "clip_index": clip_index, "notes": notes_data}), indent=2)

@mcp.tool()
def select_all_notes(ctx: Context, track_index: int, clip_index: int) -> str:
    """Select all MIDI notes in a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("select_all_notes", {"track_index": track_index, "clip_index": clip_index}), indent=2)

@mcp.tool()
def deselect_all_notes(ctx: Context, track_index: int, clip_index: int) -> str:
    """Deselect all MIDI notes in a clip."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("deselect_all_notes", {"track_index": track_index, "clip_index": clip_index}), indent=2)

@mcp.tool()
def get_live_version(ctx: Context) -> str:
    """Get the version of Ableton Live."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("get_live_version", {}), indent=2)

@mcp.tool()
def focus_view(ctx: Context, view_name: str) -> str:
    """Focus a specific view (e.g., 'Session', 'Arranger', 'Detail/Clip')."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("focus_view", {"view": view_name}), indent=2)

@mcp.tool()
def zoom_view(ctx: Context, factor: float) -> str:
    """Zoom the current view."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("zoom_view", {"factor": factor}), indent=2)

@mcp.tool()
def toggle_browser(ctx: Context) -> str:
    """Toggle browser visibility."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("toggle_browser", {}), indent=2)

@mcp.tool()
def str_for_value(ctx: Context, track_index: int, device_index: int, parameter_index: int, value: float) -> str:
    """Get the display string for a parameter value (e.g., '-6.0 dB')."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("str_for_value", {"track_index": track_index, "device_index": device_index, "parameter": parameter_index, "value": value}), indent=2)

@mcp.tool()
def re_enable_automation(ctx: Context, track_index: int, device_index: int, parameter_index: int) -> str:
    """Re-enable automation for a parameter after manual override."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("re_enable_automation", {"track_index": track_index, "device_index": device_index, "parameter": parameter_index}), indent=2)

@mcp.tool()
def list_routable_devices(ctx: Context, track_index: int) -> str:
    """List devices that can be used as routing targets for the given track."""
    conn = get_ableton_connection()
    return json.dumps(conn.send_command("list_routable_devices", {"track_index": track_index}), indent=2)

# Main execution

@mcp.tool()
def generate_bassline_advanced(ctx: Context, track_index: int, clip_index: int, key: str = "C", scale: str = "major", progression: str = None, mood: str = None, style: str = "walking", velocity: int = 100, humanize: float = 0.0) -> str:
    """Advanced bassline generator (style: walking, rock, funk, reggae, puzzle, root)"""
    return gen_bass_advanced(track_index, clip_index, key, scale, progression, mood=mood, style=style, velocity=velocity, humanize=humanize)

@mcp.tool()
def generate_strings_advanced(ctx: Context, track_index: int, clip_index: int, key: str = "C", scale: str = "major", progression: str = None, mood: str = None, style: str = "pop", velocity: int = 90, humanize: float = 0.0) -> str:
    """Advanced strings generator (style: pop, classical, rock, disco, jazz)"""
    return gen_strings_advanced(track_index, clip_index, key, scale, progression, mood=mood, style=style, velocity=velocity, humanize=humanize)

@mcp.tool()
def generate_woodwinds_advanced(ctx: Context, track_index: int, clip_index: int, key: str = "C", scale: str = "major", progression: str = None, mood: str = None, style: str = "pop", velocity: int = 90, humanize: float = 0.0) -> str:
    """Advanced woodwinds generator (style: pop, classical, jazz, reggae)"""
    return gen_winds_advanced(track_index, clip_index, key, scale, progression, mood=mood, style=style, velocity=velocity, humanize=humanize)

@mcp.tool()
def generate_brass_advanced(ctx: Context, track_index: int, clip_index: int, key: str = "C", scale: str = "major", progression: str = None, mood: str = None, style: str = "pop", velocity: int = 100, humanize: float = 0.0) -> str:
    """Advanced brass generator (style: pop, rock, metal, jazz, ska, reggae, gospel)"""
    return gen_brass_advanced(track_index, clip_index, key, scale, progression, mood=mood, style=style, velocity=velocity, humanize=humanize)

@mcp.tool()
def generate_rhythmic_comp(ctx: Context, track_index: int, clip_index: int, key: str = "C", scale: str = "major", progression: str = None, mood: str = None, style: str = "ska_skank", velocity: int = 85, humanize: float = 0.3) -> str:
    """Generate rhythmic comping (chords/keys). Style: ska_skank, reggae_skank, funk_stabs, house_piano..."""
    return gen_rhythmic_comp(track_index, clip_index, key, scale, progression, mood=mood, style=style, velocity=velocity, humanize=humanize)

# ═══════════════════════════════════════════════════════════════════════════════
# DRUMMER TOOLS - Pattern-based drum generation from library
# ═══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def list_drum_genres(ctx: Context) -> str:
    """
    List all available drum pattern genres in the library.
    
    Returns a JSON list of genre names like 'latin', 'rock', 'house', etc.
    Use these genre names with generate_drum_pattern.
    """
    try:
        genres = drummer_list_genres()
        metadata = drummer_get_metadata()
        return json.dumps({
            "genres": genres,
            "total_patterns": metadata.get("total_patterns", 0),
            "genres_count": len(genres)
        }, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def list_drum_patterns(ctx: Context, genre: str, variation: Optional[str] = None) -> str:
    """
    List all drum patterns in a specific genre.
    
    Args:
        genre: Genre name (e.g., 'latin', 'rock', 'house')
        variation: Optional filter - 'A', 'B', or 'fill'
    
    Returns list of pattern names and variations.
    """
    try:
        patterns = drummer_list_patterns(genre, variation)
        return json.dumps({"genre": genre, "patterns": patterns, "count": len(patterns)}, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def search_drum_patterns(ctx: Context, query: str, genre: Optional[str] = None, limit: int = 20) -> str:
    """
    Search for drum patterns by name.
    
    Args:
        query: Search query (partial match)
        genre: Optional genre filter
        limit: Maximum results
    
    Returns matching patterns with genre info.
    """
    try:
        results = drummer_search_patterns(query, genre, limit)
        return json.dumps({"results": results, "count": len(results)}, indent=2)
    except Exception as e:
        return f"Error: {e}"

@mcp.tool()
def generate_drum_pattern(
    ctx: Context,
    track_index: int,
    clip_index: int,
    genre: str,
    pattern_name: Optional[str] = None,
    variation: Optional[str] = None,
    bars: int = 4,
    velocity_scale: float = 1.0,
    humanize: float = 0.1,
    swing: float = 0.0
) -> str:
    """
    Generate a drum pattern from the library onto a track.
    
    Args:
        track_index: Target track (must have drum instrument)
        clip_index: Target clip slot
        genre: Genre name (use list_drum_genres to see options)
        pattern_name: Specific pattern (optional - random if None)
        variation: Filter by 'A', 'B', or 'fill' if pattern_name is None
        bars: Number of bars to generate (pattern loops)
        velocity_scale: Velocity multiplier (0.5-1.5 typical)
        humanize: Timing/velocity humanization (0.0-1.0)
        swing: Swing amount (0.0-1.0)
    
    Returns status message with pattern details.
    """
    return gen_drum_pattern(
        track_index=track_index,
        clip_index=clip_index,
        genre=genre,
        pattern_name=pattern_name,
        variation=variation,
        bars=bars,
        velocity_scale=velocity_scale,
        humanize=humanize,
        swing=swing
    )

@mcp.tool()
def generate_drum_fill(
    ctx: Context,
    track_index: int,
    clip_index: int,
    genre: str,
    bars: int = 1
) -> str:
    """
    Generate a drum fill from the library.
    
    Convenience function that selects patterns with variation='fill'.
    Great for transitions between sections.
    
    Args:
        track_index: Target track
        clip_index: Target clip slot
        genre: Genre name
        bars: Fill length (typically 1 bar)
    """
    return gen_drum_fill(
        track_index=track_index,
        clip_index=clip_index,
        genre=genre,
        bars=bars
    )

@mcp.tool()
def generate_drum_section(
    ctx: Context,
    track_index: int,
    clip_indices: str,
    genre: str,
    include_fill: bool = True,
    bars_per_clip: int = 4
) -> str:
    """
    Generate a multi-clip drum section with A/B variations.
    
    Creates varied patterns across multiple clips, optionally
    ending with a fill. Great for building song sections.
    
    Args:
        track_index: Target track
        clip_indices: Comma-separated clip indices (e.g., '0,1,2,3')
        genre: Genre name
        include_fill: Add fill at the end
        bars_per_clip: Bars per clip
    """
    try:
        indices = [int(i.strip()) for i in clip_indices.split(",")]
        return gen_drum_section(
            track_index=track_index,
            clip_indices=indices,
            genre=genre,
            include_fill=include_fill,
            bars_per_clip=bars_per_clip
        )
    except ValueError:
        return "Error: clip_indices must be comma-separated integers (e.g., '0,1,2,3')"

import argparse

def main():
    """Run the MCP server"""
    parser = argparse.ArgumentParser(description="Ableton MCP Server")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse"], help="Transport mode (stdio or sse)")
    parser.add_argument("--port", type=int, default=8000, help="Port for SSE transport")
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=args.port)
    else:
        mcp.run() # Defaults to stdio

if __name__ == "__main__":
    main()

