---
description: How to use Ableton's Arpeggiator device
---

# Arpeggiator

The Arpeggiator takes held notes (chords or single notes) and plays them as a rhythmic pattern.

## Style & Rate

- **Style**: Determines note sequence (Up, Down, UpDown, Converge, Diverge, Pinky, Thumb, Random, Chord Trigger).
- **Rate**: Speed of the pattern, synced to tempo or free (ms).
- **Gate**: Note length as a percentage of the Rate (100% = full duration, 200% = legato overlap).

```python
# Set Arpeggiator Rate to 1/16th notes
conn.send_command("set_device_parameter", {
    "track_index": 0, "device_index": 0, "parameter_name": "Sync Rate", "value": 0.25
})
```

## Key Features

| Control | Purpose |
|:---|:---|
| **Hold** | Pattern continues after keys are released. Add/remove notes by playing them again. |
| **Offset** | Shifts the pattern start point (rotates the sequence). |
| **Repeats** | Limits the number of times the pattern cycles (inf = forever). |
| **Retrigger** | Resets the pattern on Note, Beat, or Off. |

## Transposition & Dynamics

- **Transpose Mode**: Shift (semitones), Major, or Minor.
- **Distance**: Interval between transposition steps.
- **Steps**: Number of times to transpose.
- **Velocity Section**: Decay towards a target velocity over time.

> [!TIP]
> Use **Hold** + **Beat Retrigger** to create rhythmically synced arpeggios that reset on the downbeat.
