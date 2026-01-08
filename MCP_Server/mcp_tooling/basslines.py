"""
Bassline Generation Module
==========================
Generate bass notes from chord progressions using music theory rules and genre-specific idioms.

Based on detailed harmonic and rhythmic profiles:
- Jazz: Walking bass (quarter notes), guide tone targeting, chromatic approaches
- Rock/Pop: Root-5-Octave, locked to kick, 8th note driving
- Funk/Soul: Syncopated 16ths, ghost notes, octave jumps
- Reggae: Subtractive, one-drop feel, heavy low end
- Bossa Nova: Root-5 pattern with syncopation
- Country: 2-feel (Root-5 on 1 and 3)
"""

import random
from typing import List, Dict, Any, Optional, Union
from .theory import get_chord_notes
from .constants import SCALES

# Bass octave (MIDI note 36 = C2)
DEFAULT_BASS_OCTAVE = 2

# Note names for MIDI conversion
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def key_to_midi(key: str, octave: int = DEFAULT_BASS_OCTAVE) -> int:
    """Convert key name to MIDI note number at specified octave."""
    key_norm = key.upper().replace("DB", "C#").replace("EB", "D#").replace("GB", "F#").replace("AB", "G#").replace("BB", "A#")
    key_clean = key_norm.replace("M", "")
    try:
        return 12 * (octave + 1) + NOTE_NAMES.index(key_clean)
    except ValueError:
        return 36  # Default to C2

def get_chord_root_pitch(root_midi: int, scale_name: str, numeral: str) -> int:
    """Get the bass root note for a chord numeral."""
    chord_notes = get_chord_notes(root_midi, scale_name, numeral)
    if chord_notes:
        return chord_notes[0]
    return root_midi

def get_chord_tones(root_midi: int, scale_name: str, numeral: str) -> List[int]:
    """Get all tones for a chord."""
    return get_chord_notes(root_midi, scale_name, numeral)

def get_approach_note(target_pitch: int, style: str = "chromatic_below") -> int:
    """Get approach note to target pitch."""
    if style == "chromatic_below":
        return target_pitch - 1
    elif style == "chromatic_above":
        return target_pitch + 1
    elif style == "dominant_below": # 5th below
        return target_pitch - 7
    elif style == "fifth_above":
        return target_pitch + 7
    return target_pitch - 1 # Default

# --- GENRE-SPECIFIC GENERATORS ---

