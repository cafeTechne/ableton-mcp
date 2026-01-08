"""
Rhythmic Comp Generator - Pattern-based chord/keys generation.

Provides genre-specific rhythmic patterns for comping instruments like keys, guitar, organ.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger("mcp_server.rhythmic_comp")

# Rhythmic Pattern Definitions
# Format: List of (beat_offset, duration, velocity_modifier)
# beat_offset: Position within a bar (0-3 for 4/4)
# duration: Note length in beats
# velocity_modifier: Multiplier for base velocity (1.0 = normal)

COMP_PATTERNS = {
    # SKA SKANK - Classic offbeat pattern
    # Emphasizes the "and" of each beat (upstrokes)
    "ska_skank": {
        "pattern": [
            (0.5, 0.25, 0.9),   # & of 1
            (1.5, 0.25, 0.95),  # & of 2
            (2.5, 0.25, 0.9),   # & of 3
            (3.5, 0.25, 1.0),   # & of 4 (accent)
        ],
        "humanize_profile": "ska",
        "description": "Classic Jamaican ska offbeat skank"
    },
    
    # REGGAE SKANK - Similar but slightly different feel
    "reggae_skank": {
        "pattern": [
            (0.5, 0.35, 0.85),  # & of 1 (longer, softer)
            (1.5, 0.35, 0.9),   # & of 2
            (2.5, 0.35, 0.85),  # & of 3
            (3.5, 0.35, 0.95),  # & of 4
        ],
        "humanize_profile": "loose",
        "description": "Laid-back reggae offbeat"
    },
    
    # FUNK STABS - Syncopated patterns with accents
    "funk_stabs": {
        "pattern": [
            (0.0, 0.25, 1.0),   # 1 (strong)
            (0.75, 0.25, 0.8),  # Just before 2
            (1.5, 0.25, 0.9),   # & of 2
            (3.0, 0.25, 0.95),  # 4
            (3.5, 0.25, 0.85),  # & of 4
        ],
        "humanize_profile": "tight",
        "description": "Syncopated funk chord stabs"
    },
    
    # FUNK CLAVINET - E-mu style pattern
    "funk_clav": {
        "pattern": [
            (0.0, 0.15, 1.0),   # 1 (short, percussive)
            (0.5, 0.15, 0.75),  # & of 1 (ghost)
            (1.0, 0.15, 0.9),   # 2
            (1.75, 0.15, 0.7),  # Before & of 2 (ghost)
            (2.5, 0.15, 0.85),  # & of 3
            (3.0, 0.15, 0.95),  # 4
            (3.5, 0.15, 0.8),   # & of 4
        ],
        "humanize_profile": "tight",
        "description": "Clavinet-style funk pattern"
    },
    
    # HOUSE PIANO - 4-on-the-floor influenced
    "house_piano": {
        "pattern": [
            (0.0, 0.5, 1.0),    # 1 (strong, longer)
            (1.0, 0.25, 0.8),   # 2 (lighter)
            (1.5, 0.5, 0.9),    # & of 2 (accent)
            (2.5, 0.25, 0.75),  # & of 3 (ghost)
            (3.0, 0.5, 0.85),   # 4
        ],
        "humanize_profile": "tight",
        "description": "Classic house piano chords"
    },
    
    # DISCO OCTAVES - High-energy octave pattern
    "disco_octaves": {
        "pattern": [
            (0.0, 0.2, 1.0),
            (0.5, 0.2, 0.85),
            (1.0, 0.2, 0.95),
            (1.5, 0.2, 0.85),
            (2.0, 0.2, 0.95),
            (2.5, 0.2, 0.85),
            (3.0, 0.2, 1.0),
            (3.5, 0.2, 0.9),
        ],
        "humanize_profile": "tight",
        "description": "Driving disco octave pattern"
    },
    
    # GOSPEL COMPING - Soulful sustained chords
    "gospel_comp": {
        "pattern": [
            (0.0, 1.5, 1.0),    # 1 (long, soulful)
            (2.0, 0.5, 0.85),   # 3 (answer)
            (3.0, 0.75, 0.9),   # 4 (lead into next bar)
        ],
        "humanize_profile": "loose",
        "description": "Soulful gospel comping"
    },
    
    # MOTOWN - Classic Hitsville feel
    "motown": {
        "pattern": [
            (0.0, 0.4, 1.0),    # 1
            (1.0, 0.3, 0.85),   # 2
            (2.0, 0.4, 0.95),   # 3
            (3.0, 0.3, 0.8),    # 4
        ],
        "humanize_profile": "human",
        "description": "Classic Motown quarter-note feel"
    },
    
    # BOSSA NOVA - Brazilian jazz pattern
    "bossa_nova": {
        "pattern": [
            (0.0, 0.75, 0.9),   # 1
            (1.5, 0.5, 0.8),    # Syncopated
            (2.5, 0.5, 0.85),   # Syncopated
            (3.5, 0.4, 0.75),   # Anticipation
        ],
        "humanize_profile": "swing",
        "description": "Bossa nova comping pattern"
    },
    
    # STRAIGHT QUARTERS - Simple quarter note pattern
    "quarters": {
        "pattern": [
            (0.0, 0.9, 1.0),
            (1.0, 0.9, 0.85),
            (2.0, 0.9, 0.9),
            (3.0, 0.9, 0.85),
        ],
        "humanize_profile": "straight",
        "description": "Simple quarter note comping"
    },
    
    # BALLAD - Sustained chords for slow songs
    "ballad": {
        "pattern": [
            (0.0, 3.5, 0.7),    # Long sustained chord
        ],
        "humanize_profile": "loose",
        "description": "Sustained ballad chords"
    },
}


def get_comp_pattern(style: str) -> Dict[str, Any]:
    """Get a comp pattern by name, with fuzzy matching."""
    style_lower = style.lower().replace(" ", "_").replace("-", "_")
    
    # Direct match
    if style_lower in COMP_PATTERNS:
        return COMP_PATTERNS[style_lower]
    
    # Fuzzy match
    for name, pattern in COMP_PATTERNS.items():
        if style_lower in name or name in style_lower:
            return pattern
    
    # Default
    logger.warning(f"Unknown comp style '{style}', defaulting to 'quarters'")
    return COMP_PATTERNS["quarters"]


def generate_comp_notes(
    chord_notes: List[int],
    pattern: List[Tuple[float, float, float]],
    bar_offset: float,
    base_velocity: int = 80
) -> List[Dict[str, Any]]:
    """
    Generate note events for a single bar of comping.
    
    Args:
        chord_notes: List of MIDI pitches for the chord
        pattern: List of (beat_offset, duration, vel_mod) tuples
        bar_offset: The beat position where this bar starts
        base_velocity: Base velocity before modifiers
    
    Returns:
        List of note dictionaries
    """
    notes = []
    
    for beat_offset, duration, vel_mod in pattern:
        velocity = int(base_velocity * vel_mod)
        velocity = max(1, min(127, velocity))
        
        for pitch in chord_notes:
            notes.append({
                "pitch": pitch,
                "start_time": bar_offset + beat_offset,
                "duration": duration,
                "velocity": velocity,
                "mute": False
            })
    
    return notes


def list_comp_styles() -> List[str]:
    """Return a list of available comp styles."""
    return list(COMP_PATTERNS.keys())
