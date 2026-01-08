# Live.RackDevice Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: RackDevice

*This class represents a Rack device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `can_show_chains` | bool | return True, if this Rack contains a rack instrument device that is capable of showing its chains in... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `chains` | list | Return const access to the list of chains in this device. Throws an exception if can_have_chains is ... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `drum_pads` | list | Return const access to the list of drum pads in this device. Throws an exception if can_have_drum_pa... | R |
| `has_drum_pads` | bool | Returns true if the device is a drum rack which has drum pads. Throws an exception if can_have_drum_... | R |
| `has_macro_mappings` | bool | Returns true if any of the rack’s macros are mapped to a parameter.... | R |
| `is_active` | bool | Return const access to whether this device is active. This will be false bothwhen the device is off ... | R |
| `is_showing_chains` | bool | Returns True, if it is showing chains.... | R |
| `macros_mapped` | bool | A list of booleans, one for each macro parameter, which is True iffthat macro is mapped to something... | R |
| `name` | str | Return access to the name of the device.... | R |
| `parameters` | list | Const access to the list of available automatable parameters for this device.... | R |
| `return_chains` | list | Return const access to the list of return chains in this device. Throws an exception if can_have_cha... | R |
| `selected_variation_index` | list | Access to the index of the currently selected macro variation.Throws an exception if the index is ou... | R |
| `type` | unknown | Return the type of the device.... | R |
| `variation_count` | list | Access to the number of macro variations currently stored.... | R |
| `view` | unknown | Representing the view aspects of a device.... | R |
| `visible_drum_pads` | list | Return const access to the list of visible drum pads in this device. Throws an exception if can_have... | R |

### Methods

#### `add_macro()`

Increases the number of visible macro controls in the rack. Throws an exception if the maximum number of macro controls is reached. 

**Returns:** `None`

#### `copy_pad()`

Copies all contents of a drum pad from a source pad into a destination pad. copy_pad(source_index, destination_index) where source_index and destination_index correspond to the note number/index of the drum pad in a drum rack. Throws an exception when the source pad is empty, or when the source or destination indices are not between 0 - 127. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`

**Returns:** `None`

#### `delete_selected_variation()`

Deletes the currently selected macro variation.Does nothing if there is no selected variation. 

**Returns:** `None`

#### `randomize_macros()`

Randomizes the values for all macro controls not excluded from randomization. 

**Returns:** `None`

#### `recall_last_used_variation()`

Recalls the macro variation that was recalled most recently.Does nothing if no variation has been recalled yet. 

**Returns:** `None`

#### `recall_selected_variation()`

Recalls the currently selected macro variation.Does nothing if there are no variations. 

**Returns:** `None`

#### `remove_macro()`

Decreases the number of visible macro controls in the rack. Throws an exception if the minimum number of macro controls is reached. 

**Returns:** `None`

#### `store_chosen_bank()`

Set the selected bank in the device for persistency. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`

**Returns:** `None`

#### `store_variation()`

Stores a new variation of the values of all currently mapped macros 

**Returns:** `None`

### Sub-Class: RackDevice.View

**Properties:**
- `canonical_parent`
- `drum_pads_scroll_position`
- `is_collapsed`
- `is_showing_chain_devices`
- `selected_chain`
- `selected_drum_pad`

---