def _gen_jazz_walking(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Jazz Walking Bass
    Rule: Quarter notes. 1=Root, 2=Tone, 3=Tone/5th, 4=Approach to next Root.
    """
    notes = []
    beats = int(duration)
    
    # Analyze chord tones for targets
    # chord_tones usually [root, 3rd, 5th, 7th]
    third = chord_tones[1] if len(chord_tones) > 1 else root + 4
    fifth = chord_tones[2] if len(chord_tones) > 2 else root + 7
    seventh = chord_tones[3] if len(chord_tones) > 3 else root + 10
    
    current_pitch = root
    
    for beat in range(beats):
        pitch = root # Default
        vel = velocity
        dur = 0.9 # Legato but articulate
        
        if beat == 0:
            # Beat 1: Strong Root (or 3rd if inversions allowed, but usually Root)
            pitch = root
            vel = int(velocity * 1.1)
            
        elif beat == beats - 1 and next_root is not None:
             # Last Beat: Approach Logic to NEXT chord
             # High probability of chromatic approach
             if random.random() < 0.7:
                 # Chromatic approach
                 pitch = next_root - 1 if current_pitch < next_root else next_root + 1
                 # Randomize direction occasionally
                 if random.random() < 0.3: pitch = next_root - 1
                 elif random.random() < 0.3: pitch = next_root + 1
             else:
                 # Diatonic/5th approach
                 pitch = next_root + 7 if random.random() < 0.5 else next_root - 5
                 
        else:
            # Middle Beats (2, 3, etc): Targets & Passing Tones
            # Target 3rd, 5th, 7th, or octave
            options = [third, fifth, root + 12]
            if len(chord_tones) > 3: options.append(seventh)
            
            # Simple passing logic: move stepwise if possible
            # For now, random chord tone selection is robust enough for basic walking
            pitch = random.choice(options)
            
            # Add some "ghost skip" variance (very rare in walking, but maybe for turnaround)
            vel = int(velocity * 0.9)

        current_pitch = pitch
        notes.append({
            "pitch": pitch,
            "start_time": start_time + beat,
            "duration": dur,
            "velocity": vel
        })
        
    return notes

def _gen_rock_pop_driving(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Rock/Pop Driving 8ths
    Rule: Root-5-Octave, locked grid, steady 8ths.
    """
    notes = []
    beats = int(duration)
    subdivisions = 2 # 8th notes
    
    fifth = chord_tones[2] if len(chord_tones) > 2 else root + 7
    octave = root + 12
    
    pattern_type = random.choice(["straight_8", "root_5", "gallop"])
    
    for i in range(beats * subdivisions):
        note_offset = i / subdivisions
        p = root
        v = velocity
        d = 0.45
        
        # Beat logic
        is_downbeat = (i % 2 == 0)
        beat_num = (i // 2) + 1
        
        # Patterns
        if pattern_type == "root_5":
            # Root on 1, 5 on 3 (classic country/rock)
            if beat_num in [3, 4] and is_downbeat: p = fifth
            elif beat_num == 4 and not is_downbeat: p = fifth # push
            
        elif pattern_type == "gallop":
            # Iron Maiden style (dotted 8th + 16th? Simplified here as 8ths with accents)
            if not is_downbeat: v = int(velocity * 0.7)
            
        else: # straight_8
            # Occasional octave jump on weak beats
            if not is_downbeat and random.random() < 0.2: p = octave
            
        # Add note
        notes.append({
            "pitch": p,
            "start_time": start_time + note_offset,
            "duration": d,
            "velocity": v
        })
        
    return notes

def _gen_funk_syncopated(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Funk/Soul Syncopated 16ths
    Rule: The "One" is sacred. Ghost notes. Octave pops. Space.
    """
    notes = []
    # Funk is less about filling every slot, more about the grid
    # We'll generate a 1-bar pattern (16 slots)
    
    octave = root + 12
    flat_seven = root + 10 # approximate
    if len(chord_tones) > 3: flat_seven = chord_tones[3]
    
    # Always hit the ONE
    notes.append({
        "pitch": root,
        "start_time": start_time,
        "duration": 0.6, # fat
        "velocity": int(velocity * 1.1)
    })
    
    # Construct a random syncopated rhythm for the rest of the bar
    # 16th note grid
    grid = [0] * 16
    # 0 = rest, 1 = root, 2 = octave, 3 = ghost, 4 = 7th
    
    # High probability spots for funk
    # the "a" of 1 (1.75), "and" of 2 (2.5), "e" of 3 (3.25), 4 (4.0)
    
    # Preset patterns
    patterns = [
        # Bootsy-ish
        {4: 2, 6: 3, 8: 1, 10: 3, 12: 1, 14: 4},
        # Rocco-ish
        {2: 3, 3: 3, 4: 1, 7: 2, 10: 3, 12: 1, 15: 4},
        # Generic Disco Octaves
        {2: 2, 4: 1, 6: 2, 8: 1, 10: 2, 12: 1, 14: 2}
    ]
    
    selected_pat = random.choice(patterns)
    
    for step, note_type in selected_pat.items():
        if step == 0: continue # Already did the one
        
        step_time = step * 0.25
        if step_time >= duration: break
        
        p = root
        v = velocity
        d = 0.2
        
        if note_type == 2: p = octave
        elif note_type == 3: # Ghost
            p = root # muffled
            v = int(velocity * 0.5)
            d = 0.1
        elif note_type == 4: p = flat_seven
        
        notes.append({
            "pitch": p,
            "start_time": start_time + step_time,
            "duration": d,
            "velocity": v
        })
        
    return notes

def _gen_reggae_dub(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Reggae/Dub
    Rule: Avoid the One (mostly). Emphasize 3 (One Drop). Deep subs.
    """
    notes = []
    
    # Common Reggae Pattern: Drop One, Hit 2 and 3 and 4
    # OR: Hit 3 hard (One Drop)
    
    pattern_type = random.choice(["one_drop", "steppers"])
    
    if pattern_type == "one_drop":
        # Rest on 1. Hit 3.
        # Beat 3 is start_time + 2.0
        if duration >= 3:
            notes.append({
                "pitch": root,
                "start_time": start_time + 2.0, # Beat 3
                "duration": 0.8,
                "velocity": int(velocity * 1.1) 
            })
            # Maybe a pickup to 3?
            notes.append({
                 "pitch": root - 5, # Low 5th
                 "start_time": start_time + 1.5,
                 "duration": 0.4,
                 "velocity": int(velocity * 0.8)
            })
    else:
        # Steppers: Four on floor feel, but bass often syncopated
        # Root on 1, 2, 3, 4?
        pass # simplified for now
        
    # Fallback to simple melodic if pattern logic fails (e.g. short clips)
    if not notes and duration >= 1:
         notes.append({ "pitch": root, "start_time": start_time, "duration": duration, "velocity": velocity })

    return notes
    
def _gen_country_2feel(
    root: int, chord_tones: List[int], next_root: Optional[int], 
    start_time: float, duration: float, velocity: int
) -> List[Dict]:
    """
    Country 2-Feel
    Rule: Root on 1, 5th on 3. Walkups.
    """
    notes = []
    
    fifth = chord_tones[2] if len(chord_tones) > 2 else root + 7
    lower_fifth = root - 5
    
    # Beat 1: Root
    notes.append({
        "pitch": root,
        "start_time": start_time,
        "duration": 0.9,
        "velocity": int(velocity * 1.1)
    })
    
    # Beat 3: 5th (if duration allows)
    if duration >= 3:
        p = lower_fifth if random.random() < 0.5 else fifth
        notes.append({
            "pitch": p,
            "start_time": start_time + 2.0,
            "duration": 0.9,
            "velocity": velocity
        })
        
    # Walkup? (Beat 4)
    if duration >= 4 and next_root:
        # Simple chromatic walk
        notes.append({
            "pitch": next_root - 1, # leading tone
            "start_time": start_time + 3.0,
            "duration": 0.9,
            "velocity": int(velocity * 0.9)
        })
        
    return notes


# --- MAIN DISPATCHER ---

def generate_bassline_from_progression(
    chords: List[str],
    key: str,
    scale: str = "major",
    beats_per_chord: float = 4.0,
    style: str = "walking", # "jazz", "rock", "funk", "reggae", "country"
    velocity: int = 100,
    octave: int = DEFAULT_BASS_OCTAVE,
    total_bars: Optional[int] = None
) -> tuple: # (notes, length)
    """
    Generate complete bassline.
    style maps to genre-specific generators.
    """
    root_midi = key_to_midi(key, octave)
    all_notes = []
    
    # Pre-calc roots and chord tones for improved context awareness
    prog_data = []
    for chord in chords:
        r = get_chord_root_pitch(root_midi, scale, chord)
        t = get_chord_tones(root_midi, scale, chord)
        prog_data.append({"root": r, "tones": t})
        
    # Calculate timing
    if total_bars:
        beats_total = total_bars * 4
        beats_per_chord = beats_total / len(chords)
    
    current_time = 0.0
    
    for i, data in enumerate(prog_data):
        root = data["root"]
        tones = data["tones"]
        next_root = prog_data[i+1]["root"] if i+1 < len(prog_data) else None
        
        # Dispatch
        if style in ["jazz", "walking", "swing"]:
            notes = _gen_jazz_walking(root, tones, next_root, current_time, beats_per_chord, velocity)
        elif style in ["rock", "pop", "driving", "metal"]:
            notes = _gen_rock_pop_driving(root, tones, next_root, current_time, beats_per_chord, velocity)
        elif style in ["funk", "soul", "rnb", "syncopated"]:
            notes = _gen_funk_syncopated(root, tones, next_root, current_time, beats_per_chord, velocity)
        elif style in ["reggae", "dub"]:
            notes = _gen_reggae_dub(root, tones, next_root, current_time, beats_per_chord, velocity)
        elif style in ["country", "blues", "folk"]:
            notes = _gen_country_2feel(root, tones, next_root, current_time, beats_per_chord, velocity)
        else:
            # Default fallback (Root notes)
            notes = [{
                "pitch": root,
                "start_time": current_time,
                "duration": beats_per_chord - 0.1,
                "velocity": velocity
            }]
            
        all_notes.extend(notes)
        current_time += beats_per_chord
        
    return all_notes, current_time

# Alias for compatibility with generators.py import
generate_bassline_advanced = generate_bassline_from_progression
