---
description: How to generate drum patterns
---

# Drum Patterns

Generate MIDI drum patterns with the `pattern_generator` tool.

## Basic Usage

```python
pattern_generator(
    track_index=0,
    clip_slot_index=0,
    pattern_type="four_on_floor",
    bars=4,
    velocity=100
)
```

## Pattern Types

| Pattern | Style | Description |
|:---|:---|:---|
| `four_on_floor` | House/Disco | Kick on every beat |
| `breakbeat` | Breakbeat/DnB | Syncopated breaks |
| `hiphop` | Hip-Hop | Boom-bap style |
| `trap` | Trap | Hi-hat rolls, sparse kicks |
| `rock_basic` | Rock | Standard 4/4 rock |

## Parameters

| Parameter | Range | Description |
|:---|:---|:---|
| `track_index` | 0+ | Target track |
| `clip_slot_index` | 0+ | Target scene |
| `pattern_type` | see above | Drum style |
| `bars` | 1-16 | Pattern length |
| `root_note` | 36-60 | Base MIDI note (36=C1 kick) |
| `velocity` | 1-127 | Hit strength |
| `swing` | 0.0-1.0 | Swing amount |
| `humanize` | 0.0-1.0 | Timing variation |
| `fill` | true/false | Add fill at end |

## Common Patterns

### House Beat
```python
pattern_generator(
    track_index=0,
    clip_slot_index=0,
    pattern_type="four_on_floor",
    bars=4,
    velocity=110,
    swing=0.1
)
```

### Trap Beat with Fill
```python
pattern_generator(
    track_index=0,
    clip_slot_index=0,
    pattern_type="trap",
    bars=4,
    velocity=100,
    fill=True
)
```

### Humanized Rock
```python
pattern_generator(
    track_index=0,
    clip_slot_index=0,
    pattern_type="rock_basic",
    bars=4,
    velocity=105,
    humanize=0.2
)
```

## Full Workflow

```python
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.devices import search_and_load_device
import time

conn = get_ableton_connection()

# 1. Create drum track
result = conn.send_command("create_midi_track", {"index": -1})
drums_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": drums_idx, "name": "Drums"})

# 2. Load drum kit
search_and_load_device(drums_idx, "808 Core Kit", "drums")
time.sleep(1.0)

# 3. Generate pattern
pattern_generator(
    track_index=drums_idx,
    clip_slot_index=0,
    pattern_type="hiphop",
    bars=4,
    velocity=100
)

# 4. Fire to preview
conn.send_command("fire_clip", {"track_index": drums_idx, "clip_index": 0})
```

## MIDI Note Mapping

Standard GM drum mapping:
| Note | Sound |
|:---|:---|
| 36 (C1) | Kick |
| 38 (D1) | Snare |
| 42 (F#1) | Closed Hi-Hat |
| 46 (A#1) | Open Hi-Hat |
| 49 (C#2) | Crash |
| 51 (D#2) | Ride |
