# Live.Conversions Module Reference

Auto-generated from Live 11 API documentation.

---

## Module-Level Functions

### `audio_to_midi_clip()`

**Description:** Creates a MIDI clip in a new MIDI track with the notes extracted from the given audio_clip. The `audio_to_midi_type` decides which algorithm is used in the process. Raises error when called with an inconvertible clip or invalid `audio_to_midi_type`. 

**Arguments:**
- `song` (Song)
- `audio_clip` (Clip)
- `audio_to_midi_type` (int)

**Returns:** `None`

---

### `create_drum_rack_from_audio_clip()`

**Description:** Creates a new track with a drum rack with a simpler on the first pad with the specified audio clip. 

**Arguments:**
- `song` (Song)
- `audio_clip` (Clip)

**Returns:** `None`

---

### `create_midi_track_from_drum_pad()`

**Description:** Creates a new Midi track containing the specified Drum Pad’s device chain. 

**Arguments:**
- `song` (Song)
- `drum_pad` (DrumPad)

**Returns:** `None`

---

### `create_midi_track_with_simpler()`

**Description:** Creates a new Midi track with a simpler including the specified audio clip. 

**Arguments:**
- `song` (Song)
- `audio_clip` (Clip)

**Returns:** `None`

---

### `is_convertible_to_midi()`

**Description:** Returns whether `audio_clip` can be converted to MIDI. Raises error when called with a MIDI clip 

**Arguments:**
- `song` (Song)
- `audio_clip` (Clip)

**Returns:** `bool`

---

### `move_devices_on_track_to_new_drum_rack_pad()`

**Description:** Moves the entire device chain of the track according to the track index onto the C1 (note 36) drum pad of a new drum rack in a new track.If the track associated with the track index does not contain any devices nothing changes (i.e. a new track and new drum rack are not created). 

**Arguments:**
- `song` (Song)
- `track_index` (int)

**Returns:** `LomObject`

---

### `sliced_simpler_to_drum_rack()`

**Description:** Converts the Simpler into a Drum Rack, assigning each slice to a drum pad. Calling it on a non-sliced simpler raises an error. 

**Arguments:**
- `song` (Song)
- `simpler` (SimplerDevice)

**Returns:** `None`

---

## Class: AudioToMidiType

---
