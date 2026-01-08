"""
String Rhythm Patterns
======================
Rhythmic definitions for different genres.
Offsets are in beats.
"""

# Dictionary of patterns.
# key: pattern name
# value: list of trigger offsets (beats)
# Stabs usually imply short duration.
# Pads imply full duration.

PATTERNS = {
    "whole_note": [0.0],
    
    "disco_quarters": [0.0, 0.25, 0.5, 0.75], # 1, 2, 3, 4 (Bar relative)
    
    "house_offbeats": [0.125, 0.375, 0.625, 0.875], # 8th offbeats? No, House usually & of beat. 
    # Beat 1=0.0, Beat 1&=0.125 (if bar=1.0). 
    # Let's standardize: 1.0 = 1 Bar (4 beats).
    # Beat 1 = 0.0
    # Beat 2 = 0.25
    # Beat 1 "and" = 0.125 (1/8th note)
    
    # House Offbeats (Upbeats): 1&, 2&, 3&, 4& ? Or just 2 and 4?
    # Usually "&" of every beat.
    "house_offbeats": [0.125, 0.375, 0.625, 0.875],
    
    "ska_upstrokes": [0.125, 0.375, 0.625, 0.875], 
    
    "rock_quarters": [0.0, 0.25, 0.5, 0.75], 
    
    "driving_eighths": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875],
    
    "reggae_skank": [0.125, 0.375, 0.625, 0.875],
    
    # Trance/Epic
    "trance_gate": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]
}

def get_pattern(style: str) -> list:
    """
    Get offsets for style (fractions of a bar 0.0-1.0).
    The SectionConductor maps these to beats based on beats_per_bar.
    """
    if style in ["disco", "funk"]:
        return PATTERNS["disco_quarters"]
    elif style in ["house"]:
        return PATTERNS["house_offbeats"]
    elif style in ["ska"]:
        return PATTERNS["ska_upstrokes"]
    elif style in ["rock", "driving"]:
        return PATTERNS["driving_eighths"]
    elif style in ["reggae", "dub"]:
        return PATTERNS["reggae_skank"]
    # Fallback to sustain (whole)
    return PATTERNS["whole_note"] 
