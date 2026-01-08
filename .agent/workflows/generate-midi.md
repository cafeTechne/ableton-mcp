---
description: How to generate MIDI clips (chords, bass, drums, strings)
---

# MIDI Generation

## Workflow

1. Create a MIDI track
2. Load an instrument
3. Create a clip
4. Add notes OR use a generator

## Manual Note Creation

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Create clip (4 beats = 1 bar)
conn.send_command("create_clip", {"track_index": 0, "clip_index": 0, "length": 16.0})

# Add notes
notes = [
    {"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 100},   # C4
    {"pitch": 64, "start": 0.0, "duration": 1.0, "velocity": 100},   # E4
    {"pitch": 67, "start": 0.0, "duration": 1.0, "velocity": 100},   # G4
]
conn.send_command("add_notes_to_clip", {
    "track_index": 0,
    "clip_index": 0,
    "notes": notes
})
```

## Note Format

| Field | Range | Description |
|:---|:---|:---|
| pitch | 0-127 | MIDI note (60=C4, 69=A4) |
| start | 0.0+ | Beat position |
| duration | 0.0+ | Length in beats |
| velocity | 0-127 | Volume (100=default) |

## Chord Generator

```python
# Uses MCP tool
generate_chord_progression_advanced(
    track_index=0,
    clip_index=0,
    key="C",
    scale="major",
    progression="I V vi IV",
    beats_per_chord=4.0,
    voice_lead=True
)
```

## Available Generators

| Tool | Purpose |
|:---|:---|
| `generate_chord_progression_advanced` | Chords with theory |
| `generate_bassline_advanced` | Bass following chords |
| `generate_strings_advanced` | String arrangements |
| `generate_woodwinds_advanced` | Woodwind parts |
| `generate_brass_advanced` | Brass parts |
| `pattern_generator` | Drum patterns |

## Drum Patterns

```python
# four_on_floor, breakbeat, hiphop, etc.
pattern_generator(
    track_index=0,
    clip_slot_index=0,
    pattern_type="four_on_floor",
    bars=4,
    velocity=100,
    swing=0.1
)
```

## Clip Operations

```python
# Fire clip
conn.send_command("fire_clip", {"track_index": 0, "clip_index": 0})

# Stop clip
conn.send_command("stop_clip", {"track_index": 0, "clip_index": 0})

# Delete clip
conn.send_command("delete_clip", {"track_index": 0, "clip_index": 0})
```

## MIDI Effect Devices

MIDI effects process note data **before** it reaches the instrument.

| Device | Purpose |
|:---|:---|
| **Arpeggiator** | Plays held notes as a rhythmic pattern. `/arpeggiator` workflow for details. |
| **Chord** | Adds up to 6 additional notes to each incoming note (±36 semitones). |
| **Note Length** | Changes note duration. Can trigger notes from Note Off for "strum" effects. |
| **Pitch** | Transposes all notes by ±128 semitones. |
| **Random** | Randomly alters pitch based on Chance/Choices/Scale. |
| **Scale** | Forces notes to a specific scale (12x12 map). |
| **Velocity** | Compresses, expands, or randomizes note velocity. |

```python
# Load the Scale MIDI effect
conn.send_command("search_and_load_device", {
    "track_index": 0, "query": "Scale", "category": "midi_effects"
})
```

> [!TIP]
> Chain **Random** → **Scale** to create a step-sequencer-like effect constrained to a musical key.
