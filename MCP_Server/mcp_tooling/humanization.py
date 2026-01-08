import random
import math
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class HumanizeProfile:
    """
    Configuration for humanizing MIDI notes.
    """
    velocity_center: int = 90
    velocity_range: int = 15
    timing_jitter: float = 0.02  # Beats (approx 10-20ms at 120bpm is 0.02-0.04)
    
    # Groove
    groove_type: str = "straight"  # straight, swing, push, pull, loose
    groove_amount: float = 0.0     # 0.0 to 1.0 (Strength of groove)
    
    # Velocity Mapping (Grid position -> Velocity Offset)
    # 0.0 is Downbeat. 0.5 is Offbeat (8th). 0.25/0.75 are 16ths.
    velocity_map: Dict[float, int] = field(default_factory=dict)
    
    # Ghost Notes
    ghost_probability: float = 0.0
    ghost_velocity: int = 40

    @staticmethod
    def get_preset(name: str):
        p = HumanizeProfile()
        name = name.lower()
        
        if name == "tight":
            p.timing_jitter = 0.005
            p.velocity_range = 5
        
        elif name == "loose":
            p.timing_jitter = 0.04
            p.velocity_range = 25
            p.groove_type = "loose"
            p.groove_amount = 0.3
            
        elif name == "swing":
            p.groove_type = "swing"
            p.groove_amount = 0.5
            p.timing_jitter = 0.015
            p.velocity_map = {0.0: 10, 0.5: -5} # Strong downbeat
            
        elif name == "ska":
             # Ska emphasizes the offbeat
             p.groove_type = "pull" # Slight laid back
             p.groove_amount = 0.1
             p.velocity_map = {0.0: -10, 0.5: 20} # Accent offbeats
             p.timing_jitter = 0.015
             
        elif name == "human":
            p.timing_jitter = 0.025
            p.velocity_range = 20
            
        return p

def apply_humanization(notes: List[Dict[str, Any]], profile: Optional[HumanizeProfile] = None, amount: float = 1.0) -> List[Dict[str, Any]]:
    """
    Apply humanization to a list of notes in-place.
    amount: Global scaler for the profile's intensity (0.0 to 1.0).
    """
    if not notes or not profile:
        return notes
        
    for note in notes:
        start = float(note["start_time"])
        vel = int(note["velocity"])
        
        # 1. Groove / Grid Shift
        groove_offset = 0.0
        
        # Determine grid position (assuming 4/4 measure, modulo 1 beat or 4 beats?)
        # Let's look at 16th note grid
        beat_pos = start % 1.0
        
        if profile.groove_type == "swing":
            # Delay even 8ths (0.5, 1.5, etc)
            # Simple shuffle: map 0.5 -> 0.66
            # We apply offset based on proximity to 0.5
            dist_to_offbeat = abs(beat_pos - 0.5)
            if dist_to_offbeat < 0.1:
                # Max swing is usually pushing 0.5 to 0.66 (triplet)
                # 0.16 offset max.
                groove_offset = 0.16 * profile.groove_amount * amount
                
        elif profile.groove_type == "push":
            # Ahead of beat
            groove_offset = -0.03 * profile.groove_amount * amount
            
        elif profile.groove_type == "pull":
            # Behind beat
            groove_offset = 0.03 * profile.groove_amount * amount
            
        # 2. Timing Jitter (Gaussian)
        jitter = random.gauss(0, profile.timing_jitter * amount)
        
        # Apply timing
        new_start = start + groove_offset + jitter
        note["start_time"] = max(0.0, new_start)
        
        # 3. Velocity Logic
        # Base jitter
        vel_jitter = random.randint(-profile.velocity_range, profile.velocity_range) * amount
        
        # Grid Map
        map_offset = 0
        if profile.velocity_map:
            # Find closest key in map
            # Keys are 0.0 to 1.0 usually (beat relative)
            # or 0.0, 0.5, 0.25
            
            # Normalize start to beat
            beat_phase = start % 1.0 # 0.0 to 0.99
            
            # Check for matches
            for grid_pt, offset in profile.velocity_map.items():
                if abs(beat_phase - grid_pt) < 0.05:
                    map_offset = offset
                    break
        
        new_vel = vel + vel_jitter + (map_offset * amount)
        
        # Ghost Notes Logic (Occasional quiet notes? Or is this done in generation?)
        # If we are post-processing, we can't easily Insert notes without context.
        # But we can turn existing low-vel notes into ghosts?
        # Leaving Ghost Note insertion to the generator (Drum Polish goal).
        
        note["velocity"] = max(1, min(127, int(new_vel)))
        
    return notes
