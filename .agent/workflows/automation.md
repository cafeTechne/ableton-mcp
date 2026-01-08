---
description: How to apply parameter automation
---

# Automation

Create parameter ramps and changes over time. Understanding the difference between **Automation** and **Modulation** is key to managing a mix without "fighting" the AI.

## Automation vs. Modulation

| Feature | Automation (Red) | Modulation (Blue) |
|:---|:---|:---|
| **Nature** | Absolute value control | Relative offset control |
| **Interaction** | Defines the "base" position | Moves the value *within* the range allowed by automation |
| **Override** | Manual movement deactivates it | Usually stays active as an offset |
| **Best For** | Static changes, transitions | Generative movement, LFO-style patterns |

## Basic Automation Ramp

```python
apply_automation(
    track_index=0,
    clip_index=0,
    parameter_name="Filter Frequency",
    start_val=0.0,
    end_val=1.0,
    duration_bars=4,
    curve="linear"
)
```

## Parameters

| Parameter | Description |
|:---|:---|
| `track_index` | Target track |
| `clip_index` | Target clip slot |
| `parameter_name` | Device parameter name |
| `start_val` | Starting value (0.0-1.0) |
| `end_val` | Ending value (0.0-1.0) |
| `duration_bars` | Length in bars |
| `curve` | `"linear"` (more curves TBD) |

## Common Patterns

### Filter Sweep
```python
# Low to high filter sweep
apply_automation(
    track_index=0,
    clip_index=0,
    parameter_name="Frequency",
    start_val=0.1,
    end_val=0.9,
    duration_bars=8
)
```

### Volume Fade In
```python
apply_automation(
    track_index=1,
    clip_index=0,
    parameter_name="Track Volume",
    start_val=0.0,
    end_val=0.85,  # 0dB
    duration_bars=4
)
```

### Volume Fade Out
```python
apply_automation(
    track_index=1,
    clip_index=0,
    parameter_name="Track Volume",
    start_val=0.85,
    end_val=0.0,
    duration_bars=4
)
```

## Surgical Envelope Control

For precise, step-based automation (glitch effects, rhythmically gated filters).

```python
# Set a single point or step in a clip envelope
conn.send_command("set_clip_envelope_step", {
    "track_index": 0,
    "clip_index": 0,
    "device_id": "Filter", # or "mixer"
    "parameter_id": "Frequency",
    "time": 1.0, # Beat position
    "length": 0.25, # Duration of step
    "value": 0.8 # Target value
})

# Clear envelope for a specific parameter
conn.send_command("clear_clip_envelope", {
    "track_index": 0,
    "clip_index": 0,
    "device_id": "mixer",
    "parameter_id": "Track Volume"
})
```

## Finding Parameter Names

```python
# Get device parameters to find exact names
params = conn.send_command("get_device_parameters", {
    "track_index": 0,
    "device_index": 0
})

for p in params.get("parameters", []):
    print(f"{p['name']}: {p['value']}")
```

## Notes

- Parameter values are typically normalized (0.0-1.0)
- Clip must exist before applying automation
- Some parameters may not be automatable
