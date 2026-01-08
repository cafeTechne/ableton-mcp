# Live.Clip Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: AutomationEnvelope

*Describes parameter automation per clip.*

### Methods

#### `insert_step()`

**Arguments:**

- `arg2`: `float`
- `arg3`: `float`
- `arg4`: `float`

**Returns:** `None`

#### `value_at_time()`

**Arguments:**

- `arg2`: `float`

**Returns:** `float`

---

## Class: Clip

*This class represents a Clip in Live. It can be either an AudioClip or a MIDI Clip, in an Arrangement or the Session, dependingon the Track (Slot) it lives in.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `available_warp_modes` | unknown | Available for AudioClips only.Get/Set the available warp modes, that can be used.... | R/W |
| `canonical_parent` | unknown | Get the canonical parent of the Clip.... | R |
| `color` | list | Get/set access to the color of the Clip (RGB).... | R |
| `color_index` | list | Get/set access to the color index of the Clip.... | R |
| `end_marker` | unknown | Get/Set the Clips end marker pos in beats/seconds (unit depends on warping).... | R/W |
| `end_time` | unknown | Get the clip’s end time.... | R |
| `file_path` | unknown | Get the path of the file represented by the Audio Clip.... | R |
| `gain` | list | Available for AudioClips only.Read/write access to the gain setting of theAudio Clip... | R/W |
| `gain_display_string` | str | Return a string with the gain as dB value... | R |
| `groove` | unknown | Get the groove associated with this clip.... | R |
| `has_envelopes` | unknown | Will notify if the clip gets his first envelope or the last envelope is removed.... | R |
| `has_groove` | bool | Returns true if a groove is associated with this clip.... | R |
| `is_arrangement_clip` | bool | return true if this Clip is an Arrangement Clip.A Clip can be either a Session or Arrangement Clip.... | R |
| `is_audio_clip` | bool | Return true if this Clip is an Audio Clip.A Clip can be either an Audioclip or a MIDI Clip.... | R |
| `is_midi_clip` | bool | return true if this Clip is a MIDI Clip.A Clip can be either an Audioclip or a MIDI Clip.... | R |
| `is_overdubbing` | bool | returns true if the Clip is recording overdubs... | R |
| `is_playing` | unknown | Get/Set if this Clip is currently playing. If the Clips trigger modeis set to a quantization value, ... | R/W |
| `is_recording` | bool | returns true if the Clip was triggered to record or is recording.... | R |
| `is_triggered` | bool | returns true if the Clip was triggered or is playing.... | R |
| `launch_mode` | list | Get/Set access to the launch mode setting of the Clip.... | R/W |
| `launch_quantization` | list | Get/Set access to the launch quantization setting of the Clip.... | R/W |
| `legato` | list | Get/Set access to the legato setting of the Clip... | R/W |
| `length` | unknown | Get to the Clips length in beats/seconds (unit depends on warping).... | R |
| `loop_end` | unknown | Get/Set the loop end pos of this Clip in beats/seconds (unit depends on warping).... | R/W |
| `loop_start` | unknown | Get/Set the Clips loopstart pos in beats/seconds (unit depends on warping).... | R/W |
| `looping` | unknown | Get/Set the Clips ‘loop is enabled’ flag.Only Warped Audio Clips or MIDI Clip can be looped.... | R/W |
| `muted` | list | Read/write access to the mute state of the Clip.... | R/W |
| `name` | str | Read/write access to the name of the Clip.... | R/W |
| `pitch_coarse` | list | Available for AudioClips only.Read/write access to the pitch (in halftones) setting of theAudio Clip... | R/W |
| `pitch_fine` | list | Available for AudioClips only.Read/write access to the pitch fine setting of theAudio Clip, ranging ... | R/W |
| `playing_position` | list | Constant access to the current playing position of the clip.The returned value is the position in be... | R |
| `position` | unknown | Get/Set the loop position of this Clip in beats/seconds (unit depends on warping).... | R/W |
| `ram_mode` | list | Available for AudioClips only.Read/write access to the Ram mode setting of the Audio Clip... | R/W |
| `sample_length` | unknown | Available for AudioClips only.Get the sample length in sample time or -1 if there is no sample avail... | R |
| `signature_denominator` | list | Get/Set access to the global signature denominator of the Clip.... | R/W |
| `signature_numerator` | list | Get/Set access to the global signature numerator of the Clip.... | R/W |
| `start_marker` | unknown | Get/Set the Clips start marker pos in beats/seconds (unit depends on warping).... | R/W |
| `start_time` | unknown | Get the clip’s start time offset. For Session View clips, this is the time the clip was started. For... | R |
| `velocity_amount` | list | Get/Set access to the velocity to volume amount of the Clip.... | R/W |
| `view` | unknown | Get the view of the Clip.... | R |
| `warp_markers` | unknown | Available for AudioClips only.Get the warp markers for this audio clip.... | R |
| `warp_mode` | unknown | Available for AudioClips only.Get/Set the warp mode for this audio clip.... | R/W |
| `warping` | unknown | Available for AudioClips only.Get/Set if this Clip is timestreched.... | R/W |
| `will_record_on_start` | bool | returns true if the Clip will record on being started.... | R |

