---
description: How to use per-note probability and velocity deviation for humanization
---

# Humanization & Expressivity

Beyond standard quantization, AbletonMCP allows for surgical humanization of every MIDI note using advanced properties introduced in Live 11.

## Per-Note Properties

Use `update_notes` to inject life into rigid MIDI patterns.

**Note**: All `apply_note_modifications` calls STRICTLY require a `MidiNoteVector` C++ object. You must use the object returned by `get_notes_extended` and pass it back. See `AGENTS.md` for details.

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Get existing notes first to obtain note_ids
data = conn.send_command("get_notes_extended", {
    "track_index": 0, 
    "clip_index": 0
})
notes = data.get("notes", [])

# Apply humanization to each note
for note in notes:
    # 1. Randomize velocity within a deviation range (0-127)
    # Recommended range: 10-30 for noticeable feel
    note["velocity_deviation"] = 20 
    
    # 2. Add probability for rhythmic variation (0.0 to 1.0)
    # Recommended: 0.95-1.0 for subtle variation
    if note["pitch"] == 42: # Hi-Hat
        note["probability"] = 0.95
    
    # 3. Soften note releases
    note["release_velocity"] = 48

# Push updates back to Ableton
conn.send_command("update_notes", {
    "track_index": 0,
    "clip_index": 0,
    "notes": notes
})
```

## Humanization Strategies

### 1. Ghost Note Randomization
Select lower-velocity notes and give them a 50-70% probability to create a dynamic, evolving groove.

### 2. Micro-Timing (Human Feel)
Shift the `start_time` of notes slightly forward or backward by a few ticks to simulate a "lazy" or "pushed" feel.
```python
import random
# Shift note start by +/- 0.01 beats
note["start_time"] += random.uniform(-0.01, 0.01)
```

### 3. Audio Humanization
**NOT SUPPORTED**. Audio humanization via pitch envelopes or transposition automation is not supported in the current Remote Script implementation. Please stick to MIDI humanization.

### 4. Velocity Ramping
Use `velocity_deviation` on the first beat of every bar to ground the performance while keeping the internal notes fluid.

### 5. Groove Randomization (Layered Doubling)
Use the **Random** parameter in the **Groove Pool** to create realistic doublings.
1. Duplicate a track (e.g., a vocal or lead synth).
2. Apply a groove to *one* of the tracks.
3. Turn up the groove's **Random** parameter.
This causes the two layers to drift slightly and randomly out of sync, creating a thick, natural texture.

## Verification
Use `focus_view(view="Detail/Clip")` to see the probability and deviation markers appearing in the Clip View.
