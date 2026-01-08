# Live.MaxDevice Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: MaxDevice

*This class represents a Max for Live device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `audio_inputs` | list | Const access to a list of all audio inputs of the device.... | R |
| `audio_outputs` | list | Const access to a list of all audio outputs of the device.... | R |
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `is_active` | bool | Return const access to whether this device is active. This will be false bothwhen the device is off ... | R |
| `midi_inputs` | list | Const access to a list of all midi outputs of the device.... | R |
| `midi_outputs` | list | Const access to a list of all midi outputs of the device.... | R |
| `name` | str | Return access to the name of the device.... | R |
| `parameters` | list | Const access to the list of available automatable parameters for this device.... | R |
| `type` | unknown | Return the type of the device.... | R |
| `view` | unknown | Representing the view aspects of a device.... | R |

### Methods

#### `get_bank_count()`

Get the number of parameter banks. This is related to hardware control surfaces. 

**Returns:** `int`

#### `get_bank_name()`

Get the name of a parameter bank given by index. This is related to hardware control surfaces. 

**Arguments:**

- `arg2`: `int`

**Returns:** `unicode`

#### `get_bank_parameters()`

Get the indices of parameters of the given bank index. Empty slots are marked as -1. Bank index -1 refers to the best-of bank. This function is related to hardware control surfaces. 

**Arguments:**

- `arg2`: `int`

**Returns:** `list`

#### `get_value_item_icons()`

Get a list of icon identifier strings for a list parameter’s values.An empty string is given where no icon should be displayed.An empty list is given when no icons should be displayed.This is related to hardware control surfaces. 

**Arguments:**

- `arg2`: `DeviceParameter`

**Returns:** `list`

#### `store_chosen_bank()`

Set the selected bank in the device for persistency. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`

**Returns:** `None`

### Sub-Class: MaxDevice.View

**Properties:**
- `canonical_parent`
- `is_collapsed`

---
