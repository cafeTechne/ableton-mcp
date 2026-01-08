"""
Brass Voicing Strategies
========================
Logic for distributing chord tones to brass sections.
Returns pitch classes (0-11) or intervals relative to root, not absolute pitches.
"""

from typing import List, Dict

def get_pow_stack() -> List[int]:
    """
    Power Stack: Root - 5th - Octave - 5th (Open, powerful)
    Returns intervals from bass anchor.
    """
    return [0, 7, 12, 19]

def get_triad_closed_intervals() -> List[int]:
    """
    Closed Triad Intervals (Root pos)
    section.py will transpose to fit.
    """
    return [0, 4, 7] # Major default, adjusted by scale/chord in conductor

def get_shell_recipe(chord_tones: List[int]) -> Dict[str, List[int]]:
    """
    Jazz Shell Recipe.
    Returns:
        'guides': [3rd, 7th] (absolute pitch classes)
        'extensions': [9th, 13th] optional
    """
    # chord_tones usually [Root, 3rd, 5th, 7th, 9th...]
    recipe = {"guides": [], "extensions": [], "root": chord_tones[0] % 12}
    
    if len(chord_tones) > 1: recipe["guides"].append(chord_tones[1] % 12) # 3rd
    if len(chord_tones) > 3: recipe["guides"].append(chord_tones[3] % 12) # 7th
    
    if len(chord_tones) > 4: recipe["extensions"].append(chord_tones[4] % 12) # 9th
    if len(chord_tones) > 5: recipe["extensions"].append(chord_tones[5] % 12) # 13th/11th
    
    return recipe
