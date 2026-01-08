"""
String Voicing Logic
====================
Algorithms for distributing chord tones into string-friendly spreads.
"""

from typing import List, Dict
from .parts import PARTS, fit_to_range

def normalize_closed(tones: List[int], octave: int = 4) -> List[int]:
    """Bring all tones into a single octave (closed position) starting at 'octave'."""
    # Base pitch C{octave}
    base = 12 * (octave + 1)
    
    # Sort by pitch class
    # Helper to get pc and original
    pcs = sorted([(t % 12, t) for t in tones], key=lambda x: x[0])
    
    # Reconstruct in octave
    last_p = -1
    closed = []
    
    # Find the root (assuming tones[0] was root from theory check, but here we just stack)
    # Actually, theory.get_chord_notes returns [root, 3rd, 5th, 7th]. 
    # We should preserve that order? No, voicing usually implies stacking.
    # Let's stack them as close as possible.
    
    # Logic: Start first note at base. Stack others on top.
    
    # Better logic: Just modulo 12 all them, keep relative order if implied inversion?
    # Let's just flatten to PC set and build up from Root.
    # Assuming tones[0] is Bass Root.
    
    root_pc = tones[0] % 12
    current_octave_base = base
    
    # Adjust base to match root pitch roughly?
    # User passed `octave`.
    
    new_tones = []
    
    # Find which input is the root? tones[0]
    # We will build Root, 3rd, 5th, 7th upwards.
    
    # Map cleaned tones
    unique_pcs = []
    seen = set()
    for t in tones:
        pc = t % 12
        if pc not in seen:
            unique_pcs.append(pc)
            seen.add(pc)
            
    # Normalize: Start with Root PC. Find next PC above it.
    current_pitch = base + root_pc # This might be e.g. C4 or F4
    
    # Ensure base is C-based.
    # If root_pc is say G, and octave is 4 (C4=60), G4=67. 
    # If octave is 3 (C3=48), G3=55.
    
    # Start root at the requested octave
    # C=0.
    start_pitch = (12 * (octave + 1)) + root_pc
    new_tones.append(start_pitch)
    
    last_pitch = start_pitch
    for pc in unique_pcs[1:]:
        # Find next occurrence of pc above last_pitch
        next_p = last_pitch + 1
        while next_p % 12 != pc:
            next_p += 1
        new_tones.append(next_p)
        last_pitch = next_p
        
    return new_tones

def get_power_voicing(tones: List[int]) -> List[int]:
    """Root - 5th - Octave - 5th."""
    # Assume tones[0] is root, tones[2] is 5th (usually).
    # Safer: analyze intervals.
    root = tones[0]
    # Find 5th (7 semitones)
    fifth = next((t for t in tones if (t - root) % 12 == 7), root + 7)
    
    # Build: Low Root, Low 5th, High Root, High 5th
    # We'll normalize later to range.
    # Just return relative structure: 0, 7, 12, 19
    return [0, 7, 12, 19]

def get_drop2_voicing(tones: List[int], octave: int = 4) -> List[int]:
    """
    Drop-2 Voicing for 4-part writing.
    1. Take closed voicing (top 4 notes).
    2. Drop the 2nd highest note an octave.
    """
    closed = normalize_closed(tones, octave)
    if len(closed) < 2: return closed
    
    # If 3 notes (triad): [Low, Mid, High]. Drop 2 means drop Mid? 
    # Usually Drop 2 implies 4 voices.
    # If triad, double the root or use open triad.
    
    if len(closed) < 4:
         # Borrow root octave for 4th voice
         closed.append(closed[0] + 12)
         closed.sort()
         
    # Now we have at least 4.
    # Top is -1. 2nd highest is -2.
    voice_to_drop = closed.pop(-2)
    dropped = voice_to_drop - 12
    
    # Reinsert
    closed.append(dropped)
    closed.sort()
    
    return closed

def assign_to_sections(notes: List[int]) -> Dict[str, int]:
    """
    Assign a list of sorted MIDI pitches (Low -> High) to sections (vc, vla, vl2, vl1).
    Returns dict: { 'vc': pitch, 'vla': pitch ... }
    """
    # Naive assignment:
    # Lowest -> Cello
    # Top -> Violin 1
    # Middles -> Viola / Violin 2
    
    # Logic depends on count
    count = len(notes)
    assignment = {}
    
    if count == 0: return {}
    
    sorted_notes = sorted(notes)
    
    # Always assign bass
    assignment['vc'] = fit_to_range(sorted_notes[0], 'vc')
    
    # If only 1 note, everyone plays octaves?
    if count == 1:
        p = sorted_notes[0]
        assignment['vla'] = fit_to_range(p, 'vla')
        assignment['vl2'] = fit_to_range(p, 'vl2')
        assignment['vl1'] = fit_to_range(p, 'vl1')
        return assignment
        
    # Always assign top
    assignment['vl1'] = fit_to_range(sorted_notes[-1], 'vl1')
    
    # Middles
    if count == 2:
        # 2 notes: VC takes bottom, VL1 takes top.
        # VLA doubles VC (8va), VL2 doubles VL1 (8vb)?
        assignment['vla'] = fit_to_range(sorted_notes[0] + 12, 'vla')
        assignment['vl2'] = fit_to_range(sorted_notes[-1] - 12, 'vl2')
        
    elif count == 3:
        # VC=0, VL1=2.
        # Vla and Vl2 share the middle (1).
        mid = sorted_notes[1]
        assignment['vla'] = fit_to_range(mid, 'vla')
        assignment['vl2'] = fit_to_range(mid, 'vl2') #Unison or range fit?
        
    else: # 4 or more
        # VC=0, Vla=1, Vl2=2, Vl1=3 (Standard SATB)
        assignment['vla'] = fit_to_range(sorted_notes[1], 'vla')
        assignment['vl2'] = fit_to_range(sorted_notes[2], 'vl2')
        
    return assignment
