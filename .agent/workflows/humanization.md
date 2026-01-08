---
description: How to use per-note probability and velocity deviation for humanization
---

# Humanization & Expressivity

Beyond standard quantization, AbletonMCP allows for surgical humanization of every MIDI note using advanced properties introduced in Live 11.

## Per-Note Properties

Use `update_notes` to inject life into rigid MIDI patterns.

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
    note["velocity_deviation"] = 10 
    
    # 2. Add probability for rhythmic variation (0.0 to 1.0)
    # Perfect for ghost notes or hi-hat rolls
    if note["pitch"] == 42: # Hi-Hat
        note["probability"] = 0.85
    
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

## Audio Humanization (Pitch Tuning)

For audio clips, humanization is achieved via **Transposition Envelopes**. This allows for correcting or stylizing the pitch of individual notes within a recording.

```python
# 1. Target the Transposition envelope in the Clip device
# This is an additive offset to the clip's main transpose setting.
conn.send_command("insert_envelope_step", {
    "track_index": 1,
    "clip_index": 0,
    "device_id": "Clip",
    "parameter_id": "Transposition",
    "time": 0.0,
    "length": 0.25, # The duration of a single note
    "value": 0.52   # +1 semitone (normalized)
})
```

### Strategy: Vocal Tuning
Layer subtle modulation onto a vocal audio clip to simulate natural pitch drift or to create a "chopped" melodic sequence from a single sustained note.

### 3. Velocity Ramping
Use `velocity_deviation` on the first beat of every bar to ground the performance while keeping the internal notes fluid.

### 4. Groove Randomization (Layered Doubling)
Use the **Random** parameter in the **Groove Pool** to create realistic doublings.
1. Duplicate a track (e.g., a vocal or lead synth).
2. Apply a groove to *one* of the tracks.
3. Turn up the groove's **Random** parameter.
This causes the two layers to drift slightly and randomly out of sync, creating a thick, natural texture.

## Verification
Use `focus_view(view="Detail/Clip")` to see the probability and deviation markers appearing in the Clip View.
