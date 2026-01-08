"""
Strings Package
===============
Modular string section generation.
"""

from typing import List, Optional
from mcp_tooling.theory import get_chord_notes
from mcp_tooling.strings.section import SectionConductor
# Note names for MIDI conversion
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def key_to_midi(key: str, octave: int = 4) -> int:
    """Convert key name to MIDI note number (Robust)."""
    # 1. Normalize
    k = key.strip()
    # 2. Extract Pitch Class (e.g. C, C#, Db)
    # Check first 2 chars
    if len(k) > 1 and k[1] in ["#", "b"]:
        pc = k[:2]
    else:
        pc = k[:1]
        
    # Standardize sharps/flats
    pc = pc.upper().replace("DB", "C#").replace("EB", "D#").replace("GB", "F#").replace("AB", "G#").replace("BB", "A#")
    
    try:
        return 12 * (octave + 1) + NOTE_NAMES.index(pc)
    except ValueError:
        return 60  # Default to C4

def generate_strings_advanced(
    chords: List[str],
    key: str,
    scale: str = "major",
    beats_per_chord: float = 4.0,
    style: str = "pop", 
    velocity: int = 90,
    octave: int = 4,
    total_bars: Optional[int] = None,
    mode: str = "deterministic"
) -> tuple:
    """
    Generate string notes for a full progression using stateful SectionConductor.
    """
    # Calculate timing
    if total_bars and chords:
        beats_total = total_bars * 4
        beats_per_chord = beats_total / len(chords)
        
    root_midi = key_to_midi(key, octave)
    all_notes = []
    current_time = 0.0
    
    # Initialize Conductor
    conductor = SectionConductor(style)
    
    for chord in chords:
        # Get chord tones
        tones = get_chord_notes(root_midi, scale, chord)
        
        # Generate section notes for this chord
        notes = conductor.get_notes(
            tones=tones,
            start_time=current_time,
            duration=beats_per_chord,
            velocity=velocity,
            octave=octave,
            mode=mode
        )
        
        all_notes.extend(notes)
        current_time += beats_per_chord
        
    return all_notes, current_time
