"""
String Section Conductor
========================
Stateful generator that manages voice leading and orchestration.
"""

from typing import List, Dict, Optional
from .parts import PARTS, fit_to_range
from .rhythm import get_pattern
from .voicings import get_drop2_voicing, get_power_voicing, normalize_closed, assign_to_sections
from .styles import get_style_profile, StyleProfile
from ..performance import apply_performance_humanization

class SectionConductor:
    def __init__(self, style_name: str):
        self.profile: StyleProfile = get_style_profile(style_name)
        # State: Last pitch per part { 'vc': 36, ... }
        self.prev_pitches: Dict[str, int] = {}
        
    def get_notes(
        self,
        tones: List[int],
        start_time: float,
        duration: float,
        velocity: int,
        octave: int = 4,
        mode: str = "deterministic"
    ) -> List[Dict]:
        """Generate notes for one chord, updating state."""
        
        # 1. Voicing Strategy
        strat = self.profile.voicing_strategy
        if strat == "power":
            raw_voicing = get_power_voicing(tones)
            root = tones[0]
            voicing = [root + offset for offset in raw_voicing]
        elif strat == "drop2":
            voicing = get_drop2_voicing(tones, octave)
        else: # closed/default
            voicing = normalize_closed(tones, octave)
            
        # 2. Orchestrate (Assign to active parts)
        # First, filter voicing to number of active parts?
        # Or just assign all and then filter output?
        # Better: Assign to ideal parts, then filter.
        
        assigned = assign_to_sections(voicing)
        
        # 3. Voice Leading Optimization
        # For each part, find nearest pitch to previous pitch
        final_assignment = {}
        for part, pitch in assigned.items():
            if part not in self.profile.density:
                continue # Skip inactive parts
                
            final_pitch = pitch
            
            # Optimization logic
            if part in self.prev_pitches:
                prev = self.prev_pitches[part]
                # Check candidates: pitch, pitch+12, pitch-12
                # But constrained by range!
                
                # Simple logic: Find candidate closest to prev that is valid in range
                candidates = []
                # Check current, +/- 1 octave, +/- 2 octaves
                for offset in [-24, -12, 0, 12, 24]:
                    cand = pitch + offset
                    # Check range
                    # Should use part definition from parts.py
                    # fit_to_range forces it.
                    # Just check if fit_to_range(cand) == cand?
                    # Or just rely on distance.
                    
                    # We accept slightly out of range if it preserves line?
                    # No, strict range.
                    if self._is_in_range(part, cand):
                        candidates.append(cand)
                        
                if candidates:
                    # Pick closest to prev
                    best = min(candidates, key=lambda x: abs(x - prev))
                    final_pitch = best
                else:
                    # Fallback if no specific octave logic found (shouldn't happen with fit_to_range input)
                    # Just fit it
                    final_pitch = fit_to_range(pitch, part)
            else:
                # First chord: Just fit to range
                final_pitch = fit_to_range(pitch, part)
                
            self.prev_pitches[part] = final_pitch
            final_assignment[part] = final_pitch
            
        # 4. Rhythm & Output
        pattern = get_pattern(self.profile.name) # Use profile name for pattern lookup
        # pattern is fractions 0.0 - 1.0 (bar relative) if we follow new logic.
        # But wait, input duration is 'beats_per_chord'.
        # If pattern is [0.0, 0.25] (quarters), and chord is 2 beats.
        # we want 0.0 and 1.0? 
        # The user requested: "normalize patterns to bar-relative... then map to beats"
        
        # Assuming pattern is [0.0, 0.25, 0.5, 0.75] (Quarters of a bar)
        # And 1 bar = 4 beats.
        # Chord duration might be 4.0 or 2.0.
        
        # Logic: We stride through the "global" bar? 
        # Or just relative to chord start?
        # Let's map fractions to beats: 0.25 * 4 = 1 beat.
        
        # But we need to handle chord boundary.
        # If chords change on beat 3.
        # We want the pattern to align with the grid? 
        # Or reset? Usually reset for simple logic.
        
        # Let's use duration as limit.
        
        gate = self.profile.articulation.get("gate", 1.0)
        all_notes = []
        
        for frac in pattern:
            offset_beats = frac * 4.0 # standardized to 4/4 bar
            
            if offset_beats >= duration:
                continue
                
            # Calculate duration
            # Distance to next trigger?
            # Find next frac in pattern?
            # Simple gate logic: 
            # If pad (whole note), duration = duration.
            # If stabs, duration = 0.25 (1/16th) or based on gate?
            
            # User suggested: calculate next trigger.
            # Find next trigger in pattern > current frac.
            # If none, use 1.0 (bar end).
            next_frac = 1.0
            for f in pattern:
                if f > frac:
                    next_frac = f
                    break
            
            step_size_beats = (next_frac - frac) * 4.0
            # If step goes past chord duration, clip it?
            if offset_beats + step_size_beats > duration:
                step_size_beats = duration - offset_beats
            
            note_dur = step_size_beats * gate
            # Ensure min duration?
            note_dur = max(note_dur, 0.1)
            
            real_start = start_time + offset_beats
            
            for part, note in final_assignment.items():
                
                # Dynamic modifiers
                vel = velocity
                if self.profile.register_bias == "high" and part == "vc":
                    vel -= 20 # Quiet cello in high styles
                
                # Metadata for Performance Humanizer
                # Infer Role
                role = "inner"
                if part == "vc": role = "bass"
                elif part == "vl1": role = "lead"
                
                # Derive Articulation
                artic_tag = "legato" # Default pad/sustain
                if self.profile.texture in ["stab", "pulse"]:
                    artic_tag = "spicc" # Hit bucket
                elif self.profile.texture == "pad":
                    artic_tag = "legato" # Pad bucket
                
                all_notes.append({
                    "pitch": note,
                    "start_time": real_start,
                    "duration": note_dur,
                    "velocity": vel,
                    "_part": part,
                    "_section": "strings",
                    "_role": role,
                    "_articulation": artic_tag
                })
        
        # 5. Apply Performance Humanization
        all_notes = apply_performance_humanization(
            all_notes,
            style=self.profile.name,
            section_name="strings",
            profile_name=self.profile.name,
            mode=mode
        )
                
        return all_notes

    def _is_in_range(self, part_name, pitch):
        from .parts import PARTS
        p = PARTS.get(part_name)
        if not p: return True
        return p.min <= pitch <= p.max
