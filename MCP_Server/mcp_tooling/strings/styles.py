"""
String Style Profiles
=====================
Data-driven definitions for string section behavior.
"""

from typing import List, Dict, Any

class StyleProfile:
    def __init__(
        self,
        name: str,
        texture: str = "pad", # pad, stab, pulse
        rhythm_pattern: str = "whole_note",
        voicing_strategy: str = "closed", # closed, open, drop2, power, cluster
        density: List[str] = ["vc", "vla", "vl2", "vl1"], # active parts
        articulation: Dict[str, Any] = None, # gate, dynamics
        register_bias: str = "mid" # low, mid, high
    ):
        self.name = name
        self.texture = texture
        self.rhythm_pattern = rhythm_pattern
        self.voicing_strategy = voicing_strategy
        self.density = density
        self.articulation = articulation or {"gate": 1.0, "attack": "soft"}
        self.register_bias = register_bias

# Pre-defined Profiles
PROFILES = {
    "pop": StyleProfile(
        name="pop",
        texture="pad",
        rhythm_pattern="whole_note",
        voicing_strategy="closed",
        density=["vc", "vla", "vl2", "vl1"],
        articulation={"gate": 0.95, "attack": "soft"}
    ),
    "rock": StyleProfile(
        name="rock",
        texture="pad",
        rhythm_pattern="rock_quarters",
        voicing_strategy="power",
        density=["vc", "vla", "vl2", "vl1"], # heavy
        articulation={"gate": 0.9, "attack": "marked"}
    ),
    "disco": StyleProfile(
        name="disco",
        texture="stab",
        rhythm_pattern="disco_quarters",
        voicing_strategy="closed", # tight high stabs
        density=["vl1", "vl2", "vla"], # often no cello in stabs
        articulation={"gate": 0.3, "attack": "hard"},
        register_bias="high"
    ),
    "house": StyleProfile(
        name="house",
        texture="stab",
        rhythm_pattern="house_offbeats",
        voicing_strategy="closed",
        density=["vl1", "vl2", "vla"],
        articulation={"gate": 0.4, "attack": "hard"},
        register_bias="mid"
    ),
    "jazz": StyleProfile(
        name="jazz",
        texture="pad",
        rhythm_pattern="whole_note", # or comping?
        voicing_strategy="drop2",
        density=["vc", "vla", "vl2", "vl1"],
        articulation={"gate": 0.9, "attack": "soft"}
    ),
    "reggae": StyleProfile(
        name="reggae",
        texture="stab", # or bubble
        rhythm_pattern="reggae_skank",
        voicing_strategy="closed", # thin
        density=["vl1", "vl2"], # sparse
        articulation={"gate": 0.2, "attack": "soft"},
        register_bias="high"
    ),
    "epic": StyleProfile(
        name="epic",
        texture="pad",
        rhythm_pattern="whole_note",
        voicing_strategy="power",
        density=["vc", "vla", "vl2", "vl1"],
        articulation={"gate": 1.0, "attack": "slow"}
    )
}

def get_style_profile(name: str) -> StyleProfile:
    """Get profile by name, fallback to pop."""
    # Fuzzy match?
    name_lower = name.lower()
    if name_lower in PROFILES:
        return PROFILES[name_lower]
    
    # Keyword match
    for key, profile in PROFILES.items():
        if key in name_lower:
            return profile
            
    return PROFILES["pop"]