### Methods

#### `add_new_notes()`

Expects a Python iterable holding a number of Live.Clip.MidiNoteSpecification objects. The objects will be used to construct new notes in the clip. 

**Arguments:**

- `arg2`: `object`

**Returns:** `None`

#### `apply_note_modifications()`

Expects a list of notes as returned from get_notes_extended. The content of the list will be used to modify existing notes in the clip, based on matching note IDs. This function should be used when modifying existing notes, e.g. changing the velocity or start time. The function ensures that per-note events attached to the modified notes are preserved. This is NOT the case when replacing notes via a combination of remove_notes_extended and add_new_notes. The given list can be a subset of the notes in the clip, but it must not contain any notes that are not present in the clip.  

**Arguments:**

- `arg2`: `MidiNoteVector`

**Returns:** `None`

#### `automation_envelope()`

Return the envelope for the given parameter.Returns None if the envelope doesn’t exist.Returns None for Arrangement clips.Returns None for parameters from a different track. 

**Arguments:**

- `arg2`: `DeviceParameter`

**Returns:** `AutomationEnvelope`

#### `beat_to_sample_time()`

Available for AudioClips only. Converts the given beat time to sample time. Raises an error if the sample is not warped. 

**Arguments:**

- `beat_time`: `float`

**Returns:** `float`

#### `clear_all_envelopes()`

Clears all envelopes for this clip. 

**Returns:** `None`

#### `clear_envelope()`

Clears the envelope of this clips given parameter. 

**Arguments:**

- `arg2`: `DeviceParameter`

**Returns:** `None`

#### `create_automation_envelope()`

Creates an envelope for a given parameter and returns it.This should only be used if the envelope doesn’t exist.Raises an error if the envelope can’t be created. 

**Arguments:**

- `arg2`: `DeviceParameter`

**Returns:** `AutomationEnvelope`

#### `crop()`

Crops the clip. The region that is cropped depends on whether the clip is looped or not. If looped, the region outside of the loop is removed. If not looped, the region outside the start and end markers is removed. 

**Returns:** `None`

#### `deselect_all_notes()`

De-selects all notes present in the clip. 

**Returns:** `None`

#### `duplicate_loop()`

Make the loop two times longer and duplicates notes and envelopes. Duplicates the clip start/end range if the clip is not looped. 

**Returns:** `None`

#### `duplicate_region()`

Duplicate the notes in the specified region to the destination_time. Only notes of the specified pitch are duplicated or all if pitch is -1. If the transposition_amount is not 0, the notes in the region will be transposed by the transpose_amount of semitones.Raises an error on audio clips. 

**Arguments:**

- `region_start`: `float`
- `region_length`: `float`
- `destination_time`: `float`
- `pitch`: `int` *(default: -1 [)*
- `transposition_amount`: `int` *(default: 0]])*

**Returns:** `None`

#### `fire()`

(Re)Start playing this Clip. 

**Returns:** `None`

#### `get_notes()`

Returns a tuple of tuples where each inner tuple represents a note starting in the given pitch- and time range. The inner tuple contains pitch, time, duration, velocity, and mute state. 

**Arguments:**

- `from_time`: `float`
- `from_pitch`: `int`
- `time_span`: `float`
- `pitch_span`: `int`

**Returns:** `tuple`

#### `get_notes_by_id()`

Return a list of MIDI notes matching the given note IDs.  

**Arguments:**

- `arg2`: `object`

**Returns:** `MidiNoteVector`

#### `get_notes_extended()`

Returns a list of MIDI notes from the given pitch and time range. Each note is represented by a Live.Clip.MidiNote object. The returned list can be modified freely, but modifications will not be reflected in the MIDI clip until apply_note_modifications is called. 

**Arguments:**

- `from_pitch`: `int`
- `pitch_span`: `int`
- `from_time`: `float`
- `time_span`: `float`

**Returns:** `MidiNoteVector`

#### `get_selected_notes()`

Returns a tuple of tuples where each inner tuple represents a selected note. The inner tuple contains pitch, time, duration, velocity, and mute state. 

**Returns:** `tuple`

#### `get_selected_notes_extended()`

