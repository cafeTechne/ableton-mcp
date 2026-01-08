"""
Woodwind Rhythm Patterns
========================
Rhythmic definitions for woodwind figures.
"""

# Patterns: fractional offsets relative to chord duration (0.0 to 1.0)
PATTERNS = {
    "whole_note": [0.0],
    
    "rock_quarters": [0.0, 0.25, 0.5, 0.75],
    
    "reggae_skank": [0.125, 0.375, 0.625, 0.875], # Offbeats
    
    "straight_eighths": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875], # 8ths
    
    "swing_eighths": [0.0, 0.166, 0.25, 0.416, 0.5, 0.666, 0.75, 0.916], # Triplet feel approx
    
    "trance_gate": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875],
    
    "eighth_note_run": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]
}

def get_pattern(pattern_name: str) -> list:
    """Get pattern by name, default to whole_note."""
    return PATTERNS.get(pattern_name, PATTERNS["whole_note"])
