---
description: How to select, humanize, and bulk-edit MIDI notes in clips
---

# MIDI Editing & Humanization

The AI can manipulate existing MIDI clips with surgical precision, going beyond simple note generation.

## Selection Controls

Precise control over which notes are targeted for manipulation.

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Selection
conn.send_command("select_all_notes", {"track_index": 0, "clip_index": 0})
conn.send_command("deselect_all_notes", {"track_index": 0, "clip_index": 0})
```

## Humanization & Expressivity

Apply probability and velocity variation to make patterns feel more "alive."

```python
# Set probability (0.0 to 1.0)
# Make a high-hat pattern slightly unpredictable
conn.send_command("update_notes", {
    "track_index": 0, 
    "clip_index": 0,
    "notes": [
        {"pitch": 42, "time": 0.0, "duration": 0.25, "probability": 0.8},
        {"pitch": 42, "time": 0.25, "duration": 0.25, "probability": 0.6}
    ]
})

# Set velocity deviation
# Add natural dynamic variation to a piano part
conn.send_command("update_notes", {
    "track_index": 0, 
    "clip_index": 0,
    "notes": [
        {"pitch": 60, "time": 0.0, "velocity_deviation": 10},
        {"pitch": 64, "time": 0.0, "velocity_deviation": 10}
    ]
})
```

## Bulk Operations

Replace or append large blocks of notes.

```python
# Replace all selected notes with a new sequence
# notes is a JSON array of note objects
conn.send_command("replace_selected_notes", {
    "track_index": 0, 
    "clip_index": 0,
    "notes": [
        {"pitch": 36, "time": 0.0, "duration": 4.0},
        {"pitch": 48, "time": 4.0, "duration": 4.0}
    ]
})
```

## Clip Transformations

```python
# Transpose a clip by semitones
conn.send_command("transpose_clip", {"track_index": 0, "clip_index": 0, "semitones": 7})

# Quantize a clip (grid: 5=1/16, amount: 0.0 to 1.0)
conn.send_command("quantize_clip", {
    "track_index": 0, 
    "clip_index": 0, 
    "grid": 5, 
    "amount": 1.0
})
```
