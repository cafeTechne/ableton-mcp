"""
Brass Orchestration Module
==========================
Generates brass section midi.
"""

from typing import List, Optional
from mcp_tooling.theory import get_chord_notes
from mcp_tooling.brass.section import BrassConductor

# Helper for key parsing (should be shared util but copying for safety)
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
def key_to_midi(key: str, octave: int = 4) -> int:
    k = key.strip().upper()
    if len(k) > 1 and k[1] in ["#", "B"]:
        pc = k[:2].replace("DB", "C#").replace("EB", "D#").replace("GB", "F#").replace("AB", "G#").replace("BB", "A#")
    else:
        pc = k[:1]
    try:
        return 12 * (octave + 1) + NOTE_NAMES.index(pc)
    except:
        return 60

def generate_brass_advanced(
    chords: List[str],
    key: str,
    scale: str = "major",
    beats_per_chord: float = 4.0,
    style: str = "pop",
    velocity: int = 100,
    octave: int = 3,
    total_bars: Optional[int] = None,
    mode: str = "deterministic"
) -> tuple:
    """
    Generate brass notes.
    """
    if total_bars and chords:
        beats_per_chord = (total_bars * 4.0) / len(chords)
        
    root_midi = key_to_midi(key, octave)
    all_notes = []
    current_time = 0.0
    
    conductor = BrassConductor(style)
    
    for chord in chords:
        tones = get_chord_notes(root_midi, scale, chord)
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
