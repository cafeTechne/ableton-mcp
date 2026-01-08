# Live.TransmuteDevice Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: TransmuteDevice

*This class represents a Transmute device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `frequency_dial_mode_index` | unknown | Return the current frequency dial mode index... | R |
| `frequency_dial_mode_list` | list | Return the current frequency dial mode list... | R |
| `is_active` | bool | Return const access to whether this device is active. This will be false bothwhen the device is off ... | R |
| `midi_gate_index` | unknown | Return the current midi gate index... | R |
| `midi_gate_list` | list | Return the current midi gate list... | R |
| `mod_mode_index` | unknown | Return the current mod mode index... | R |
| `mod_mode_list` | list | Return the current mod mode list... | R |
| `mono_poly_index` | unknown | Return the current mono poly mode index... | R |
| `mono_poly_list` | list | Return the current mono poly mode list... | R |
| `name` | str | Return access to the name of the device.... | R |
| `parameters` | list | Const access to the list of available automatable parameters for this device.... | R |
| `pitch_bend_range` | unknown | Return the current pitch bend range... | R |
| `pitch_mode_index` | unknown | Return the current pitch mode index... | R |
| `pitch_mode_list` | list | Return the current pitch mode list... | R |
| `polyphony` | unknown | Return the current polyphony... | R |
| `type` | unknown | Return the type of the device.... | R |
| `view` | unknown | Representing the view aspects of a device.... | R |

### Methods

#### `store_chosen_bank()`

Set the selected bank in the device for persistency. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`

**Returns:** `None`

### Sub-Class: TransmuteDevice.View

**Properties:**
- `canonical_parent`
- `is_collapsed`

---
