"""
Performance Humanization
========================
Injects Ableton Live 11+ performance fields with musical awareness.
- Robust grouping (Global 1/16th ticks, articulation buckets)
- Texture-aware thinning (Reggae vs Ska split)
- Correct dynamic physics (Loud = Tight)
- Modes: Deterministic (Mute) vs Probability (Live Chance)
"""

import random
from typing import List, Dict, Any, Optional, Tuple

def apply_performance_humanization(
    notes: List[Dict],
    style: str,
    section_name: str, # "brass", "woodwinds", "strings"
    profile_name: Optional[str] = None, # e.g. "pop", "jazz"
    mode: str = "deterministic" # "deterministic" or "probability"
) -> List[Dict]:
    """
    Post-process notes to add humanization fields.
    Uses correlated probability grouping (ensemble coherence).
    """
    style_key = (profile_name or style or "").lower().replace("-", "_").strip()
    
    # 0. Detect Style Flags
    is_jazz = any(k in style_key for k in ["jazz", "neo_soul", "rnb", "comp"])
    is_ska = "ska" in style_key or "rocksteady" in style_key
    is_reggae = "reggae" in style_key
    is_pop = "pop" in style_key
    
    # 1. Group Events for Correlated Probability
    # Key = (tick, bucket_id)
    # User Point 2: Unify tick units (Global 0.25 ticks)
    
    events: Dict[Tuple[int, str], List[Dict]] = {}
    
    # Global Tick Base: 1/16th (0.25)
    BASE_GRID = 0.25
    
    for note in notes:
        start = note["start_time"]
        artic = note.get("_articulation", "sustain")
        
        # Determine Bucket
        bucket = "other"
        if "hit" in artic or "stab" in artic or "spicc" in artic:
            bucket = "hit"
        elif "pad" in artic or "swell" in artic or "legato" in artic:
            bucket = "pad"
            
        # Determine Quantization Factor
        # Hits stay tight (0.25 -> factor 1)
        # Pads/Jazz loosen (0.5 -> factor 2)
        factor = 1 # Default 0.25
        
        if bucket == "pad": 
             factor = 2 # 0.5 grid
        elif is_jazz and bucket != "hit":
             factor = 2
             
        # Snap to grid, expressed in Global Ticks (Integer Safe)
        # User Point 1: Nearest Snap, Tie Goes Earlier
        
        # Add epsilon for potentially noisy floats: 1.99999 -> 2.0
        ticks = int((start / BASE_GRID) + 0.5 + 1e-9) 
        
        q = ticks // factor
        r = ticks % factor
        
        # Tie-break logic: if r*2 <= factor, snap down. Else snap up.
        # e.g. ticks=5 (1.25), factor=2. q=2, r=1. r*2=2 <= 2. Snap to 2*2=4 (1.0). Correct.
        # e.g. ticks=6 (1.5), factor=2. q=3, r=0. r*2=0 <= 2. Snap to 6. Correct.
        # e.g. ticks=7 (1.75), factor=2. q=3, r=1. r*2=2 <= 2. Snap to 3*2=6 (1.5). Correct.
        
        target_tick = (q * factor) if (r * 2) <= factor else ((q + 1) * factor)
        
        key = (target_tick, bucket)
        if key not in events: events[key] = []
        events[key].append(note)

    processed = []
    
    # Sort keys: by tick, then priority order
    bucket_order = {"hit": 0, "other": 1, "pad": 2}
    sorted_keys = sorted(events.keys(), key=lambda k: (k[0], bucket_order.get(k[1], 1)))
    
    # Phrasing State (Local to stream)
    state = {
        "hit": {"hits": 0, "rests": 0},
        "pad": {"hits": 0, "rests": 0},
        "other": {"hits": 0, "rests": 0}
    }
    
    for (tick, bucket) in sorted_keys:
        group_notes = events[(tick, bucket)]
        q_start = tick * BASE_GRID # Time in beats
        
        # Grid reconstruction using standard tick counts
        ticks_per_beat = int(round(1.0 / BASE_GRID)) # 4
        ticks_per_bar = int(round(4.0 / BASE_GRID)) # 16
        
        is_bar_downbeat = (tick % ticks_per_bar) == 0
        is_beat = (tick % ticks_per_beat) == 0
        # User Point 5: "And of Beat" (Offset 0.5) detection
        # tick % 4 == 2 is exactly midway (1/8th note offbeat)
        is_and_of_beat = (tick % ticks_per_beat) == (ticks_per_beat // 2)
        
        # State Access
        # User Point 3: Disable state-based phrasing/clamping in probability mode
        use_phrasing = (mode == "deterministic")
        
        if use_phrasing:
            hits = state[bucket]["hits"]
            rests = state[bucket]["rests"]
        else:
            hits = 0
            rests = 0
        
        # Determine Group Probability Baseline
        group_prob = 1.0
        
        # Style overrides
        if section_name == "brass":
            if is_jazz and bucket == "hit":
                base = 0.6 if is_bar_downbeat else 0.45
                if use_phrasing:
                    if hits >= 3: base *= 0.5
                    if rests >= 2: base *= 1.5
                group_prob = base
                
            elif is_ska and bucket == "hit":
                if is_and_of_beat: # Only offbeats are high prob
                    group_prob = 0.90 
            
            elif is_reggae and bucket == "hit":
                if is_and_of_beat:
                     group_prob = 0.85
                     
            elif is_pop and bucket == "hit":
                group_prob = 0.95
        
        elif section_name == "woodwinds":
             if is_jazz: group_prob = 0.6
             else: group_prob = 0.95 

        # Roll for Group (Deterministic Only)
        # Event Active means "The Chord Happens"
        event_active = True
        
        if mode == "deterministic":
            if group_prob < 1.0:
                if random.random() > group_prob:
                    event_active = False
        
        # Update State (Simulated based on deterministic outcome)
        if mode == "deterministic":
            if event_active:
                state[bucket]["hits"] += 1
                state[bucket]["rests"] = 0
            else:
                state[bucket]["hits"] = 0
                state[bucket]["rests"] += 1
            
        # Role Weights
        role_weights = {"lead": 1.0, "inner": 0.95, "bass": 0.9}
        if is_jazz: role_weights = {"lead": 1.0, "inner": 0.55, "bass": 0.75}
        if is_ska: role_weights = {"lead": 1.0, "inner": 0.95, "bass": 1.0}
        if is_reggae: role_weights = {"lead": 1.0, "inner": 0.85, "bass": 0.9}
        if bucket == "pad": role_weights = {"lead": 1.0, "inner": 1.0, "bass": 1.0}
        
        for note in group_notes:
            # Deterministic: Handle Group Dropout
            if mode == "deterministic":
                # Clear stale mute state first (Safety Fix)
                note.pop("mute", None)
                # Centralize probability reset (User Point 2)
                note["probability"] = 1.0
                
                if not event_active:
                    note["mute"] = True
                    processed.append(note)
                    # Skipped physics here naturally
                    continue
            
            # Hierarchical Dropout Weights
            role = note.get("_role", "inner")
            keep_prob = role_weights.get(role, 0.9)
            
            # User Point 1: Fix Double Probability & Logic Split
            if mode == "deterministic":
                 # Group already passed (event_active=True). 
                 # Only roll for role thinning.
                 if keep_prob < 1.0 and random.random() > keep_prob:
                     note["mute"] = True
                 note["probability"] = 1.0
                 
                 # Optimization: Skip physics for muted notes (User Point 2)
                 if note.get("mute"):
                      processed.append(note)
                      continue
            else:
                 # Probability Mode
                 # No rolling. Set Live probability.
                 final_prob = group_prob * keep_prob
                 note["probability"] = max(0.0, min(1.0, final_prob))
                 
                 # Schema Guard (User Point 3)
                 note.pop("mute", None) 
            
            # Customize Physics
            artic = note.get("_articulation", "sustain")
            velocity = note.get("velocity", 100)
            part = note.get("_part", "")
            
            # --- Velocity Deviation ---
            base_dev = 5 
            if bucket == "pad": base_dev = 10
            elif bucket == "hit": base_dev = 4
            
            t = max(0.4, min(1.6, velocity/90.0))
            if bucket == "pad":
                 scaled_dev = int(base_dev * (1.6 - 0.6 * t))
            else: 
                 scaled_dev = int(base_dev * (1.3 - 0.4 * t)) 
            
            # Pitch-based Register
            pitch = note.get("pitch", 60)
            is_high = pitch >= 72 
            is_low = pitch <= 48  
            
            if is_high: scaled_dev = int(scaled_dev * 0.8) 
            if is_low and bucket == "pad": scaled_dev = int(scaled_dev * 0.9)
            
            note["velocity_deviation"] = max(0, min(127, scaled_dev))
            
            # --- Release Velocity ---
            rel_vel = 64
            if bucket == "hit":
                 rel_vel = 80 + random.randint(-6, 6)
            elif bucket == "pad":
                 rel_vel = 20 + random.randint(-4, 4)
            elif is_jazz and "comp" in artic:
                 rel_vel = 55 + random.randint(-10, 10)
            
            note["release_velocity"] = max(0, min(127, rel_vel))
            
            # Duration Nudge
            # User Point 3: Clamp overlaps / max duration for hits
            dur = note["duration"]
            nudge = 1.0
            if bucket == "pad":
                 nudge = random.uniform(0.92, 1.03)
            elif bucket == "hit":
                 nudge = random.uniform(0.85, 1.0)
            
            new_dur = max(0.05, dur * nudge)
            
            if bucket == "hit":
                 # Prevent smear
                 new_dur = min(new_dur, 0.48)
            
            note["duration"] = new_dur
                 
            processed.append(note)

    return processed
