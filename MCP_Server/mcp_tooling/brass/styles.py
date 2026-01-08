"""
Brass Style Profiles
====================
Definitions for brass genre behaviors.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class BrassProfile:
    name: str
    active_instruments: List[str] # ["tpt", "tbn", "hn"]
    roles: Dict[str, str] # "tpt": "lead"
    texture: str # "hit", "swell", "pad"
    rhythm_pattern: str # Key in rhythm.py
    voicing_strategy: str # "power_stack", "triad", "shell"
    gate: float # 0.1 for stabs, 1.0 for pads
    density: int # Max voices active per hit
    register_bias: str # "high", "low", "wide"

PROFILES = {
    "pop": BrassProfile(
        name="pop",
        active_instruments=["tpt", "hn", "tbn"],
        roles={"tpt": "lead", "hn": "inner", "tbn": "support"},
        texture="hit", 
        rhythm_pattern="hit_1_and", 
        voicing_strategy="triad",
        gate=0.3, 
        density=3,
        register_bias="mid"
    ),
    "rock": BrassProfile(
        name="rock",
        active_instruments=["tpt", "tbn"],
        roles={"tpt": "lead", "tbn": "bass"},
        texture="hit",
        rhythm_pattern="hit_1", 
        voicing_strategy="power_stack",
        gate=0.2,
        density=2,
        register_bias="mid"
    ),
    "metal": BrassProfile(
        name="metal",
        active_instruments=["tbn", "hn"], 
        roles={"tbn": "bass", "hn": "lead"},
        texture="hit", # Stabs not swells
        rhythm_pattern="whole_note", 
        voicing_strategy="power_stack", 
        gate=0.8,
        density=2,
        register_bias="low"
    ),
    "jazz": BrassProfile(
        name="jazz",
        active_instruments=["tpt", "tbn"],
        roles={"tpt": "lead", "tbn": "counter"},
        texture="riff",
        rhythm_pattern="hit_1_and", # Sparse comping
        voicing_strategy="shell",
        gate=0.4,
        density=2,
        register_bias="mid"
    ),
    "ska": BrassProfile(
        name="ska",
        active_instruments=["tpt", "tbn"],
        roles={"tpt": "lead", "tbn": "harmony"},
        texture="hit",
        rhythm_pattern="ska_offbeats",
        voicing_strategy="triad",
        gate=0.15,
        density=2,
        register_bias="mid"
    ),
    "reggae": BrassProfile(
        name="reggae",
        active_instruments=["tpt", "tbn"],
        roles={"tpt": "lead", "tbn": "harmony"},
        texture="hit",
        rhythm_pattern="ska_offbeats",
        voicing_strategy="triad",
        gate=0.2,
        density=2,
        register_bias="mid"
    ),
    "gospel": BrassProfile(
        name="gospel",
        active_instruments=["tpt", "hn", "tbn"],
        roles={"tpt": "lead", "hn": "inner", "tbn": "bass"},
        texture="shout",
        rhythm_pattern="gospel_shout",
        voicing_strategy="triad", 
        gate=0.4,
        density=3,
        register_bias="wide"
    ),
    "edm": BrassProfile(
        name="edm",
        active_instruments=["tpt"], 
        roles={"tpt": "lead"},
        texture="hit",
        rhythm_pattern="edm_gate_8ths",
        voicing_strategy="power_stack",
        gate=0.5,
        density=1,
        register_bias="high"
    ),
    "classical": BrassProfile(
        name="classical",
        active_instruments=["tpt", "hn", "tbn", "tba"],
        roles={"tpt": "cue", "hn": "glue", "tbn": "weight", "tba": "bass"},
        texture="pad",
        rhythm_pattern="whole_note",
        voicing_strategy="triad",
        gate=0.95,
        density=4,
        register_bias="wide"
    )
}

def get_style_profile(name: str) -> BrassProfile:
    name_lower = name.lower()
    if name_lower in PROFILES: return PROFILES[name_lower]
    for key, p in PROFILES.items():
        if key in name_lower: return p
    return PROFILES["pop"]
