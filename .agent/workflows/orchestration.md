---
description: How to generate strings, brass, and woodwind parts
---

# Orchestration

Generate orchestral arrangements that follow chord progressions.

## Strings

```python
generate_strings_advanced(
    track_index=0,
    clip_index=0,
    key="C",
    scale="major",
    progression="I V vi IV",
    style="pop",
    velocity=90,
    octave=4
)
```

### Styles
| Style | Description |
|:---|:---|
| `pop` | Sustained pads |
| `rock` | Power chords |
| `disco` | Octave jumps |
| `jazz` | Voice-led |
| `reggae` | Choppy rhythmic |

## Brass

```python
generate_brass_advanced(
    track_index=1,
    clip_index=0,
    key="C",
    scale="major",
    progression="I V vi IV",
    style="ska",
    velocity=100,
    octave=3
)
```

### Styles
| Style | Description |
|:---|:---|
| `pop` | Stabs and hits |
| `ska` | Offbeat skanks |
| `jazz` | Cool voicings |
| `funk` | Syncopated hits |
| `classical` | Sustained melodic |

## Woodwinds

```python
generate_woodwinds_advanced(
    track_index=2,
    clip_index=0,
    key="C",
    scale="major",
    progression="I V vi IV",
    style="classical",
    velocity=85,
    octave=5
)
```

### Styles
| Style | Description |
|:---|:---|
| `pop` | Simple melodic |
| `classical` | Runs and arpeggios |
| `jazz` | Improvised feel |

## Parameters (All Generators)

| Parameter | Type | Description |
|:---|:---|:---|
| `track_index` | int | Target track |
| `clip_index` | int | Target scene |
| `key` | str | "C", "F#", "Bb", etc. |
| `scale` | str | "major", "minor", "dorian" |
| `progression` | str | "I V vi IV" or preset name |
| `mood` | str | "romantic", "dark", etc. |
| `style` | str | Genre-specific style |
| `velocity` | int | 1-127 |
| `octave` | int | Base octave (4 = middle) |
| `beats_per_chord` | float | Chord duration |
| `total_bars` | int | Override length |

## Full Orchestra Example

```python
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.devices import search_and_load_device
import time

conn = get_ableton_connection()

KEY = "G"
SCALE = "major"
PROG = "I IV V I"

# Strings
result = conn.send_command("create_midi_track", {"index": -1})
strings_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": strings_idx, "name": "Strings"})
search_and_load_device(strings_idx, "String Ensemble", "instruments")
time.sleep(0.5)

generate_strings_advanced(
    track_index=strings_idx, clip_index=0,
    key=KEY, scale=SCALE, progression=PROG,
    style="pop", octave=4
)

# Brass
result = conn.send_command("create_midi_track", {"index": -1})
brass_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": brass_idx, "name": "Brass"})
search_and_load_device(brass_idx, "Brass Section", "instruments")
time.sleep(0.5)

generate_brass_advanced(
    track_index=brass_idx, clip_index=0,
    key=KEY, scale=SCALE, progression=PROG,
    style="pop", octave=3
)

# Woodwinds
result = conn.send_command("create_midi_track", {"index": -1})
winds_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": winds_idx, "name": "Woodwinds"})
search_and_load_device(winds_idx, "Flute", "instruments")
time.sleep(0.5)

generate_woodwinds_advanced(
    track_index=winds_idx, clip_index=0,
    key=KEY, scale=SCALE, progression=PROG,
    style="classical", octave=5
)
```
