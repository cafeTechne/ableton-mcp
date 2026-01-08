---
description: How to get track and session information from Ableton
---

# Track and Session Info

## Get Full Session Overview

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Get all tracks, scenes, tempo
info = conn.send_command("get_song_context", {"include_clips": False})

print(f"Tempo: {info['tempo']} BPM")
print(f"Tracks: {len(info['tracks'])}")
print(f"Scenes: {len(info['scenes'])}")
```

## Get Single Track Details

```python
info = conn.send_command("get_track_info", {"track_index": 0})

print(f"Name: {info['name']}")
print(f"Volume: {info['volume']}")
print(f"Panning: {info['panning']}")
print(f"Devices: {len(info.get('devices', []))}")
```

## List All Tracks

```python
context = conn.send_command("get_song_context", {"include_clips": False})
for track in context['tracks']:
    print(f"{track['index']}: {track['name']} ({'MIDI' if track['is_midi_track'] else 'Audio'})")
```

## List Devices on Track

```python
info = conn.send_command("get_track_info", {"track_index": 0})
for dev in info.get("devices", []):
    print(f"  {dev['index']}: {dev['name']} ({dev['class_name']})")
```

## Get Device Parameters

```python
params = conn.send_command("get_device_parameters", {
    "track_index": 0,
    "device_index": 0
})
for p in params.get("parameters", [])[:10]:  # First 10
    print(f"  {p['name']}: {p['value']}")
```

## Response Fields

### Track Info
| Field | Type | Description |
|:---|:---|:---|
| name | string | Track name |
| index | int | Track index |
| is_midi_track | bool | MIDI or Audio |
| volume | float | 0.0-1.0 |
| panning | float | -1.0 to 1.0 |
| devices | list | Device chain |
| sends | list | Send levels |

### Device Info
| Field | Type | Description |
|:---|:---|:---|
| name | string | Display name |
| class_name | string | Internal class (e.g., "Eq8") |
| index | int | Position in chain |

## Common Patterns

### Find Track by Name
```python
context = conn.send_command("get_song_context", {"include_clips": False})
for track in context['tracks']:
    if "Vocal" in track['name']:
        print(f"Found vocal at index {track['index']}")
```

### Find Device by Type
```python
info = conn.send_command("get_track_info", {"track_index": 0})
for dev in info.get("devices", []):
    if "eq" in dev['class_name'].lower():
        print(f"EQ at device index {dev['index']}")
```
