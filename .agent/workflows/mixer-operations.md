---
description: How to control track volume, panning, sends, and mute/solo
---

# Mixer Operations

All mixer parameters use **direct values** (not normalized like EQ).

## Volume

```python
# 0.0 = silence, 0.85 = 0dB (unity), 1.0 = +6dB
conn.send_command("set_track_volume", {"track_index": 0, "volume": 0.85})
```

| Value | dB |
|:---|:---|
| 0.0 | -inf (silence) |
| 0.7 | -3 dB |
| 0.85 | 0 dB (unity) |
| 1.0 | +6 dB |

## Panning

```python
# -1.0 = hard left, 0.0 = center, 1.0 = hard right
conn.send_command("set_track_panning", {"track_index": 0, "panning": 0.0})

# Pan Modes: 0=Stereo (Default), 1=Split Stereo
conn.send_command("set_pan_mode", {"track_index": 0, "mode": 1})
```

- **Stereo Pan Mode**: Standard balance control (positions LR signal in stereo field).
- **Split Stereo Pan Mode**: Independent control of Left and Right input channels. Useful for surgical stereo placement.

## Sends

```python
# Send to Return A (index 0)
conn.send_command("set_send_level", {
    "track_index": 0,
    "send_index": 0,  # 0=A, 1=B
    "level": 0.5
})
```

## Mute/Solo/Arm

```python
conn.send_command("set_track_mute", {"track_index": 0, "mute": True})
conn.send_command("set_track_solo", {"track_index": 0, "solo": True})
conn.send_command("set_track_arm", {"track_index": 0, "arm": True})

## Solo and Cueing

Ableton supports two monitoring workflows for the Solo buttons.

```python
# 0=Solo (Default), 1=Cue
conn.send_command("set_solo_cue_mode", {"mode": 1})

# When in Cue Mode, Solo buttons act as Headphone Cues
conn.send_command("set_track_solo", {"track_index": 0, "solo": True})
```

- **Solo Mode**: Standard behavior (mutes all other tracks).
- **Cue Mode**: Routes selected tracks to the "Cue Out" port (Headphones) without affecting the Master output. Essential for DJ-style previewing.

> [!NOTE]
> Ensure `Master Out` and `Cue Out` are mapped to different hardware ports in your Audio Preferences.

## Monitoring Modes

Monitoring determines how input signals are heard through the track.

```python
# Modes: 0=In, 1=Auto, 2=Off
conn.send_command("set_track_monitor", {"track_index": 0, "monitor": 1})
```

- **In**: Record-independent monitoring (Aux style). Clip output is suppressed.
- **Auto**: Monitors only when the track is armed and not playing clips (Default).
- **Off**: Monitoring disabled (useful for direct/hardware monitoring).

## Input & Output Configuration

Tracks use a "Type" and "Channel" chooser pair for patching.

```python
# Set Input (From)
conn.send_command("set_track_input", {
    "track_index": 1,
    "type": "Ext. In",
    "channel": "1/2 (Stereo)"
})

# Set Output (To)
conn.send_command("set_track_output", {
    "track_index": 1,
    "type": "Master"
})
```

### Internal Routing Points

When tapping signal from another track, you can choose the tap point:

- **Pre FX**: Raw signal before track devices/mixer.
- **Post FX**: Signal after device chain, before mixer fader/pan.
- **Post Mixer**: Final track output (Default).

```python
# Receive input from Track 0, Post FX
conn.send_command("set_track_input", {
    "track_index": 1,
    "type": "0-Drums", # Track Index - Name
    "channel": "Post FX"
})
```
```

## Track Names

```python
conn.send_command("set_track_name", {"track_index": 0, "name": "Lead Vocal"})
```

## Get Current Values

```python
info = conn.send_command("get_track_info", {"track_index": 0})
print(f"Volume: {info['volume']}")
print(f"Panning: {info['panning']}")
print(f"Sends: {info['sends']}")
print(f"Muted: {info.get('mute', False)}")
```

## Mix Balance Example

```python
# Set up a basic mix
tracks = [
    (0, 0.85, 0.0, "Drums"),      # Center, unity
    (1, 0.75, 0.0, "Bass"),       # Center, -3dB
    (2, 0.70, -0.3, "Guitar L"),  # Slightly left
    (3, 0.70, 0.3, "Guitar R"),   # Slightly right
    (4, 0.80, 0.0, "Vocal"),      # Center, prominent
]

for idx, vol, pan, name in tracks:
    conn.send_command("set_track_volume", {"track_index": idx, "volume": vol})
    conn.send_command("set_track_panning", {"track_index": idx, "panning": pan})
    conn.send_command("set_track_name", {"track_index": idx, "name": name})
```

## Master & Return Tracks

Return tracks have their own indexing.

```python
# Master controls
conn.send_command("set_master_volume", {"volume": 0.85})
conn.send_command("set_master_pan", {"pan": 0.0})

# Return track controls
conn.send_command("set_return_volume", {"index": 0, "volume": 0.85}) # Return A
conn.send_command("set_return_pan", {"index": 0, "pan": 0.0})
conn.send_command("set_return_track_name", {"index": 0, "name": "Reverb"})

# Global controls
conn.send_command("set_crossfader", {"value": 0.0}) # -1.0 to 1.0
conn.send_command("set_cue_volume", {"volume": 0.85})
```

## Chains & Pads

If a track contains a Drum Rack or Instrument Rack, you can control internal mixer settings.

```python
# Set chain volume (e.g., inside a Drum Rack)
conn.send_command("set_chain_volume", {
    "track_index": 0,
    "device_index": 0,
    "chain_index": 12, # E.g., Clap
    "volume": 0.85
})

## Track Delays

Compensate for acoustic, hardware, or human timing discrepancies.

```python
# Adjust track delay (+/- ms)
conn.send_command("set_track_delay", {
    "track_index": 0,
    "delay": 15.0 # Positive = Late, Negative = Early
})
```

## Mixing Rack Chains

Instrument and Drum Racks can be folded/unfolded in the Session Mixer to show individual parallel chains.

```python
# Fold/Unfold Rack Chains in Session Mixer
conn.send_command("set_rack_mixer_folded", {
    "track_index": 0,
    "device_index": 0,
    "folded": False
})
```

- **Linked Controls**: Changes to volume/pan in the Session Mixer are reflected in the Rack's Chain List immediately.
- **Multiselect**: If multiple chains are selected in the Session Mixer, adjusting one adjusts all (this does **not** happen in the Chain List).

## Extracting Chains

Move parallel chains to their own tracks for independent processing or MIDI manipulation.

| Source Area | Extraction Result |
|:---|:---|
| **Chain List** | Moves only the **devices** to a new track. |
| **Session Mixer** | Moves both **devices** and **MIDI data** (Drum Racks only). |

```python
# Extract snare chain + MIDI notes to its own track
conn.send_command("extract_drum_chain", {
    "track_index": 0,
    "note": 38
})
```

> [!WARNING]
> Changing track delays during playback can cause audio artifacts (clicks/pops). This tool is best used for static mix offsets or Arrangement View alignment.
```
