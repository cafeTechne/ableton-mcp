---
description: How to use specialized devices (EQ8, Compressor) with surgical control
---

# Specialized Device Control

Certain native Ableton devices have extra MCP tools for surgical control that bypasses standard parameter automation.

## EQ Eight (EQ8)

Control individual bands and filter types.

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Configure Band 1 as a High Pass filter
conn.send_command("set_eq8_band", {
    "track_index": 0,
    "band_index": 1,
    "enabled": True,
    "freq": 0.1, # Normalized 100Hz approx
    "filter_type": 0 # 0=High Pass, 1=Low Shelf, etc.
})

# Boost Band 3 (Peak)
conn.send_command("set_eq8_band", {
    "track_index": 0,
    "band_index": 3,
    "gain": 0.6, # +3dB approx
    "q": 0.5
})
```

## Compressor

Manage sidechain routing and activation.

```python
conn.send_command("set_compressor_sidechain", {
    "track_index": 1, # Bass
    "enabled": True,
    "source_track_index": 2, # Kick
    "gain": 0.5,
    "mix": 1.0
})
```

## External Instrument

The **External Instrument** device allows you to integrate hardware synthesizers and multi-timbral plug-ins as if they were internal devices.

```python
# Configure External Instrument
conn.send_command("set_external_instrument_routing", {
    "track_index": 0,
    "device_index": 0,
    "midi_to_type": "Ext. Out",
    "midi_to_channel": "Channel 1",
    "audio_from": "1/2 (Stereo)",
    "gain": 0.85, # Unity
    "hardware_latency": 15.0 # ms
})
```

### Hardware Integration Tips
- **Analog Devices**: Set latency in **milliseconds** to maintain timing when changing sample rates.
- **Digital Devices**: Set latency in **samples** for surgical precision.
- **Local Off**: When using a keyboard synth, ensure its "Local Off" setting is enabled to avoid MIDI loops (Live should act as the central hub).

## Device Information

```python
# Get specialized details (different from standard get_device_info)
info = conn.send_command("get_specialized_device_info", {
    "track_index": 0,
    "device_index": 0
})
```

## Auto Filter

Analog-modeled filter with multiple **Circuit Types** that emulate classic hardware.

| Circuit | Based On | Notes |
|:---|:---|:---|
| Clean | EQ Eight | CPU-efficient, transparent |
| OSR | British monosynth | Hard-clipping diode limits resonance |
| MS2 | Japanese semi-modular (Korg) | Soft-clipping, warm |
| SMP | Custom hybrid | Blends MS2 + PRD characteristics |
| PRD | US ladder (Moog) | No explicit resonance limiting |

> [!TIP]
> With non-Clean circuits, resonance above 100% enables **self-oscillation**.

```python
conn.send_command("set_device_parameter", {
    "track_index": 0, "device_index": 0, "parameter_name": "Circuit", "value": 0.4 # PRD
})
```

## Amp & Cabinet (Guitar Rig)

**Amp** emulates 7 classic guitar amps. **Cabinet** adds speaker/microphone emulation.

- **Pair them**: Cabinet is designed to follow Amp.
- **Mic Position**: Near On-Axis (bright), Near Off-Axis (resonant), Far (balanced).
- **Creative Use**: Feed drums, synths, or vocals through Amp for analog grit.

```python
# Load Amp and Cabinet onto a track
conn.send_command("search_and_load_device", {"track_index": 0, "query": "Amp", "category": "audio_effects"})
conn.send_command("search_and_load_device", {"track_index": 0, "query": "Cabinet", "category": "audio_effects"})
```
