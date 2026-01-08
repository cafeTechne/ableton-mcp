
# Musical Scales
SCALES = {
    "major": [0, 2, 4, 5, 7, 9, 11],
    "minor": [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "phrygian": [0, 1, 3, 5, 7, 8, 10],
    "lydian": [0, 2, 4, 6, 7, 9, 11],
    "mixolydian": [0, 2, 4, 5, 7, 9, 10],
    "locrian": [0, 1, 3, 5, 6, 8, 10],
    "harmonic_minor": [0, 2, 3, 5, 7, 8, 11],
    "melodic_minor": [0, 2, 3, 5, 7, 9, 11]
}

# Common Progressions
PROGRESSIONS = {
    "pop_1": ["I", "V", "vi", "IV"],
    "pop_2": ["vi", "IV", "I", "V"],
    "pop_3": ["I", "V", "vi", "iii", "IV", "I", "IV", "V"], # Pachelbel-ish
    "pop_4": ["I", "I", "IV", "V"],
    "emotional": ["vi", "IV", "I", "V"],
    "jazz_251": ["ii", "V", "I"],
    "blues": ["I7", "IV7", "I7", "V7", "IV7", "I7"],
    "trap_dark": ["i", "VI", "i", "VI"],
    "house_deep": ["i7", "v7", "i7", "VI7"],
    "jazz_minor": ["i7", "ii7dim", "V7", "i7"],
    "fifties_rock": ["I", "IV", "V", "IV"],
    "fifties_doo_wop": ["I", "vi", "IV", "V"]
}

# Song Templates (Blueprints)
GENRE_TEMPLATES = {
    "pop": {
        "structure": ["Intro", "Verse 1", "Chorus", "Verse 2", "Chorus", "Bridge", "Chorus", "Outro"],
        "progression_map": {
            "Intro": "pop_1", "Verse 1": "pop_1", "Chorus": "pop_4", 
            "Verse 2": "pop_1", "Bridge": "pop_3", "Outro": "pop_1"
        },
        "tracks": [
            {"name": "Drums", "type": "drums", "instrument": "808 Core Kit"},
            {"name": "Chords", "type": "chords", "instrument": "Grand Piano"},
            {"name": "Bass", "type": "bass", "instrument": "Bass-Hip-Hop Sub"}
        ]
    },
    "house": {
        "structure": ["Intro", "Build", "Drop", "Break", "Drop", "Outro"],
        "progression_map": {
            "Intro": "emotional", "Build": "emotional", "Drop": "pop_4", 
            "Break": "emotional", "Outro": "emotional"
        },
        "tracks": [
            {"name": "Drums", "type": "drums", "instrument": "909 Core Kit"},
            {"name": "Chords", "type": "chords", "instrument": "Pad-Analog"},
            {"name": "Bass", "type": "bass", "instrument": "Bass-Analog"}
        ]
    },
    "jazz": {
        "structure": ["Head", "Solo 1", "Solo 2", "Head"],
        "progression_map": {
            "Head": "jazz_minor", "Solo 1": "jazz_minor", "Solo 2": "jazz_minor"
        },
        "tracks": [
            {"name": "Drums", "type": "drums", "instrument": "Jazz Kit"},
            {"name": "Piano", "type": "chords", "instrument": "Grand Piano"},
            {"name": "Bass", "type": "bass", "instrument": "Upright Bass"}
        ]
    }
}
