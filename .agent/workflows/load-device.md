---
description: How to load devices (EQ, Compressor, instruments) onto tracks
---

# Loading Devices

## Quick Reference

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Load any device by name
conn.send_command("search_and_load_device", {
    "track_index": 0,
    "query": "EQ Eight",
    "category": "audio_effects"
})

# Hot-Swap the selected device (Simulates 'Q' key)
conn.send_command("hot_swap_device", {
    "track_index": 0,
    "device_index": 0
})
```

## Device Signal Flow

Devices in Live's chain always travel from **left to right**.

- **MIDI Tracks**: Can host MIDI Effects (left), an Instrument (center), and Audio Effects (right).
- **Audio Tracks**: Host Audio Effects only.
- **Instruments**: Act as a bridge, converting MIDI on the left into Audio on the right.

> [!IMPORTANT]
> Audio effects placed to the left of an instrument in a MIDI track will NOT receive any signal. MIDI effects placed to the right of an instrument will likewise be inactive.

## Categories

| Category | Examples |
|:---|:---|
| `audio_effects` | EQ Eight, Compressor, Reverb, Delay |
| `midi_effects` | Arpeggiator, Chord, Scale |
| `instruments` | Grand Piano, Wavetable, Simpler |
| `drums` | 808, 909, Drum Rack |
| `sounds` | Presets with samples |
| `all` | Search everything |

## Common Devices

```python
# EQ
conn.send_command("search_and_load_device", {"track_index": 0, "query": "EQ Eight", "category": "audio_effects"})

# Compressor
conn.send_command("search_and_load_device", {"track_index": 0, "query": "Glue Compressor", "category": "audio_effects"})

# Reverb
conn.send_command("search_and_load_device", {"track_index": 0, "query": "Reverb", "category": "audio_effects"})

# Piano
conn.send_command("search_and_load_device", {"track_index": 0, "query": "Grand Piano", "category": "instruments"})
```

## Verify Device Loaded

```python
import time
time.sleep(1.0)  # Wait for device to load

info = conn.send_command("get_track_info", {"track_index": 0})
for dev in info.get("devices", []):
    print(f"{dev['index']}: {dev['name']} ({dev['class_name']})")

## Activator & CPU Management

To save CPU cycles without deleting devices, use the **Activator Switch**.

```python
# Turn device OFF (No CPU usage, signal passes unprocessed)
conn.send_command("set_device_activator", {
    "track_index": 0,
    "device_index": 0,
    "on": False
})
```

## Default Presets

You can customize how Live responds to various actions by saving **Default Presets** in your User Library:
- **Dropping Samples**: Save a `Simpler` to `Defaults/Dropping Samples/On Device View`.
- **Slicing**: Save a `Drum Rack` to `Defaults/Slicing`.
- **Audio to MIDI**: Save Racks to `Defaults/Audio to MIDI/Harmony` (or Melody/Drums).
```

## Troubleshooting

| Issue | Solution |
|:---|:---|
| "Browser item not found" | Check spelling, try partial match |
| Device not appearing | Add `time.sleep(1.0)` after load |
| Wrong track | Verify track_index with `get_track_info` first |
