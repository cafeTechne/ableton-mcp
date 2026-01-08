---
description: How to configure EQ Eight parameters (CRITICAL: use normalized values)
---

# EQ Configuration

## ⚠️ Critical Warning

**All EQ parameters use normalized 0.0-1.0 values, NOT Hz or dB!**

```python
# ❌ WRONG - This will SILENCE the track
conn.send_command("set_eq8_band", {"track_index": 0, "band_index": 1, "freq": 180})

# ✅ CORRECT - Use normalized value
conn.send_command("set_eq8_band", {"track_index": 0, "band_index": 1, "freq": 0.299})
```

## Conversion Functions

```python
from server import hz_to_normalized, db_to_normalized

freq_norm = hz_to_normalized(180)   # -> 0.299
gain_norm = db_to_normalized(-3)    # -> 0.4
```

## Frequency Reference

| Hz | Normalized | Use |
|:---|:---|:---|
| 40 | 0.180 | Sub bass cut |
| 80 | 0.240 | Kick/bass body |
| 180 | 0.299 | Vocal high-pass |
| 300 | 0.359 | Mud cut |
| 1000 | 0.597 | Mid reference |
| 3000 | 0.756 | Presence |
| 10000 | 0.899 | Air |

## Gain Reference

| dB | Normalized |
|:---|:---|
| -6 | 0.3 |
| -3 | 0.4 |
| 0 | 0.5 |
| +3 | 0.6 |
| +6 | 0.7 |

## Filter Types

| Value | Type |
|:---|:---|
| 0 | Low Cut 12dB/oct |
| 1 | Low Cut 48dB/oct |
| 2 | Low Shelf |
| 3 | Bell (parametric) |
| 4 | High Shelf |
| 5 | Notch |
| 6 | High Cut 12dB/oct |
| 7 | High Cut 48dB/oct |

## Examples

### High-Pass at 180 Hz
```python
conn.send_command("set_eq8_band", {
    "track_index": 0,
    "band_index": 1,
    "enabled": True,
    "freq": 0.299,
    "filter_type": 0
})
```

### Bell Boost at 3 kHz (+3 dB)
```python
conn.send_command("set_eq8_band", {
    "track_index": 0,
    "band_index": 3,
    "enabled": True,
    "freq": 0.756,
    "gain": 0.6,
    "q": 0.5,
    "filter_type": 3
})
```

## Instrument Presets

### Kick
- Band 1: HP 40Hz → `freq=0.180, filter_type=0`
- Band 2: Boost 60Hz → `freq=0.210, gain=0.60, filter_type=3`

### Vocals
- Band 1: HP 180Hz → `freq=0.299, filter_type=1`
- Band 3: Presence 3k → `freq=0.756, gain=0.57, filter_type=3`
- Band 8: Air 10k → `freq=0.899, gain=0.55, filter_type=4`

## EQ Three

A DJ-style 3-band isolator EQ. Each band can be completely cut (`-inf`) or boosted (`+6dB`).

- **FreqLo / FreqHi**: Define the crossover frequencies.
- **24/48 dB Switch**: Higher = sharper cut, more CPU, more coloring.

> [!NOTE]
> EQ Three's 48dB mode intentionally colors the sound, even when all gains are at 0dB. For transparency, use EQ Eight.

```python
conn.send_command("set_device_parameter", {
    "track_index": 0, "device_index": 0, "parameter_name": "GainLo", "value": 0.0 # -inf
})
```

## Channel EQ

A simple, adaptive 3-band EQ inspired by classic mixing desks.

- **HP 80Hz**: Fixed high-pass toggle to remove rumble.
- **Low (100Hz Shelf)**: Adaptive curve; more boost → wider curve.
- **Mid (Sweepable Peak)**: 120Hz - 7.5kHz range. +/- 12dB.
- **High (Shelf + Low-Pass)**: When cutting, also lowers the LPF cutoff (to 8kHz at -15dB).

> [!TIP]
> Place a **Saturator** after Channel EQ to simulate analog desk non-linearities (boosted low end = more distortion).
