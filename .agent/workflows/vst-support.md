---
description: How to use VST/AU plugins like Serum, Vital, Surge XT
---

# VST/AU Plugin Support

You can load third-party plugins using the standard device loading tools.

## Loading a Plugin

Plugins are loaded by name, just like native devices.

```python
from mcp_tooling.devices import search_and_load_device
import time

# Load Serum (VST3)
search_and_load_device(track_index=0, query="Serum", category="plug-ins")

# Load Vital
search_and_load_device(track_index=1, query="Vital", category="plug-ins")

# Load Surge XT
search_and_load_device(track_index=2, query="Surge XT", category="plug-ins")

# Wait for the heavy GUI to load!
time.sleep(2.0)
```

## Best Practice: Use Instrument Racks (.adg)

Directly loading a VST loads the *default* preset. To load a specific sound:

1.  Open the VST in Ableton.
2.  Select your patch (e.g., "Bass - Wobble").
3.  Group the device (Ctrl+G / Cmd+G) into an Instrument Rack.
4.  Map important parameters (Cutoff, Res) to Macros.
5.  Save the Rack to your User Library with a searchable name (e.g., "Vital Wobble Bass").

Now you can load it easily:

```python
search_and_load_device(track_index=0, query="Vital Wobble Bass", category="sounds")
```

## Automating VST Parameters

VST parameters are only visible to Ableton (and MCP) if they are "published" in the device panel.

### Configuration Mode
If a parameter is not visible in the `get_device_info` response:
1.  Open the VST window.
2.  Press the **Configure** button in the device header.
3.  Click/adjust the parameter in the VST GUI. It will appear in Ableton's panel.
4.  Once added, it is permanently available for automation/modulation.

```python
# Create automation for a configured parameter
conn.send_command("apply_automation", {
    "track_index": 0,
    "clip_index": 0,
    "parameter_name": "Filter Cutoff", 
    "start_val": 0.0,
    "end_val": 1.0,
    "duration_bars": 4
})
```

## Sidechaining for VST/AU

Plug-ins that support external triggers (e.g., sidechain compressors, vocoders) have a routing panel on the left of the device.

```python
# Set Sidechain Source for a VST
conn.send_command("set_plug_in_sidechain", {
    "track_index": 1, # Bass
    "device_index": 0, # VST Compressor
    "source_track_index": 0, # Kick
    "gain": 1.0,
    "mix": 1.0
})
```

## Platform Differences

- **VST2 (.vst)**: Uses Banks/Presets (.fxb/.fxp). Presets "belong" to the specific instance.
- **VST3 (.vst3)**: Newer format, often better CPU management.
- **Audio Units (.au)**: macOS only. Presets are shared across the system via the `User Library/Presets` folder.

## Troubleshooting

-   **"Device not found"**: Ensure the plugin is scanned and visible in Ableton's "Plug-ins" browser category.
-   **Wrong version**: Live might distinguish "Servo VST" vs "Servo AU". Be specific in your query.
