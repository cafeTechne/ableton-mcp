---
description: How to create, fire, and manage scenes
---

# Scene Operations

Scenes are horizontal rows in Session View - firing a scene plays all clips in that row.

## Get Current Scenes

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

context = conn.send_command("get_song_context", {"include_clips": False})
scenes = context.get("scenes", [])

for scene in scenes:
    print(f"{scene['index']}: {scene.get('name', 'Untitled')}")
```

## Create Scene

```python
# Append to end
result = conn.send_command("create_scene", {"index": -1, "name": "Chorus"})
new_idx = result.get("index")

# Insert at specific position
result = conn.send_command("create_scene", {"index": 2, "name": "Verse 2"})
```

## Fire Scene

```python
# Fire scene (plays all clips in that row)
conn.send_command("fire_scene", {"index": 0})

# New: Fire by name directly
conn.send_command("fire_clip_by_name", {"clip_pattern": "Chorus"})
conn.send_command("fire_scene_by_name", {"pattern": "Chorus"})
```

## Scene Properties

```python
# Set scene tempo and time signature
conn.send_command("set_scene_tempo", {"scene_index": 0, "tempo": 124.0})
conn.send_command("set_scene_time_signature", {"scene_index": 0, "numerator": 3, "denominator": 4})

# Move or Duplicate
conn.send_command("move_scene", {"scene_index": 0, "target_index": 2})
conn.send_command("duplicate_scene", {"scene_index": 0})
```

## Scene Information

```python
# Get detailed info about a specific scene
info = conn.send_command("get_scene_info", {"scene_index": 0})
print(info) # { "name": "Chorus", "tempo": 124.0, "color": 12345, ... }

# Get overview of all scenes
overview = conn.send_command("get_scene_overview", {})
```

## Delete Scene

```python
# ⚠️ Use with caution - deletes all clips in that row
conn.send_command("delete_scene", {"index": 3})
```

## Common Patterns

### Create Song Structure
```python
sections = ["Intro", "Verse 1", "Chorus", "Verse 2", "Chorus", "Bridge", "Outro"]

for name in sections:
    conn.send_command("create_scene", {"index": -1, "name": name})
```

### Fire Scene by Name (Native Tool)
```python
# The server now has native support for this
conn.send_command("fire_scene_by_name", {"pattern": "Chorus", "match_mode": "contains"})
```
