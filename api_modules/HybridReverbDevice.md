# Live.HybridReverbDevice Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: HybridReverbDevice

*This class represents a Hybrid Reverb device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `ir_attack_time` | unknown | Return the current IrAttackTime... | R |
| `ir_category_index` | unknown | Return the current IR category index... | R |
| `ir_category_list` | list | Return the current IR categories list... | R |
| `ir_decay_time` | unknown | Return the current IrDecayTime... | R |
| `ir_file_index` | unknown | Return the current IR file index... | R |
| `ir_file_list` | list | Return the current IR file list... | R |
| `ir_size_factor` | unknown | Return the current IrSizeFactor... | R |
| `ir_time_shaping_on` | unknown | Return the current IrTimeShapingOn... | R |
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

### Sub-Class: HybridReverbDevice.View

**Properties:**
- `canonical_parent`
- `is_collapsed`

---
