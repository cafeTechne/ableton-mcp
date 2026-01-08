from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class WoodwindProfile:
    name: str
    active_instruments: List[str] # ["fl", "ob", "cl", "bn"]
    roles: Dict[str, str] # "fl": "lead", "bn": "bass"
    tessitura: Dict[str, int] # "fl": 84, "cl": 60 (Preferred centers)
    texture: str # "homophonic", "polyphonic"
    rhythm_pattern: str # "whole_note", "eighth_note_run"
    density: List[str] # Instruments to actually play? Or density setting?
    articulation: Dict[str, float] # gate, attack
    register_bias: str # "high", "low", "wide"

PROFILES = {
    "pop": WoodwindProfile(
        name="pop",
        active_instruments=["fl", "cl"],
        roles={"fl": "lead", "cl": "obligato"},
        tessitura={"fl": 84, "cl": 64}, 
        texture="polyphonic", # Distinct lines
        rhythm_pattern="whole_note", # Simple pads/lines
        density=["fl", "cl"],
        articulation={"gate": 0.9},
        register_bias="high"
    ),
    "rock": WoodwindProfile(
        name="rock",
        active_instruments=["fl"],
        roles={"fl": "lead"},
        tessitura={"fl": 88},
        texture="homophonic",
        rhythm_pattern="rock_quarters",
        density=["fl"],
        articulation={"gate": 0.5},
        register_bias="high"
    ),
    "classical": WoodwindProfile(
        name="classical",
        active_instruments=["fl", "ob", "cl", "bn"],
        roles={"fl": "lead", "ob": "counter", "cl": "inner", "bn": "bass"},
        tessitura={"fl": 84, "ob": 74, "cl": 60, "bn": 48},
        texture="homophonic", # Quartet style
        rhythm_pattern="whole_note",
        density=["fl", "ob", "cl", "bn"],
        articulation={"gate": 0.95},
        register_bias="wide"
    ),
    "jazz": WoodwindProfile(
        name="jazz",
        active_instruments=["fl", "cl"], # Flute/Clarinet doubling
        roles={"fl": "lead", "cl": "lead"}, # Unison or harmonies
        tessitura={"fl": 76, "cl": 64},
        texture="homophonic",
        rhythm_pattern="swing_eighths",
        density=["fl", "cl"],
        articulation={"gate": 0.7},
        register_bias="mid"
    ),
    "reggae": WoodwindProfile(
        name="reggae",
        active_instruments=["fl", "ob"], # Horn section-ish
        roles={"fl": "lead", "ob": "lead"},
        tessitura={"fl": 80, "ob": 72},
        texture="homophonic",
        rhythm_pattern="reggae_skank",
        density=["fl", "ob"],
        articulation={"gate": 0.2},
        register_bias="high"
    ),
    "edm": WoodwindProfile(
        name="edm",
        active_instruments=["fl"],
        roles={"fl": "ostinato"},
        tessitura={"fl": 90}, 
        texture="monophonic",
        rhythm_pattern="trance_gate",
        density=["fl"],
        articulation={"gate": 0.4},
        register_bias="very_high"
    ),
}

def get_style_profile(name: str) -> WoodwindProfile:
    return PROFILES.get(name, PROFILES["pop"])
