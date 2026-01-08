---
description: How to convert between audio/MIDI and slice samples
---

# Audio & MIDI Conversions

Utilize Ableton's powerful conversion algorithms to bridge the gap between audio and MIDI domains.

## Audio to MIDI (Algorithms)

Extract musical information from audio clips using context-aware algorithms.

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# 1. Convert Harmony: Polyphonic (Chords, Guitars, Piano)
conn.send_command("audio_to_harmony", {"track_index": 0, "clip_index": 0})

# 2. Convert Melody: Monophonic (Singer, Whistling, Solo instrument)
conn.send_command("audio_to_melody", {"track_index": 0, "clip_index": 0})

# 3. Convert Drums: Percussive (Breakbeats, Beatboxing)
# Attempts to map Kick, Snare, and Hats automatically.
conn.send_command("audio_to_drums", {"track_index": 0, "clip_index": 0})
```

### Optimization Tips
- **Clear Attacks**: Notes that "swell" or fade in are hard to detect.
- **Isolated Instruments**: Best results come from unaccompanied audio.
- **High Quality**: Use `.wav` or `.aiff`; lossy `.mp3` files can yield unpredictable results.
- **Transient Tuning**: Since Live uses transient markers for division, manually "tuning" them in the sample editor *before* conversion will improve accuracy.

## Slicing to New MIDI Track

Divides audio into time-based chunks assigned to a chromatic MIDI sequence and a Drum Rack.

```python
# Creates a Drum Rack with one chain per slice
conn.send_command("create_drum_rack_from_audio_clip", {
    "track_index": 0, 
    "clip_index": 0
})
```

### Slicing Workflow
1.  **Macro Control**: Most factory slicing presets map macros to Simplers for envelope, loop, and crossfade control across all slices simultaneously.
2.  **Resequencing**: Once sliced, the MIDI clip forms a "staircase" pattern. Editing these notes allows for immediate rhythmic reconfiguration of the original audio.
3.  **Processing**: Each slice can be processed with unique audio effects. To process groups, select chains and group them into a nested Rack.

## Track Flattening & Formatting

```python
# Convert MIDI track to Audio (Freeze & Flatten equivalent)
conn.send_command("midi_to_audio", {"track_index": 0})

# Consolidate multiple clips into a single new clip
conn.send_command("consolidate_clip", {"track_index": 0, "clip_index": 0})
```

## Resampling (Master Loopback)

Record the output of the session back into an audio track for creative processing or to save CPU.

```python
# 1. Select the track for recording
# 2. Set input to Resampling
conn.send_command("set_track_input", {
    "track_index": 2, 
    "type": "Resampling"
})

# 3. Arm and start recording
conn.send_command("set_track_arm", {"track_index": 2, "arm": True})
conn.send_command("trigger_session_record", {})
```

### Resampling Strategy
- **Master Effects**: Resampling captures the output **after** Master Track processing (Compression/EQ).
- **Cleanup**: Once resampled, you can delete CPU-heavy tracks or effects to free up resources.
- **Immediate Iteration**: Capture a complex rhythmic manipulation from the Crossfader or specialized devices back into a sample for immediate "flipping."
