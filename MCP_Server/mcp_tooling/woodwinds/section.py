"""
Woodwind Section Conductor
==========================
Stateful generator for woodwind sections using advanced role-based orchestration.
"""

from typing import List, Dict, Optional, Tuple
import random
from .parts import PARTS, fit_to_range
from .rhythm import get_pattern
from .styles import get_style_profile, WoodwindProfile
from ..performance import apply_performance_humanization

class WoodwindConductor:
    def __init__(self, style_name: str):
        self.profile: WoodwindProfile = get_style_profile(style_name)
        # State: Last pitch per instrument { 'fl': 72, ... }
        self.prev_pitches: Dict[str, int] = {}
        self.bar_counter = 0

    def get_notes(
        self,
        tones: List[int],
        start_time: float,
        duration: float,
        velocity: int,
        octave: int = 4,
        mode: str = "deterministic"
    ) -> List[Dict]:
        """
        Generate notes for one chord using advanced orchestration.
        tones: List of MIDI pitches (Root-based).
        """
        self.bar_counter += 1
        
        # 1. Analyze Chord
        # Extract pitch classes map: {0: 'root', 4: '3rd', 7: '5th' ...} roughly
        # Assumes tones[0] is root.
        root_pc = tones[0] % 12
        chord_pcs = [t % 12 for t in tones]
        
        # 2. Candidate Generation (Range-Aware)
        # For each instrument, generate valid candidates from chord tones
        def get_candidates(inst_name: str, pcs: List[int]) -> List[int]:
            part = PARTS.get(inst_name)
            if not part: return []
            candidates = []
            # Scan range
            for p in range(part.min, part.max + 1):
                if (p % 12) in pcs:
                    candidates.append(p)
            return candidates

        active_insts = self.profile.active_instruments
        # Process in specific order? Maybe role based?
        # Let's process Bass first, then Lead, then others.
        
        assignments: Dict[str, int] = {}
        
        # Helper: Get role for instrument
        def get_role(inst): return self.profile.roles.get(inst, "inner")
        
        sorted_insts = sorted(active_insts, key=lambda x: (
            0 if get_role(x) == "bass" else
            1 if get_role(x) == "lead" else
            2
        ))
        
        used_pitches = set()

        for inst_name in sorted_insts:
            role = get_role(inst_name)
            candidates = get_candidates(inst_name, chord_pcs)
            
            if not candidates: continue
            
            target_pitch = 0
            
            # --- Role Logic ---
            
            if role == "bass":
                # strict lowest
                # If Bassoon, prefer Roots (tones[0]) or 5ths
                # Filter candidates for root/5th only if possible
                priority_pcs = [root_pc]
                if len(tones) > 2: priority_pcs.append(tones[2] % 12) # 5th usually index 2? safely index
                
                bass_cands = [c for c in candidates if (c % 12) in priority_pcs]
                if not bass_cands: bass_cands = candidates # Fallback
                
                # Pick lowest avail
                target_pitch = min(bass_cands)
                
            elif role == "lead":
                # Melodic logic
                # 1. Try to keep common tone (min movement)
                # 2. Try to move stepwise
                # 3. Target profile tessitura
                
                prev = self.prev_pitches.get(inst_name)
                center = self.profile.tessitura.get(inst_name, 72)
                
                if prev:
                    # Find candidate closest to prev
                    # Bias slightly towards center just to prevent drift
                    target_pitch = min(candidates, key=lambda x: abs(x - prev) + 0.1 * abs(x - center))
                else:
                    target_pitch = min(candidates, key=lambda x: abs(x - center))
                    
            elif role == "counter" or role == "obligato":
                # Avoid unison with Lead if possible
                # Prefer 3rds/7ths (Color)
                # Here we simplify: Pick candidate closest to tessitura that isn't used
                
                center = self.profile.tessitura.get(inst_name, 60)
                
                # Filter out used pitches if density permits (don't strictly ban unisons but deprioritize them)
                free_cands = [c for c in candidates if c not in used_pitches]
                
                pool_to_use = free_cands if free_cands else candidates
                target_pitch = min(pool_to_use, key=lambda x: abs(x - center))
                
            else: # inner / padding
                # Just fit in
                center = self.profile.tessitura.get(inst_name, 60)
                target_pitch = min(candidates, key=lambda x: abs(x - center))

            assignments[inst_name] = target_pitch
            used_pitches.add(target_pitch)
            self.prev_pitches[inst_name] = target_pitch

        # 3. Constraint Pass (Spacing/Order)
        # Check for bad crossings: e.g. Bassoon > Flute
        # Define expected register order: bn < cl < ob < fl
        # This is hard because clarinet is wide range.
        # But generally: bn (bass) < others.
        # Let's just fix Bassoon crossing for now.
        
        if "bn" in assignments:
            bn_pitch = assignments["bn"]
            for other in ["cl", "ob", "fl"]:
                if other in assignments and assignments[other] < bn_pitch:
                    # Swap or shift?
                    # Shift bass down?
                    new_bn = bn_pitch - 12
                    part_bn = PARTS["bn"]
                    if new_bn >= part_bn.min:
                        # Safety: Ensure explicitly valid
                        new_bn = fit_to_range(new_bn, "bn")
                        assignments["bn"] = new_bn
                        self.prev_pitches["bn"] = new_bn
                    # Else shift other up?
                    # Keep simple for now.

        # 4. Rhythm & Output
        # Use profile rhythm pattern key
        pattern_name = self.profile.rhythm_pattern
        pattern_offsets = sorted(get_pattern(pattern_name))
        gate = self.profile.articulation.get("gate", 0.9)
        
        all_notes = []
        
        # Breathing / Phrasing: Only Lead drops occasionally
        lead_inst = next((i for i in assignments if self.profile.roles.get(i) == "lead"), None)
        
        # Define skip_probability
        skip_probability = 0.0
        if len(pattern_offsets) > 4: # fast notes
             skip_probability = 0.1
        
        for idx, frac in enumerate(pattern_offsets):
            # Scale offset by actual duration (bar-relative -> fractional)
            # Pattern 0.0-1.0 maps to 0.0-duration
            
            offset_beats = frac * duration
            
            # Calculate note duration
            # Distance to next offset or end of bar
            if idx < len(pattern_offsets) - 1:
                next_frac = pattern_offsets[idx+1]
                step = (next_frac - frac) * duration
            else:
                step = duration - offset_beats
            
            # Clamp step
            if offset_beats + step > duration:
                step = duration - offset_beats
                
            base_dur = max(step * gate, 0.1)
            start = start_time + offset_beats
            
            # Apply assignments
            for inst, pitch in assignments.items():
                
                # Breathing rule: Only lead drops, others support
                if inst == lead_inst and skip_probability > 0 and random.random() < skip_probability:
                    continue
                
                # Metadata for Performance Humanizer
                role = self.profile.roles.get(inst, "inner")
                
                # Derive Articulation from Context
                if self.profile.rhythm_pattern == "trance_gate":
                    artic_tag = "spicc"
                elif self.profile.rhythm_pattern == "reggae_skank" or gate <= 0.35:
                    artic_tag = "stab"
                else:
                    artic_tag = "legato"
                
                # Per-note duration (avoid leaking dur across instruments)
                note_dur = base_dur
                if artic_tag == "stab":
                    note_dur = min(note_dur, 0.25)

                all_notes.append({
                    "pitch": pitch,
                    "start_time": start,
                    "duration": note_dur,
                    "velocity": velocity,
                    "_part": inst,
                    "_section": "woodwinds",
                    "_role": role,
                    "_articulation": artic_tag
                })
                
        # 5. Apply Performance Humanization
        all_notes = apply_performance_humanization(
            all_notes, 
            style=self.profile.name, 
            section_name="woodwinds", 
            profile_name=self.profile.name,
            mode=mode
        )
                
        return all_notes
