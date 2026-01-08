# Live.Sample Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: Sample

*This class represents a sample file loaded into a Simpler instance.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `beats_granulation_resolution` | list | Access to the Granulation Resolution parameter in Beats Warp Mode.... | R |
| `beats_transient_envelope` | list | Access to the Transient Envelope parameter in Beats Warp Mode.... | R |
| `beats_transient_loop_mode` | list | Access to the Transient Loop Mode parameter in Beats Warp Mode.... | R |
| `canonical_parent` | list | Access to the sample’s canonical parent.... | R |
| `complex_pro_envelope` | list | Access to the Envelope parameter in Complex Pro Mode.... | R |
| `complex_pro_formants` | list | Access to the Formants parameter in Complex Pro Warp Mode.... | R |
| `end_marker` | list | Access to the position of the sample’s end marker.... | R |
| `file_path` | unknown | Get the path of the sample file.... | R |
| `gain` | list | Access to the sample gain.... | R |
| `length` | unknown | Get the length of the sample file in sample frames.... | R |
| `sample_rate` | list | Access to the audio sample rate of the sample.... | R |
| `slices` | int | Access to the list of slice points in sample time in the sample.... | R |
| `slicing_beat_division` | list | Access to sample’s slicing step size.... | R |
| `slicing_region_count` | list | Access to sample’s slicing split count.... | R |
| `slicing_sensitivity` | list | Access to sample’s slicing sensitivity whose sensitivity is in between 0.0 and 1.0.The higher the se... | R |
| `slicing_style` | list | Access to sample’s slicing style.... | R |
| `start_marker` | list | Access to the position of the sample’s start marker.... | R |
| `texture_flux` | list | Access to the Flux parameter in Texture Warp Mode.... | R |
| `texture_grain_size` | list | Access to the Grain Size parameter in Texture Warp Mode.... | R |
| `tones_grain_size` | list | Access to the Grain Size parameter in Tones Warp Mode.... | R |
| `warp_markers` | unknown | Get the warp markers for this sample.... | R |
| `warp_mode` | list | Access to the sample’s warp mode.... | R |
| `warping` | list | Access to the sample’s warping property.... | R |

### Methods

#### `beat_to_sample_time()`

Converts the given beat time to sample time. Raises an error if the sample is not warped. 

**Arguments:**

- `beat_time`: `float`

**Returns:** `float`

#### `clear_slices()`

Clears all slices created in Simpler’s manual mode. 

**Returns:** `None`

#### `gain_display_string()`

Get the gain’s display value as a string. 

**Returns:** `unicode`

#### `insert_slice()`

Add a slice point at the provided time if there is none. 

**Arguments:**

- `slice_time`: `int`

**Returns:** `None`

#### `move_slice()`

Move the slice point at the provided time. 

**Arguments:**

- `old_time`: `int`
- `new_time`: `int`

**Returns:** `int`

#### `remove_slice()`

Remove the slice point at the provided time if there is one. 

**Arguments:**

- `slice_time`: `int`

**Returns:** `None`

#### `reset_slices()`

Resets all edited slices to their original positions. 

**Returns:** `None`

#### `sample_to_beat_time()`

Converts the given sample time to beat time. Raises an error if the sample is not warped. 

**Arguments:**

- `sample_time`: `float`

**Returns:** `float`

---

## Class: SlicingBeatDivision

---

## Class: SlicingStyle

---

## Class: TransientLoopMode

---