Returns a list of all MIDI notes from the clip that are currently selected. Each note is represented by a Live.Clip.MidiNote object. The returned list can be modified freely, but modifications will not be reflected in the MIDI clip until apply_note_modifications is called. 

**Returns:** `MidiNoteVector`

#### `move_playing_pos()`

Jump forward or backward by the specified relative amount in beats. Will do nothing, if the Clip is not playing. 

**Arguments:**

- `arg2`: `float`

**Returns:** `None`

#### `quantize()`

Quantize all notes in a clip or align warp markers. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `float`

**Returns:** `None`

#### `quantize_pitch()`

Quantize all the notes of a given pitch.  Raises an error on audio clips. 

**Arguments:**

- `arg2`: `int`
- `arg3`: `int`
- `arg4`: `float`

**Returns:** `None`

#### `remove_notes()`

Delete all notes starting in the given pitch- and time range. 

**Arguments:**

- `arg2`: `float`
- `arg3`: `int`
- `arg4`: `float`
- `arg5`: `int`

**Returns:** `None`

#### `remove_notes_by_id()`

Delete all notes matching the given note IDs. This function should NOT be used to implement modification of existing notes (i.e. in combination with add_new_notes), as that leads to loss of per-note events. apply_note_modifications must be used instead for modifying existing notes. 

**Arguments:**

- `arg2`: `object`

**Returns:** `None`

#### `remove_notes_extended()`

Delete all notes starting in the given pitch and time range. This function should NOT be used to implement modification of existing notes (i.e. in combination with add_new_notes), as that leads to loss of per-note events. apply_note_modifications must be used instead for modifying existing notes. 

**Arguments:**

- `from_pitch`: `int`
- `pitch_span`: `int`
- `from_time`: `float`
- `time_span`: `float`

**Returns:** `None`

#### `replace_selected_notes()`

Called with a tuple of tuples where each inner tuple represents a note in the same format as returned by get_selected_notes. The notes described that way will then be used to replace the old selection. 

**Arguments:**

- `arg2`: `tuple`

**Returns:** `None`

#### `sample_to_beat_time()`

Available for AudioClips only. Converts the given sample time to beat time. Raises an error if the sample is not warped. 

**Arguments:**

- `sample_time`: `float`

**Returns:** `float`

#### `scrub()`

Scrubs inside a clip. scrub_position defines the position in beats that the scrub will start from. The scrub will continue until stop_scrub is called. Global quantization applies to the scrub’s position and length. 

**Arguments:**

- `scrub_position`: `float`

**Returns:** `None`

#### `seconds_to_sample_time()`

Available for AudioClips only. Converts the given seconds to sample time. Raises an error if the sample is warped. 

**Arguments:**

- `seconds`: `float`

**Returns:** `float`

#### `select_all_notes()`

Selects all notes present in the clip. 

**Returns:** `None`

#### `set_fire_button_state()`

Set the clip’s fire button state directly. Supports all launch modes. 

**Arguments:**

- `arg2`: `bool`

**Returns:** `None`

#### `set_notes()`

Called with a tuple of tuples where each inner tuple represents a note in the same format as returned by get_notes. The notes described that way will then be added to the clip. 

**Arguments:**

- `arg2`: `tuple`

**Returns:** `None`

#### `stop()`

Stop playing this Clip. 

**Returns:** `None`

#### `stop_scrub()`

Stops the current scrub. 

**Returns:** `None`

### Sub-Class: Clip.View

**Properties:**
- `canonical_parent`
- `grid_is_triplet`
- `grid_quantization`

**Methods:**
- `hide_envelope()`
- `select_envelope_parameter()`
- `show_envelope()`
- `show_loop()`

---

## Class: ClipLaunchQuantization

---

## Class: GridQuantization

---

## Class: LaunchMode

---

## Class: MidiNote

*An object representing a MIDI Note*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `duration` | unknown | ... | R |
| `mute` | unknown | ... | R |
| `note_id` | unknown | A numerical ID that’s unique within the originating clip of the note. Not to beused directly, but im... | R |
| `pitch` | unknown | ... | R |
| `probability` | unknown | ... | R |
| `release_velocity` | unknown | ... | R |
| `start_time` | unknown | ... | R |
| `velocity` | unknown | ... | R |
| `velocity_deviation` | unknown | ... | R |

---

## Class: MidiNoteSpecification

*An object specifying the data for creating a MIDI note. To be used with the add_new_notes function.*

---

## Class: WarpMarker

*This class represents a WarpMarker type.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `beat_time` | unknown | A WarpMarker’s beat time.... | R |
| `sample_time` | unknown | A WarpMarker’s sample time.... | R |

---

## Class: WarpMode

---
