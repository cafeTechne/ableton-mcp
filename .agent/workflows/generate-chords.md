---
description: How to generate chord progressions with music theory
---

# Chord Generation

## Quick Start

```python
# Uses the advanced generator with full theory support
generate_chord_progression_advanced(
    track_index=0,
    clip_index=0,
    key="C",
    scale="major",
    progression="I V vi IV",
    beats_per_chord=4.0,
    voice_lead=True,
    octave=4
)
```

## Parameters

| Parameter | Options | Default |
|:---|:---|:---|
| key | C, D, E, F, G, A, B (+ #/b) | C |
| scale | major, minor, harmonic_minor, dorian | major |
| progression | Roman numerals or preset name | "pop_1" |
| mood | romantic, hopeful, dark, mysterious | None |
| beats_per_chord | 1.0, 2.0, 4.0, 8.0 | 4.0 |
| rhythm_style | whole, arp, stab | whole |
| voice_lead | true/false | false |
| octave | 2-6 | 4 |

## Common Progressions

| Name | Numerals | Style |
|:---|:---|:---|
| Pop | I V vi IV | Uplifting |
| Doo-Wop | I vi IV V | 50s classic |
| Jazz | ii V I | Jazz standards |
| Blues | I7 IV7 V7 | Blues |
| Sad | vi IV I V | Melancholy |
| Rock | I IV V | Classic rock |

## Mood-Based Generation

```python
# Let the generator pick progression based on mood
generate_chord_progression_advanced(
    track_index=0,
    clip_index=0,
    key="A",
    scale="minor",
    mood="mysterious",
    beats_per_chord=4.0,
    total_bars=8
)
```

## Custom Progressions

You can supply raw Roman Numerals instead of a preset name.

```python
# Custom "Axis" progression
generate_chord_progression_advanced(
    track_index=0,
    clip_index=0,
    key="D",
    scale="minor",
    progression="VI VII i i",  # Bb C Dm Dm in D minor
    voice_lead=True
)
```

### Supported Symbols
- **Basic**: `I` (Major), `i` (Minor)
- **7ths**: `IM7`, `i7`, `V7`, `dim7`
- **Extensions**: `add9`, `sus4`, `sus2`
- **Accidentals**: `bVI` (Flat 6), `#iv` (Sharp 4)

Examples:
- `"I V vi IV"` (Pop)
- `"ii V I"` (Jazz)
- `"i bVII bVI V"` (Andalusian/Metal)
```

## With Instrument Loading

```python
# Full workflow
conn.send_command("search_and_load_device", {
    "track_index": 0,
    "query": "Grand Piano",
    "category": "instruments"
})

import time
time.sleep(1.0)

generate_chord_progression_advanced(
    track_index=0,
    clip_index=0,
    key="Eb",
    scale="major",
    progression="I vi IV V",
    voice_lead=True
)
```

## Related Workflows

- `/generate-midi` - Manual note creation
- `/generate-bass` - Bass following chords
- `/load-device` - Loading instruments
