# Live.WavetableDevice Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: EffectMode

---

## Class: FilterRouting

---

## Class: ModulationSource

---

## Class: UnisonMode

---

## Class: VoiceCount

---

## Class: Voicing

---

## Class: WavetableDevice

*This class represents a Wavetable device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `filter_routing` | unknown | Return the current filter routing.... | R |
| `is_active` | bool | Return const access to whether this device is active. This will be false bothwhen the device is off ... | R |
| `mono_poly` | unknown | Return the current voicing mode.... | R |
| `name` | str | Return access to the name of the device.... | R |
| `oscillator_1_effect_mode` | unknown | Return the current effect mode of the oscillator 1.... | R |
| `oscillator_1_wavetable_category` | unknown | Return the current wavetable category of the oscillator 1.... | R |
| `oscillator_1_wavetable_index` | unknown | Return the current wavetable index of the oscillator 1.... | R |
| `oscillator_1_wavetables` | unknown | Get a vector of oscillator 1's wavetable names.... | R |
| `oscillator_2_effect_mode` | unknown | Return the current effect mode of the oscillator 2.... | R |
| `oscillator_2_wavetable_category` | unknown | Return the current wavetable category of the oscillator 2.... | R |
| `oscillator_2_wavetable_index` | unknown | Return the current wavetable index of the oscillator 2.... | R |
| `oscillator_2_wavetables` | unknown | Get a vector of oscillator 2's wavetable names.... | R |
| `oscillator_wavetable_categories` | unknown | Get a vector of the available wavetable categories.... | R |
| `parameters` | list | Const access to the list of available automatable parameters for this device.... | R |
| `poly_voices` | unknown | Return the current number of polyphonic voices. Uses the VoiceCount enumeration.... | R |
| `type` | unknown | Return the type of the device.... | R |
| `unison_mode` | unknown | Return the current unison mode.... | R |
| `unison_voice_count` | unknown | Return the current number of unison voices.... | R |
| `view` | unknown | Representing the view aspects of a device.... | R |
| `visible_modulation_target_names` | str | Get the names of all the visible modulation targets.... | R |

### Methods

#### `add_parameter_to_modulation_matrix()`

Add a non-pitch parameter to the modulation matrix. 

**Arguments:**

- `parameter`: `DeviceParameter`

**Returns:** `int`

#### `get_modulation_target_parameter_name()`

Get the parameter name of the modulation target at the given index. 

**Arguments:**

- `target_index`: `int`

**Returns:** `unicode`

#### `get_modulation_value()`

Get the value of a modulation amount for the given target-source connection. 

**Arguments:**

- `target_index`: `int`
- `source`: `int`

**Returns:** `float`

#### `is_parameter_modulatable()`

Indicate whether the parameter is modulatable. Note that pitch parameters only exist in python and must be handled there. 

**Arguments:**

- `parameter`: `DeviceParameter`

**Returns:** `bool`

#### `set_modulation_value()`

Set the value of a modulation amount for the given target-source connection. 

**Arguments:**

- `target_index`: `int`
- `source`: `int`
- `value`: `float`

**Returns:** `None`

#### `store_chosen_bank()`

Set the selected bank in the device for persistency. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`

**Returns:** `None`

### Sub-Class: WavetableDevice.View

**Properties:**
- `canonical_parent`
- `is_collapsed`

---
