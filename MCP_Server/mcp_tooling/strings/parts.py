"""
String Parts Definitions
========================
Ranges and roles for the string section.
"""

class StringPart:
    def __init__(self, name, min_pitch, max_pitch, role):
        self.name = name
        self.min = min_pitch
        self.max = max_pitch
        self.role = role # 'bass', 'tenor', 'alto', 'soprano'

# Ranges (approximate comfortable playing ranges)
# MIDI 36 = C2, 48 = C3, 60 = C4

PARTS = {
    "vc": StringPart("Cello", 36, 67, "bass"),      # C2 - G4
    "vla": StringPart("Viola", 48, 79, "tenor"),    # C3 - G5
    "vl2": StringPart("Violin 2", 55, 88, "alto"),  # G3 - E6
    "vl1": StringPart("Violin 1", 55, 96, "soprano") # G3 - C7
}

def fit_to_range(pitch: int, part_name: str) -> int:
    """Transpose pitch by octaves to fit within part range."""
    part = PARTS.get(part_name)
    if not part:
        return pitch
        
    # Naive fit: keep shifting until inside
    # Better fit: find octave closest to center of range?
    center = (part.min + part.max) / 2
    
    current = pitch
    # Normalize to base octave first? No, just shift
    
    # Check if we need to shift up
    while current < part.min:
        current += 12
        
    # Check if we need to shift down
    while current > part.max:
        current -= 12
        
    # Final check (if range is < 12 semitones, might fail, but string ranges are wide)
    # If still out (due to while loops overshooting?), clamp
    if current < part.min: current += 12
    if current > part.max: current -= 12
    
    return current
