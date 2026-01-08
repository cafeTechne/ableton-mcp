# Live.Eq8Device Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: EditMode

---

## Class: Eq8Device

*This class represents an Eq8 device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `edit_mode` | list | Access to Eq8's edit mode.... | R |
| `global_mode` | list | Access to Eq8's global mode.... | R |
| `is_active` | bool | Return const access to whether this device is active. This will be false bothwhen the device is off ... | R |
| `name` | str | Return access to the name of the device.... | R |
| `oversample` | list | Access to Eq8's oversample value.... | R |
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

### Sub-Class: Eq8Device.View

**Properties:**
- `canonical_parent`
- `is_collapsed`
- `selected_band`

---

## Class: GlobalMode

---
