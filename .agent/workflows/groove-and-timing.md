---
description: How to manage Groove Pool, swing, and clip timing
---

# Groove & Timing

Manipulate the rhythmic feel of your session using the Groove Pool and global timing controls.

## Global Swing & Groove

Apply a rhythmic "lean" to the entire session.

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Set global swing (0.0 to 1.0)
conn.send_command("set_swing_amount", {"amount": 0.5})

# Scaler for ALL active grooves in the session (0.0 to 1.3)
conn.send_command("set_groove_amount", {"amount": 1.0})
```

## Groove Pool Parameters

Each groove in the pool has real-time controls that affect all clips assigned to it:

| Parameter | Function |
|:---|:---|
| **Base** | The timing resolution (1/4, 1/8, etc.) against which groove notes are measured. |
| **Quantize** | Amount of "straight" quantization applied *before* the groove takes effect (0-100%). |
| **Timing** | Intensity of the groove's rhythmic pattern. |
| **Random** | Adds subtle timing fluctuations (per voice) for humanization. |
| **Velocity** | Scales the note velocities based on the groove's velocity data (-100 to +100%). |

## Clip Grooves

Assign specific groove files from the Groove Pool to individual clips.

```python
# 1. List available grooves in the pool
pool = conn.send_command("get_groove_pool", {})
print(pool) # List of groove names/indices

# 2. Assign groove to a clip (Audio requires Warping enabled)
conn.send_command("set_clip_groove", {
    "track_index": 0,
    "clip_index": 0,
    "groove_name": "MPC 16 Swing-62"
})

# 3. Commit groove
# Writes timing to MIDI notes or creates Warp Markers in Audio clips.
conn.send_command("commit_groove", {
    "track_index": 0,
    "clip_index": 0
})
```

## Extracting & Editing Grooves

- **Extract Groove**: Drag any audio/MIDI clip to the Groove Pool to capture its timing and velocity characteristics.
- **Edit Groove**: Drag a groove from the pool onto a MIDI track to edit its notes manually, then extract it back.

## Creative Strategies

### Non-Destructive Quantization
To use the Groove Pool as a real-time quantizer without rhythmic "swing":
1. Set **Timing**, **Random**, and **Velocity** to 0%.
2. Adjust **Quantize** and **Base** to taste.

### Humanized Layering
Duplicate a track and apply a groove with high **Random** to only *one* of the tracks. This creates realistic "doubling" (e.g., for string sections or vocals) as the two layers drift randomly against each other.

### Single-Voice Grooving
In a Drum Rack, extract a specific chain (e.g., the Snare) to its own track. This allows you to apply a "lazy" or "laid-back" groove to the snare while keeping the hi-hats perfectly on the grid.

## Groove Information

```python
# Get current groove settings for a clip
details = conn.send_command("get_clip_details", {
    "track_index": 0, 
    "clip_index": 0
})
print(details.get("groove_name"))
```
