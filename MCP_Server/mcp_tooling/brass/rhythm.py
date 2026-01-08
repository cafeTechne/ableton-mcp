"""
Brass Rhythm Patterns
=====================
Fractional start times relative to chord duration (0.0 to 1.0).
"""

PATTERNS = {
    # Hits
    "hit_1": [0.0],
    "hit_1_and": [0.0, 0.5], # 1 and 3 in 4/4
    "hit_2_4": [0.25, 0.75], # Backbeats (2, 4 in 4/4)
    
    "ska_offbeats": [0.125, 0.375, 0.625, 0.875], # &, &, &, &
    
    # Stylistic
    "disco_hits": [0.0, 0.5], # 1 and 3 check
    "gospel_shout": [0.0, 0.375, 0.5, 0.875], # Syncopated
    
    # EDM
    "edm_gate_8ths": [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875],
    
    # Sustains
    "whole_note": [0.0]
}

def get_pattern(name: str) -> list:
    return PATTERNS.get(name, PATTERNS["whole_note"])
