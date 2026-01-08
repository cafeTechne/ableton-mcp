---
description: How to load samples into Simpler and Sampler
---

# Sample Loading

Load audio samples into Simpler, Sampler, or directly to clips.

## Load Sample by Name

```python
# Searches browser and loads to track
load_sample_by_name(
    sample_name="808 Kick",
    track_index=0,
    clip_index=0,
    category="sounds",
    fire=False
)
```

## Load into Simpler

```python
# Creates Simpler and loads sample
load_simpler_with_sample(
    track_index=0,
    file_path="kick_808.wav"
)
```

## Load into Sampler

```python
# Creates Sampler and loads sample
load_sampler_with_sample(
    track_index=0,
    file_path="piano_c3.wav"
)
```

## Categories

| Category | Content |
|:---|:---|
| `sounds` | Audio files, loops, one-shots |
| `samples` | Raw sample files |
| `drums` | Drum kits and samples |
| `all` | Search everything |

## Helper Function Pattern

```python
from mcp_tooling.ableton_helpers import load_sample_to_simpler

# Intelligent loading with fallback
success = load_sample_to_simpler(
    track_index=0,
    sample_query="House Loop",
    backup_query="Loop"  # Fallback if first query fails
)

if success:
    print("Sample loaded!")
```

## Full Workflow Example

```python
from mcp_tooling.connection import get_ableton_connection
import time

conn = get_ableton_connection()

# 1. Create MIDI track
result = conn.send_command("create_midi_track", {"index": -1})
track_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": track_idx, "name": "Drums"})

# 2. Load sample into Simpler
load_sample_by_name(
    sample_name="Break Loop",
    track_index=track_idx,
    clip_index=0,
    category="samples"
)

time.sleep(1.0)

# 3. Fire to preview
conn.send_command("fire_clip", {"track_index": track_idx, "clip_index": 0})
```

## Notes

- Searches use fuzzy matching
- MIDI tracks auto-create Simpler when loading audio
- Audio tracks load samples directly to clip slots

## Sample Slicing

Manage slices for Simpler in Slice mode or Simpler instances.

```python
# Insert a slice at 1.5 seconds
slice_sample(track_index=0, action="insert", slice_time=1.5)

# Remove a slice
slice_sample(track_index=0, action="remove", slice_time=1.5)

# Clear all manual slices
slice_sample(track_index=0, action="clear")

# Reset slices to auto-detected
slice_sample(track_index=0, action="reset")
```

## Simpler Surgical Edits

Deep control over Simpler device parameters.

```python
# Manipulation
conn.send_command("reverse_simpler_sample", {"track_index": 0, "device_index": 0})
conn.send_command("crop_simpler_sample", {"track_index": 0, "device_index": 0})

# Playback Modes: 0=Classic, 1=One-Shot, 2=Slicing
conn.send_command("set_simpler_playback_mode", {"track_index": 0, "device_index": 0, "mode": 1})

# Markers (0.0 to 1.0)
conn.send_command("set_simpler_sample_markers", {
    "track_index": 0, 
    "device_index": 0, 
    "start": 0.1, 
    "end": 0.8
})

# Warping
conn.send_command("warp_simpler_sample", {"track_index": 0, "device_index": 0, "enabled": True})
```

