# Live.PluginDevice Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: PluginDevice

*This class represents a plugin device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `is_active` | bool | Return const access to whether this device is active. This will be false bothwhen the device is off ... | R |
| `name` | str | Return access to the name of the device.... | R |
| `parameters` | list | Const access to the list of available automatable parameters for this device.... | R |
| `presets` | list | Get the list of presets the plugin offers.... | R |
| `selected_preset_index` | list | Access to the index of the currently selected preset.... | R |
| `type` | unknown | Return the type of the device.... | R |
| `view` | unknown | Representing the view aspects of a device.... | R |

### Methods

#### `get_parameter_names()`

Get the range of plugin parameter names, bound by begin and end. If end is smaller than 0 it is interpreted as the parameter count.  

**Arguments:**

- `begin`: `int` *(default: 0 [)*
- `end`: `int` *(default: -1]])*

**Returns:** `StringVector`

#### `store_chosen_bank()`

Set the selected bank in the device for persistency. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`

**Returns:** `None`

### Sub-Class: PluginDevice.View

**Properties:**
- `canonical_parent`
- `is_collapsed`

---
