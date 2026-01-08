"""
Brass Instrument Definitions
============================
Ranges and roles for the brass section.
"""

class BrassInstrument:
    def __init__(self, name, min_pitch, max_pitch, tessitura_center, role_bias):
        self.name = name
        self.min = min_pitch
        self.max = max_pitch
        self.tessitura_center = tessitura_center
        self.role_bias = role_bias

# Ranges (approximate comfortable playing ranges)
# MIDI 60 = C4 (Middle C)
# Trumpet (Bb): F#3 (54) - C6 (84) (can go higher)
# Horn (F): B1 (35) - F5 (77)
# Trombone: E2 (40) - Bb4 (70)
# Tuba: D1 (26) - F3 (53)

PARTS = {
    "tpt": BrassInstrument("Trumpet", 54, 88, 74, "lead"),      # Targeting D5 area for lead
    "hn": BrassInstrument("Horn", 35, 77, 60, "inner"),         # Middle C area glue
    "tbn": BrassInstrument("Trombone", 40, 72, 48, "tenor"),    # C3 area weight
    "tba": BrassInstrument("Tuba", 24, 55, 36, "bass")          # C2 area foundation
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
        
    # Final check - if oscillating, clamp?
    if current < part.min: current += 12
    if current > part.max: current -= 12
    
    return current
