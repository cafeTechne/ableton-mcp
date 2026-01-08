# Live.ClipSlot Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: ClipSlot

*This class represents an entry in Lives Session view matrix.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `canonical_parent` | unknown | Get the canonical parent of the ClipSlot.... | R |
| `clip` | unknown | Returns the Clip which this clipslots currently owns. Might be None.... | R |
| `color` | unknown | Returns the canonical color for the clip slot or None if it does not exist.... | R |
| `color_index` | unknown | Returns the canonical color index for the clip slot or None if it does not exist.... | R |
| `controls_other_clips` | bool | Returns true if firing this slot will fire clips in other slots.Can only be true for slots in group ... | R |
| `has_clip` | bool | Returns true if this Clipslot owns a Clip.... | R |
| `has_stop_button` | unknown | Get/Set if this Clip has a stop button, which will, if fired, stop anyother Clip that is currently p... | R/W |
| `is_group_slot` | unknown | Returns whether this clip slot is a group track slot (group slot).... | R |
| `is_playing` | unknown | Returns whether the clip associated with the slot is playing.... | R |
| `is_recording` | unknown | Returns whether the clip associated with the slot is recording.... | R |
| `is_triggered` | list | Const access to the triggering state of the clip slot.... | R |
| `playing_status` | list | Const access to the playing state of the clip slot.Can be either stopped, playing, or recording.... | R |
| `will_record_on_start` | bool | returns true if the clip slot will record on being fired.... | R |

### Methods

#### `create_clip()`

Creates an empty clip with the given length in the slot. Throws an error when called on non-empty slots or slots in non-MIDI tracks. 

**Arguments:**

- `arg2`: `float`

**Returns:** `None`

#### `delete_clip()`

Removes the clip contained in the slot. Raises an exception if the slot was empty. 

**Returns:** `None`

#### `duplicate_clip_to()`

Duplicates the slot’s clip to the passed in target slot. Overrides the target’s clip if it’s not empty. Raises an exception if the (source) slot itself is empty, or if source and target have different track types (audio vs. MIDI). Also raises if the source or target slot is in a group track (so called group slot). 

**Arguments:**

- `arg2`: `ClipSlot`

**Returns:** `None`

#### `fire()`

Fire a Clip if this Clipslot owns one, else trigger the stop button, if we have one. 

**Returns:** `None`

#### `set_fire_button_state()`

Set the clipslot’s fire button state directly. Supports all launch modes. 

**Arguments:**

- `arg2`: `bool`

**Returns:** `None`

#### `stop()`

Stop playing the contained Clip, if there is a Clip and its currently playing. 

**Returns:** `None`

---

## Class: ClipSlotPlayingState

---
