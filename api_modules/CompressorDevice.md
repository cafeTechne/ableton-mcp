# Live.CompressorDevice Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: CompressorDevice

*This class represents a Compressor device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `available_input_routing_channels` | list | Return a list of source channels for input routing in the sidechain.... | R |
| `available_input_routing_types` | list | Return a list of source types for input routing in the sidechain.... | R |
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `input_routing_channel` | unknown | Get and set the current source channel for input routing in the sidechain.Raises ValueError if the c... | R |
| `input_routing_type` | unknown | Get and set the current source type for input routing in the sidechain.Raises ValueError if the type... | R |
| `is_active` | bool | Return const access to whether this device is active. This will be false bothwhen the device is off ... | R |
| `name` | str | Return access to the name of the device.... | R |
| `parameters` | list | Const access to the list of available automatable parameters for this device.... | R |
| `type` | unknown | Return the type of the device.... | R |
| `view` | unknown | Representing the view aspects of a device.... | R |

### Methods

#### `store_chosen_bank()`

Set the selected bank in the device for persistency. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`

**Returns:** `None`

### Sub-Class: CompressorDevice.View

**Properties:**
- `canonical_parent`
- `is_collapsed`

---
