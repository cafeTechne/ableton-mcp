---
description: How to create and manage parallel chains, zones, and macros in Racks
---

# Rack Management

Racks allow for parallel processing, complex multi-instrument setups, and simplified macro control.

## Creating Racks

Group existing devices or create an empty container.

```python
# Group specific devices into a Rack
conn.send_command("group_devices", {
    "track_index": 0,
    "device_indices": [0, 1]
})

# Create an empty Rack (e.g., Audio Effect Rack)
conn.send_command("search_and_load_device", {
    "track_index": 0,
    "query": "Audio Effect Rack",
    "category": "audio_effects"
})
```

## Parallel Signal Flow

- **Parallel Processing**: Each chain in a Rack receives the same input.
- **Mixer**: Chains have independent volume, pan, and solo controls.

```python
# Create a new parallel chain in a Rack
conn.send_command("create_rack_chain", {
    "track_index": 0,
    "device_index": 0 # The Rack index
})

# Rename a chain
conn.send_command("set_chain_name", {
    "track_index": 0,
    "device_index": 0,
    "chain_index": 1,
    "name": "Sub Layer"
})
```

## Zones (MIDI Filtering)

Zones determine which signals (MIDI or Select) trigger a chain.

- **Key Zones**: Split instruments across the keyboard.
- **Velocity Zones**: Layer sounds based on play strength.
- **Chain Select Zones**: Toggle between "presets" using a single MIDI parameter.

```python
# Set Chain Select Zone (0-127)
conn.send_command("set_chain_zone", {
    "track_index": 0,
    "device_index": 0,
    "chain_index": 1,
    "range_start": 0,
    "range_end": 10
})

# Move the Chain Selector
conn.send_command("set_rack_chain_selector", {
    "track_index": 0,
    "device_index": 0,
    "value": 5
})
```

## Macro Controls

Macros map one knob to multiple internal parameters.

- **Mapping**: Assign internal device parameters to 1 of 16 macros.
- **Randomization**: Use `conn.send_command("randomize_macros", {"track_index": 0, "device_index": 0})` for inspiration.
- **Variations**: Store "Snapshots" of macro states.

```python
# Store a Macro Variation
conn.send_command("store_macro_variation", {
    "track_index": 0,
    "device_index": 0
})

# Recall a Variation by index
conn.send_command("recall_macro_variation", {
    "track_index": 0,
    "device_index": 0,
    "variation_index": 2
})
```

> [!TIP]
> Use **Macro Variations** to create instant "builds" or "drops" by recalling different snapshots.
