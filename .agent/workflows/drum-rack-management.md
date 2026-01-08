---
description: How to manage Drum Rack pads, choke groups, and pad solo/mute
---

# Drum Rack Management

Control individual pads and chains within a Drum Rack device.

## Pad Operations

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Solo or Mute specific pads (MIDI notes 0-127)
conn.send_command("solo_drum_pad", {"track_index": 0, "note": 36, "solo": True})
conn.send_command("mute_drum_pad", {"track_index": 0, "note": 38, "mute": True})

# Copy a pad's settings and devices to another note
conn.send_command("copy_drum_pad", {
    "track_index": 0,
    "from_note": 36, 
    "to_note": 48
})
```

## Pad View & Mapping

Each pad in a Drum Rack represents a MIDI note.

- **Dragging Objects**: Dragging a sample to an empty pad creates a `Simpler`.
- **Replacing**: Dropping a new sample on a pad replaces the instrument but keeps existing effects (MIDI/Audio) intact.
- **Layering**: Hold `Alt` (Win) / `Cmd` (Mac) while dragging multiple samples to a single pad to create a nested Instrument Rack.

## Choke Groups

Use Choke Groups to ensure only one sound in a set plays at a time (e.g., Open vs. Closed Hi-hat).

```python
# Set Choke Group (0 = None, 1-16 = Group)
conn.send_command("set_drum_pad_choke_group", {
    "track_index": 0, 
    "note": 46, # Open HH
    "choke_group": 1 
})
conn.send_command("set_drum_pad_choke_group", {
    "track_index": 0, 
    "note": 42, # Closed HH
    "choke_group": 1
})
```

## I/O & Routing

Each drum chain can have unique MIDI MIDI settings.

```python
# Set the MIDI note the chain responds to ("Receive")
# and the note it triggers ("Play")
conn.send_command("set_drum_chain_io", {
    "track_index": 0,
    "chain_index": 0,
    "receive_note": 36, # C1
    "play_note": 60     # C3
})
```

## Internal Return Chains

Drum Racks can host up to 6 internal return chains (e.g., a dedicated Rack Reverb).

```python
# Create a return chain inside the Rack
conn.send_command("create_rack_return_chain", {
    "track_index": 0,
    "device_index": 0
})

# Send signal from a drum pad to the Rack's internal return
conn.send_command("set_rack_chain_send", {
    "track_index": 0,
    "device_index": 0,
    "chain_index": 0,
    "send_index": 0,
    "amount": 0.8
})
```


## Extracting Chains

To move a specific drum voice (e.g., a Snare) and its MIDI data onto its own track:

```python
# 1. Identify the chain in the mixer
# 2. Extract specific chain to its own track
conn.send_command("extract_drum_chain", {
    "track_index": 0,
    "note": 38 # Snare
})
```

> [!TIP]
> This is particularly useful for applying **independent grooves** to different drum sounds, such as keeping the hi-hats on the grid while making the snare "lazy" (slightly behind the beat).

## Drum Rack Inspection

```python
# Get all pads and their chain names
info = conn.send_command("get_drum_rack_info", {
    "track_index": 0, 
    "include_empty": False
})

for pad in info.get("pads", []):
    print(f"Note {pad['note']}: {pad['name']}")
```
