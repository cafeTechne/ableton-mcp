---
description: How to control tempo and playback
---

# Transport Control

## Get Current State

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

context = conn.send_command("get_song_context", {"include_clips": False})
print(f"Tempo: {context.get('tempo')} BPM")
print(f"Playing: {context.get('is_playing')}")
```

## Set Tempo

```python
# Range: 20-999 BPM
conn.send_command("set_tempo", {"tempo": 120.0})
```

## Start Playback

```python
conn.send_command("start_playback", {})
```

## Stop Playback

```python
conn.send_command("stop_playback", {})
```

## Advanced Transport

```python
# Tap Tempo
conn.send_command("tap_tempo", {})

# Nudge Tempo
conn.send_command("nudge_tempo", {"direction": "up", "active": True}) # Hold nudge
conn.send_command("nudge_tempo", {"direction": "up", "active": False}) # Release nudge

# Jump & Scrub
conn.send_command("jump_by", {"beats": 4.0}) # Jump forward 1 bar
conn.send_command("scrub_song", {"beats": -16.0}) # Set loop to 4 bars starting at bar 1
conn.send_command("set_loop", {"enabled": True, "start": 0.0, "length": 4.0})

## Crossfader & Cueing

The Crossfader allows for VCA-style blending between any number of tracks assigned to A or B.

```python
# 1. Global Crossfader position (-1.0 to 1.0)
conn.send_command("set_crossfader", {"value": -1.0}) # Hard Left (A)

# 2. Track Assignment
# 0=None, 1=A, 2=B
conn.send_command("set_track_crossfade_assignment", {
    "track_index": 0, 
    "assignment": 1 # Assign to A
})

# 3. Cueing (DJ Preview)
# Adjust headphones volume for cued tracks
conn.send_command("set_cue_volume", {"volume": 0.85})
```

### Crossfader Curves
Right-click the crossfader in the UI to select between 7 curves (Constant Power, Dipped, etc.) to match your performance style.
```

## Tempo Automation

The song tempo can be automated just like any other parameter. This is handled on the **Master Track**.

```python
# Create a tempo ramp from 120 to 128 BPM
for beat in range(8):
    conn.send_command("insert_envelope_step", {
        "track_index": -1, # Master Track reference
        "clip_index": -1,  # Arrangement reference
        "device_id": "mixer",
        "parameter_id": "Song Tempo",
        "time": float(beat),
        "length": 1.0,
        "value": (120 + beat) / 200.0 # Normalized value (0.0=20BPM, 1.0=999BPM)
    })
```

## Groove & Swing

```python
# Set global swing amount
conn.send_command("set_swing_amount", {"amount": 0.3}) # 30% swing
```

## Common Patterns

### Setup Session Tempo
```python
GENRES = {
    "house": 124,
    "techno": 130,
    "hip_hop": 90,
    "drum_and_bass": 174,
    "reggae": 80,
    "rock": 120,
    "ballad": 70,
}

genre = "house"
conn.send_command("set_tempo", {"tempo": float(GENRES[genre])})
```

### Preview and Stop
```python
import time

# Fire a scene and let it play
conn.send_command("fire_scene", {"index": 0})
conn.send_command("start_playback", {})

# Preview for 8 seconds
time.sleep(8)

conn.send_command("stop_playback", {})
```
