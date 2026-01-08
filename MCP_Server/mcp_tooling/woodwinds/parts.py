"""
Woodwind Instrument Definitions
===============================
Ranges and roles for the woodwind section.
"""

class WoodwindInstrument:
    def __init__(self, name, min_pitch, max_pitch, role_bias):
        self.name = name
        self.min = min_pitch
        self.max = max_pitch
        self.role_bias = role_bias # 'soprano', 'alto', 'tenor', 'bass'

# Ranges (approximate comfortable playing ranges)
# MIDI 60 = C4 (Middle C)
# Flute: C4 (60) - C7 (96)
# Oboe: Bb3 (58) - G6 (91)
# Clarinet (Bb): D3 (50) - Bb6 (94) (Concert pitch approx)
# Bassoon: Bb1 (34) - Eb5 (75)

PARTS = {
    "fl": WoodwindInstrument("Flute", 60, 96, "soprano"),
    "ob": WoodwindInstrument("Oboe", 58, 91, "alto"),
    "cl": WoodwindInstrument("Clarinet", 50, 94, "tenor"), # Wide range!
    "bn": WoodwindInstrument("Bassoon", 34, 75, "bass")
}

def fit_to_range(pitch: int, part_name: str) -> int:
    """Transpose pitch by octaves to fit within part range."""
    part = PARTS.get(part_name)
    if not part:
        return pitch
        
    current = pitch
    
    # Check if we need to shift up
    while current < part.min:
        current += 12
        
    # Check if we need to shift down
    while current > part.max:
        current -= 12
        
    # Final check
    if current < part.min: current += 12
    if current > part.max: current -= 12
    
    return current
