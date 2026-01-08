"""
Brass Section Conductor
=======================
Impact-first generation logic for brass with rigorous constraints.
"""

from typing import List, Dict, Optional
import random
from .parts import PARTS
from .rhythm import get_pattern
from .styles import get_style_profile, BrassProfile
from .voicings import get_pow_stack, get_shell_recipe
from ..performance import apply_performance_humanization

class BrassConductor:
    def __init__(self, style_name: str):
        self.profile: BrassProfile = get_style_profile(style_name)
        self.prev_pitches: Dict[str, int] = {}
        self.phrase_counter = 0

    def get_notes(
        self,
        tones: List[int], # Raw chord tones (MIDI)
        start_time: float,
        duration: float,
        velocity: int,
        octave: int = 3,
        mode: str = "deterministic"
    ) -> List[Dict]:
        
        self.phrase_counter += 1
        
        # 1. Candidate Generation
        assignments: Dict[str, int] = {}
        active_insts = self.profile.active_instruments
        strategy = self.profile.voicing_strategy
        
        # Helper: Find pitch instance closest to target
        def closest_pitch(target, pc, constraint_range=None):
            # Generate range C1 to C7
            candidates = []
            for o in range(1, 8):
                p = o * 12 + (pc % 12)
                candidates.append(p)
            
            # Filter by constraint range (instrument range)
            if constraint_range:
                candidates = [c for c in candidates if constraint_range.min <= c <= constraint_range.max]
                if not candidates: return None # Fallback?

            return min(candidates, key=lambda x: abs(x - target))

        if strategy == "power_stack":
            # Anchor to low instrument (Tuba or Bone) center
            anchor_inst = "tba" if "tba" in active_insts else "tbn"
            anchor_center = PARTS[anchor_inst].tessitura_center
            
            # Find root pitch near anchor
            root_pc = tones[0] % 12
            anchor_pitch = closest_pitch(anchor_center, root_pc, PARTS[anchor_inst])
            if not anchor_pitch: anchor_pitch = anchor_center # Fallback
            
            # Intervals: 0, 7, 12, 19
            offsets = get_pow_stack()
            stack_pitches = [anchor_pitch + o for o in offsets]
            
            # Assign bottom up
            # Order: tba, tbn, hn, tpt
            ordered_insts = sorted(active_insts, key=lambda x: PARTS[x].tessitura_center)
            
            for i, inst in enumerate(ordered_insts):
                if i < len(stack_pitches):
                    assignments[inst] = stack_pitches[i]
                else:
                    # Double top?
                    assignments[inst] = stack_pitches[-1]

        elif strategy == "shell":
            recipe = get_shell_recipe(tones)
            guides = recipe["guides"]
            exts = recipe["extensions"]
            root = recipe["root"]
            
            # Order: Bass/Tuba takes Root. Others take Shell.
            remaining_insts = list(active_insts)
            
            # 1. Bass role
            if "tba" in remaining_insts: 
                # Assign root low
                assignments["tba"] = closest_pitch(PARTS["tba"].tessitura_center, root, PARTS["tba"])
                remaining_insts.remove("tba")
            if "tbn" in remaining_insts and "bass" in self.profile.roles.get("tbn", ""):
                 assignments["tbn"] = closest_pitch(PARTS["tbn"].tessitura_center, root, PARTS["tbn"])
                 remaining_insts.remove("tbn")
            
            # 2. Guide Tones (Tbn/Hn usually)
            # Try to give 3rd and 7th
            # Prioritize 3rd if single voice? Or 7th? 3rd defines quality mostly.
            
            guides_pool = list(guides)
            # Ensure we have enough guides
            while len(guides_pool) < len(remaining_insts):
                 if exts: guides_pool.append(exts[0]) # Use extension if avail
                 else: guides_pool.append(guides[0]) # Recycle
            
            # Assign remaining (Tbn, Hn, Tpt)
            # Sort by register
            remaining_insts.sort(key=lambda x: PARTS[x].tessitura_center)
            
            # Assign low guide to low inst, high to high
            # Guides are PCs. Need to fit to tessitura.
            guides_pool.sort(key=lambda x: (x - root + 12) % 12) # Sort by interval from root? 3rd < 7th?
            # 3rd is interval 3/4. 7th is 10/11. 
            # Actually, just matching to tessitura is safer.
            
            for inst in remaining_insts:
                # Find best fit guide
                center = PARTS[inst].tessitura_center
                
                # Try all guides, pick one that lands optimally near center
                # AND check spacing if possible?
                
                best_p = 0
                best_dist = 999
                
                for g in guides_pool:
                     p = closest_pitch(center, g, PARTS[inst])
                     if not p: continue
                     d = abs(p - center)
                     if d < best_dist:
                         best_dist = d
                         best_p = p
                
                assignments[inst] = best_p

        else: # Triad / Default
            # Fit closest chord tones to tessitura
            root_pc = tones[0] % 12
            pc_pool = [t % 12 for t in tones]
            
            for inst in active_insts:
                center = PARTS[inst].tessitura_center
                bias = self.profile.register_bias
                if bias == "high": center += 7
                if bias == "low": center -= 7
                
                # Pick best pc
                best_p = 0
                best_dist = 999
                for pc in pc_pool:
                    p = closest_pitch(center, pc, PARTS[inst])
                    if not p: continue
                    d = abs(p - center)
                    if d < best_dist:
                        best_dist = d
                        best_p = p
                assignments[inst] = best_p
        
        # 2. Constraint Solver (Post-Pass)
        # Enforce tba <= tbn <= hn <= tpt
        # And minimum spacing
        
        ordered_keys = ["tba", "tbn", "hn", "tpt"]
        present_keys = [k for k in ordered_keys if k in assignments]
        
        for i in range(len(present_keys) - 1):
            low_inst = present_keys[i]
            high_inst = present_keys[i+1]
            
            p_low = assignments[low_inst]
            p_high = assignments[high_inst]
            
            # Rules:
            # 1. No Crossing (p_high >= p_low)
            if p_high < p_low:
                # Violation. 
                # Fix: Bump high up octave? Or low down?
                # Try bump high up
                p_high += 12
                # Check range?
                assignments[high_inst] = p_high
                
            # 2. Low Register Mud (if p_low < 48, ensure distance >= 5 semitones)
            if p_low < 48:
                if p_high - p_low < 5:
                    # Too close. Bump high.
                    assignments[high_inst] += 12
            
            # 3. Reduce Unisons (Unless Power Stack)
            if strategy != "power_stack" and p_high == p_low:
                # Bump high up to next chord tone?
                # Or just octave shift
                assignments[high_inst] += 12

        # 2a. Range Normalization (Safety)
        # Bumping might have pushed notes out of instrument range.
        # Wrap them back down or clamp if possible.
        for inst, pitch in assignments.items():
            part = PARTS.get(inst)
            if not part: continue
            # Simple clamp or wrap? Wrap is safer musically (octave error > silence)
            while pitch > part.max:
                pitch -= 12
            while pitch < part.min:
                pitch += 12
            # Final clamp if somehow still out (weird narrow range?)
            if pitch > part.max: pitch = part.max
            if pitch < part.min: pitch = part.min
            assignments[inst] = pitch

        # 3. Phrasing / Breath
        # Probability drop logic
        playing = True
        if self.profile.texture not in ["pad", "swell"]:
            # If fast hits, maybe always play
            # If Sparse style (Jazz comp), prob check
            if self.profile.name == "jazz" and random.random() < 0.3:
                 playing = False
        
        if not playing: return []

        # 4. Rhythm & Duration
        rhythm_key = self.profile.rhythm_pattern
        offsets = sorted(get_pattern(rhythm_key))
        gate = self.profile.gate
        
        all_notes = []
        
        # Density check: Subset of voices? 
        # Only for certain styles
        active_subset = list(assignments.keys())
        if self.profile.density < len(active_subset):
            # Pick subset based on role priority?
            # Lead + Bass always. Inner drops.
            # Simplified: Random sample or fixed priority
            # Keep Lead ("tpt") and Bass ("tba"/"tbn")
            keepers = set()
            if "tpt" in active_subset: keepers.add("tpt")
            if "tba" in active_subset: keepers.add("tba")
            elif "tbn" in active_subset: keepers.add("tbn")
            
            # Fill rest
            others = [k for k in active_subset if k not in keepers]
            needed = self.profile.density - len(keepers)
            if needed > 0 and others:
                keepers.update(others[:needed])
            
            active_subset = list(keepers)
            
        
        for idx, frac in enumerate(offsets):
            start = start_time + (frac * duration)
            
            # Dynamic Duration Logic
            # Calc step to next event
             # Distance to next offset or end of bar
            if idx < len(offsets) - 1:
                next_frac = offsets[idx+1]
                step = (next_frac - frac) * duration
            else:
                step = duration - (frac * duration) # To end of duration
            
            final_dur = step * gate
            # Clamp for stabs
            if self.profile.texture == "hit":
                final_dur = min(final_dur, 0.4) # Short stabs max
            
            
            for inst in active_subset:
                if inst not in assignments: continue
                pitch = assignments[inst]
                
                # Check range again after shifts?
                part = PARTS.get(inst)
                if pitch < part.min or pitch > part.max: continue # Emergency clip
                
                # Metadata for Performance Humanizer
                role = self.profile.roles.get(inst, "inner")
                texture = self.profile.texture
                artic_tag = "sustain"
                if texture in ["hit", "shout", "riff"]:
                     artic_tag = "hit"
                if texture in ["pad", "swell"]:
                     artic_tag = "pad"
                
                all_notes.append({
                    "pitch": pitch,
                    "start_time": start,
                    "duration": final_dur,
                    "velocity": velocity if frac == 0 else int(velocity * 0.9),
                    "_part": inst,
                    "_section": "brass",
                    "_role": role,
                    "_articulation": artic_tag
                })
        
        # 5. Apply Performance Humanization
        all_notes = apply_performance_humanization(
            all_notes, 
            style=self.profile.name, 
            section_name="brass", 
            profile_name=self.profile.name,
            mode=mode
        )
                
        return all_notes
