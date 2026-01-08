---
description: How to use unlinked envelopes, sample scrambling, and template clips
---

# Creative Sound Design

Ableton Live's clip envelopes are powerful tools for non-destructive sound design. By unlinking envelopes and modulating sample properties, you can create complex, generative patterns from simple loops.

## Unlinked Envelope Loops (LFO Style)

You can create an envelope that is longer or shorter than the clip itself. For example, a 1-bar drum loop can have an 8-bar volume fade or a 4-bar filter sweep.

> [!NOTE]
> To "unlink" an envelope in the Live UI, click the **Linked/Unlinked** toggle in the Clip Envelopes tab. Once unlinked, you can use the following MCP commands to define the pattern.

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# 1. Create a 4-bar filter sweep on a 1-bar loop
# (Assuming the envelope is unlinked in the UI)
for bar in range(4):
    conn.send_command("insert_envelope_step", {
        "track_index": 0,
        "clip_index": 0,
        "device_id": 0, # Auto-Filter index
        "parameter_id": "Frequency",
        "time": bar * 4.0,
        "length": 4.0,
        "value": 0.2 + (bar * 0.2) # Ramping up
    })
```

## Sample Scrambling (Audio Clips)

Use the **Sample Offset** envelope to rearrange beats within an audio clip without destructive editing.

```python
# Create a "scrambled" rhythmic pattern
# 0.0 is center, positive values move to "future", negative to "past"
conn.send_command("insert_envelope_step", {
    "track_index": 0,
    "clip_index": 0,
    "device_id": "Clip",
    "parameter_id": "Sample Offset",
    "time": 0.0,
    "length": 0.25, # 1/16th note
    "value": 0.6    # Displace the playhead
})
```

### The "Escalator" Shape
Drawing a downward "escalator" shape in the Sample Offset envelope effectively repeats the same slice of audio, creating a stutter effect.

## Using Clips as Templates

Once you have a complex set of envelopes on a clip, you can swap the sample while keeping the modulation intact.

1.  Create your "Template Clip" with intricate envelopes.
2.  Use `load_browser_item` to drag a new sample onto the **Clip View** (Detail View) while the template clip is selected.
3.  The envelopes will now modulate the new sound.

## Creative Strategies

- **Polyrhythmic Modulation**: Set your unlinked envelope loop length to an odd number (e.g., 3.2.1) while your clip loop is 4.0.0. The modulation will shift in relation to the rhythm, creating an evolving texture.
- **Generative Pads**: Use a long unlinked Transposition envelope (pitch) to turn a short atmospheric sample into a slowly evolving melody.
