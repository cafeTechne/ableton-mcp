---
description: How to generate full songs with blueprints
---

# Song Blueprint

Generate entire songs with tracks, scenes, and clips in one workflow.

## Two-Step Process

1. **`create_song_blueprint`** - Generate JSON plan
2. **`construct_song`** - Build it in Ableton

## Create Blueprint

```python
# Generate blueprint JSON for a genre
blueprint = create_song_blueprint(
    genre="pop",  # pop, jazz, funk, doowop
    key="C",
    scale="major"
)

print(blueprint)  # JSON with tracks, scenes, clips
```

## Construct Song

```python
# Build from blueprint
result = construct_song(blueprint_json=blueprint)
print(result)  # Log of created tracks/scenes
```

## Available Genres

| Genre | Tracks | Style |
|:---|:---|:---|
| `pop` | Drums, Bass, Keys, Strings | Standard pop structure |
| `jazz` | Drums, Walking Bass, Piano | Jazz standards |
| `funk` | Drums, Slap Bass, Keys | Funk grooves |
| `doowop` | Drums, Bass, Piano, Vocals placeholder | 50s style |

## Full Example

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Set tempo first
conn.send_command("set_tempo", {"tempo": 120.0})

# Generate and build
blueprint = create_song_blueprint(genre="funk", key="E", scale="minor")
result = construct_song(blueprint_json=blueprint)

print(result)
```

## Custom Blueprint

You can also create custom blueprints:

```python
import json

custom = {
    "genre": "custom",
    "key": "G",
    "scale": "major",
    "tracks": [
        {"name": "Drums", "type": "drums", "instrument": "808 Kit"},
        {"name": "Bass", "type": "bass", "instrument": "Analog Bass"},
        {"name": "Synth", "type": "chords", "instrument": "Wavetable"},
    ],
    "scenes": [
        {"name": "Intro", "clips": [
            {"track_name": "Drums", "type": "drums", "progression": "pop_1", "bars": 4},
            {"track_name": "Bass", "type": "bass", "progression": "pop_1", "bars": 4},
        ]},
    ]
}

result = construct_song(blueprint_json=json.dumps(custom))
```
