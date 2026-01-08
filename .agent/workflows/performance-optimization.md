---
description: How to optimize CPU usage, delay compensation, and monitoring latency
---

# Performance & System Optimization

Maintain a responsive session by managing CPU load and timing delays.

## CPU Management

- **Activator Switches**: Turn off devices that aren't currently needed. This stops their CPU consumption while preserving their settings.
- **Freeze Track**: Use `conn.send_command("freeze_track", {"track_index": 0})` to render a CPU-heavy track to audio while keeping its MIDI/devices available for unfreezing.
- **Track Muting**: Muting a track with the Track Activator (`conn.send_command("set_track_mute", {"track_index": 0, "mute": True})`) also reduces its CPU footprint if it contains heavy plug-ins.

## Device Delay Compensation

Live automatically keeps all tracks in sync by compensating for the processing time of devices.

```python
# Toggle global delay compensation
conn.send_command("set_delay_compensation", {"enabled": True})
```

### Reduced Latency When Monitoring
When recording live instruments, you may want to prioritize "feel" over perfect track sync.

```python
# Enable lowest possible latency for input-monitored tracks
conn.send_command("set_reduced_latency_monitoring", {"enabled": True})
```

- **ON**: Lowest latency for recording, but monitored tracks may be out of sync with return tracks.
- **OFF**: All tracks in perfect sync, but higher latency for the performer (Default).

## Hardware & Plug-in Latency

- **System Folders**: Live scans `/Library/Audio/Plug-Ins/VST` (Mac) or the registry-defined folder (Win).
- **Custom Folders**: Use `conn.send_command("set_vst_custom_folder", {"path": "C:/CustomPlugins"})` if your plugins are outside the standard path.
- **Manual Offsets**: For hardware synths, use the **External Instrument**'s `hardware_latency` slider to nudge the timing in milliseconds or samples.
