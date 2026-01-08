---
description: How to capture MIDI, record sessions, and manage overdubs
---

# Performance Recording

The AI can manage the recording process, allowing the user to focus on performing while the agent handles the "technical" side of session management.

## Capturing MIDI (Retroactive)

If you just played something great but weren't recording, use `capture_midi` to retrieve it.

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Grabs recent MIDI input and puts it into a clip
conn.send_command("capture_midi", {})
```

## Session Recording & Overdub

Control the transport state for layered performances.

```python
# Enable/Disable Overdub (layering MIDI without erasing)
conn.send_command("set_overdub", {"overdub": True})

# Trigger Session Record
# Plays the current slot and starts recording into it
conn.send_command("trigger_session_record", {})

# Toggle Session Record (Global)
conn.send_command("set_session_record", {"recording": True})

## Recording Automation

To record parameter movements into clips:

```python
# 1. Enable Automation Arm (essential!)
conn.send_command("set_session_automation_record", {"enabled": True})

# 2. Arm the track and start recording
conn.send_command("set_track_arm", {"track_index": 0, "arm": True})
conn.send_command("trigger_session_record", {})
```

## Managing Overrides

If you manually change an automated parameter, the automation deactivates. Use **Re-Enable Automation** to return to the recorded movements.

```python
# Re-enable specific parameter
conn.send_command("re_enable_automation", {
    "track_index": 0,
    "device_index": 0,
    "parameter_index": 0
})

# Re-enable all parameters in the song
conn.send_command("re_enable_all_automation", {})
```
```

## Workflow: "Capture and Next"

A common performance strategy: Capture the current playing clips into a new scene and move on.

```python
# 1. Capture current arrangement/playing state into a new scene
conn.send_command("capture_and_insert_scene", {})

# 2. Fire the next (empty) scene to keep the momentum
conn.send_command("fire_scene", {"index": -1})
```

## Record Quantization

```python
# Set record quantization (0=None, 1=1/4, 2=1/8, 3=1/8T, etc.)
conn.send_command("set_record_quantization", {"quantization": 4}) # 1/16
```
