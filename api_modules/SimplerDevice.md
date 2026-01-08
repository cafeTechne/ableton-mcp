# Live.SimplerDevice Module Reference

Auto-generated from Live 11 API documentation.

---

## Module-Level Functions

### `get_available_voice_numbers()`

**Description:** Get a vector of valid Simpler voice numbers. 

**Returns:** `IntVector`

---

## Class: PlaybackMode

---

## Class: SimplerDevice

*This class represents a Simpler device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `can_have_chains` | bool | Returns true if the device is a rack.... | R |
| `can_have_drum_pads` | bool | Returns true if the device is a drum rack.... | R |
| `can_warp_as` | bool | Returns true if warp_as is available.... | R |
| `can_warp_double` | bool | Returns true if warp_double is available.... | R |
| `can_warp_half` | bool | Returns true if warp_half is available.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the Device.... | R |
| `class_display_name` | str | Return const access to the name of the device’s class name as displayed in Live’s browser and device... | R |
| `class_name` | str | Return const access to the name of the device’s class.... | R |
| `is_active` | bool | Return const access to whether this device is active. This will be false bothwhen the device is off ... | R |
| `multi_sample_mode` | unknown | Returns whether Simpler is in mulit-sample mode.... | R |
| `name` | str | Return access to the name of the device.... | R |
| `pad_slicing` | bool | When set to true, slices can be added in slicing mode by playing notes .that are not assigned to sli... | R |
| `parameters` | list | Const access to the list of available automatable parameters for this device.... | R |
| `playback_mode` | list | Access to Simpler’s playback mode.... | R |
| `playing_position` | list | Constant access to the current playing position in the sample.The returned value is the normalized p... | R |
| `playing_position_enabled` | bool | Returns whether Simpler is showing the playing position.The returned value is True while the sample ... | R |
| `retrigger` | list | Access to Simpler’s retrigger mode.... | R |
| `sample` | unknown | Get the loaded Sample.... | R |
| `slicing_playback_mode` | list | Access to Simpler’s slicing playback mode.... | R |
| `type` | unknown | Return the type of the device.... | R |
| `view` | unknown | Representing the view aspects of a device.... | R |
| `voices` | list | Access to the number of voices in Simpler.... | R |

### Methods

#### `crop()`

Crop the loaded sample to the active area between start- and end marker. Calling this method on an empty simpler raises an error. 

**Returns:** `None`

#### `guess_playback_length()`

Return an estimated beat time for the playback length between start- and end-marker. Calling this method on an empty simpler raises an error. 

**Returns:** `float`

#### `reverse()`

Reverse the loaded sample. Calling this method on an empty simpler raises an error. 

**Returns:** `None`

#### `store_chosen_bank()`

Set the selected bank in the device for persistency. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`

**Returns:** `None`

#### `warp_as()`

Warp the playback region between start- and end-marker as the given length. Calling this method on an empty simpler raises an error. 

**Arguments:**

- `beat_time`: `float`

**Returns:** `None`

#### `warp_double()`

Doubles the tempo for region between start- and end-marker. 

**Returns:** `None`

#### `warp_half()`

Halves the tempo for region between start- and end-marker. 

**Returns:** `None`

### Sub-Class: SimplerDevice.View

**Properties:**
- `canonical_parent`
- `is_collapsed`
- `sample_end`
- `sample_env_fade_in`
- `sample_env_fade_out`
- `sample_loop_end`
- `sample_loop_fade`
- `sample_loop_start`
- `sample_start`
- `selected_slice`

---

## Class: SlicingPlaybackMode

---
