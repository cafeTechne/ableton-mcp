# Live.Track Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: DeviceContainer

*This class is a common super class of Track and Chain*

---

## Class: DeviceInsertMode

---

## Class: RoutingChannel

*This class represents a routing channel.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `display_name` | str | Display name of routing channel.... | R |
| `layout` | unknown | The routing channel’s Layout, e.g., mono or stereo.... | R |

---

## Class: RoutingChannelLayout

---

## Class: RoutingType

*This class represents a routing type.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `attached_object` | unknown | Live object associated with the routing type.... | R |
| `category` | unknown | Category of the routing type.... | R |
| `display_name` | str | Display name of routing type.... | R |

---

## Class: RoutingTypeCategory

---

## Class: Track

*This class represents a track in Live. It can be either an Audio track, a MIDI Track, a Return Track or the Master track. The Master Track and at least one Audio or MIDI track will be always present.Return Tracks are optional.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `arm` | unknown | Arm the track for recording. Not available for Master- and Send Tracks.... | R |
| `arrangement_clips` | list | const access to the list of clips in arrangement viewThe list will be empty for the master, send and... | R |
| `available_input_routing_channels` | list | Return a list of source channels for input routing.... | R |
| `available_input_routing_types` | list | Return a list of source types for input routing.... | R |
| `available_output_routing_channels` | list | Return a list of destination channels for output routing.... | R |
| `available_output_routing_types` | list | Return a list of destination types for output routing.... | R |
| `can_be_armed` | bool | return True, if this Track has a valid arm property. Not all trackscan be armed (for example return ... | R |
| `can_be_frozen` | bool | return True, if this Track can be frozen.... | R |
| `can_show_chains` | bool | return True, if this Track contains a rack instrument device that is capable of showing its chains i... | R |
| `canonical_parent` | unknown | Get the canonical parent of the track.... | R |
| `clip_slots` | list | const access to the list of clipslots (see class AClipSlot) for this track.The list will be empty fo... | R |
| `color` | list | Get/set access to the color of the Track (RGB).... | R |
| `color_index` | list | Get/Set access to the color index of the track. Can be None for no color.... | R/W |
| `current_input_routing` | unknown | Get/Set the name of the current active input routing.When setting a new routing, the new routing mus... | R/W |
| `current_input_sub_routing` | unknown | Get/Set the current active input sub routing.When setting a new routing, the new routing must be one... | R/W |
| `current_monitoring_state` | unknown | Get/Set the track’s current monitoring state.... | R/W |
| `current_output_routing` | unknown | Get/Set the current active output routing.When setting a new routing, the new routing must be one of... | R/W |
| `current_output_sub_routing` | unknown | Get/Set the current active output sub routing.When setting a new routing, the new routing must be on... | R/W |
| `devices` | list | Return const access to all available Devices that are present in the TracksDevicechain. This tuple w... | R |
| `fired_slot_index` | list | const access to the index of the fired (and thus blinking) clipslot in this track.This index is -1 i... | R |
| `fold_state` | bool | Get/Set whether the track is folded or not. Only available if is_foldable is True.... | R/W |
| `group_track` | unknown | return the group track if is_grouped.... | R |
| `has_audio_input` | bool | return True, if this Track can be feed with an Audio signal. This istrue for all Audio Tracks.... | R |
| `has_audio_output` | bool | return True, if this Track sends out an Audio signal. This istrue for all Audio Tracks, and MIDI tra... | R |
| `has_midi_input` | bool | return True, if this Track can be feed with an Audio signal. This istrue for all MIDI Tracks.... | R |
| `has_midi_output` | bool | return True, if this Track sends out MIDI events. This istrue for all MIDI Tracks with no Instrument... | R |
| `implicit_arm` | unknown | Arm the track for recording. When The track is implicitly armed, it showsin a weaker color in the li... | R |
| `input_meter_left` | unknown | Momentary value of left input channel meter, 0.0 to 1.0. For Audio Tracks only.... | R |
| `input_meter_level` | unknown | Return the MIDI or Audio meter value of the Tracks input, depending on thetype of the Track input. M... | R |
| `input_meter_right` | unknown | Momentary value of right input channel meter, 0.0 to 1.0. For Audio Tracks only.... | R |
| `input_routing_channel` | unknown | Get and set the current source channel for input routing.Raises ValueError if the type isn’t one of ... | R |
| `input_routing_type` | unknown | Get and set the current source type for input routing.Raises ValueError if the type isn’t one of the... | R |
| `input_routings` | list | Const access to the list of available input routings.... | R |
| `input_sub_routings` | list | Return a list of all available input sub routings.... | R |
| `is_foldable` | bool | return True if the track can be (un)folded to hide/reveal contained tracks.... | R |
| `is_frozen` | bool | return True if this Track is currently frozen. No changes should be applied to the track’s devices o... | R |
| `is_grouped` | bool | return True if this Track is current part of a group track.... | R |
| `is_part_of_selection` | bool | return False if the track is not selected.... | R |
| `is_showing_chains` | unknown | Get/Set whether a track with a rack device is showing its chains in session view.... | R/W |
| `is_visible` | bool | return False if the track is hidden within a folded group track.... | R |
| `mixer_device` | list | Return access to the special Device that every Track has: This Device containsthe Volume, Pan, Senda... | R |
| `mute` | unknown | Mute/unmute the track.... | R |
| `muted_via_solo` | bool | Returns true if the track is muted because another track is soloed.... | R |
| `name` | str | Read/write access to the name of the Track, as visible in the track header.... | R/W |
| `output_meter_left` | unknown | Momentary value of left output channel meter, 0.0 to 1.0.For tracks with audio output only.... | R |
| `output_meter_level` | unknown | Return the MIDI or Audio meter value of the Track output (behind themixer_device), depending on the ... | R |
| `output_meter_right` | unknown | Momentary value of right output channel meter, 0.0 to 1.0.For tracks with audio output only.... | R |
| `output_routing_channel` | unknown | Get and set the current destination channel for output routing.Raises ValueError if the channel isn’... | R |
| `output_routing_type` | unknown | Get and set the current destination type for output routing.Raises ValueError if the type isn’t one ... | R |
| `output_routings` | list | Const access to the list of all available output routings.... | R |
| `output_sub_routings` | list | Return a list of all available output sub routings.... | R |
| `playing_slot_index` | list | const access to the index of the currently playing clip in the track.Will be -1 when no clip is play... | R |
| `solo` | unknown | Get/Set the solo status of the track. Note that this will not disable thesolo state of any other tra... | R/W |
| `view` | unknown | Representing the view aspects of a Track.... | R |

### Methods

#### `delete_clip()`

Delete the given clip. Raises a runtime error when the clip belongs to another track. 

**Arguments:**

- `arg2`: `Clip`

**Returns:** `None`

#### `delete_device()`

Delete a device identified by the index in the ‘devices’ list. 

**Arguments:**

- `arg2`: `int`

**Returns:** `None`

#### `duplicate_clip_slot()`

Duplicate a clip and put it into the next free slot and return the index of the destination slot. A new scene is created if no free slot is available. If creating the new scene would exceed the limitations, a runtime error is raised. 

**Arguments:**

- `arg2`: `int`

**Returns:** `int`

#### `duplicate_clip_to_arrangement()`

Duplicate the given clip into the arrangement of this track at the provided destination time and return it. When the type of the clip and the type of the track are incompatible, a runtime error is raised. 

**Arguments:**

- `clip`: `Clip`
- `destination_time`: `float`

**Returns:** `Clip`

#### `get_data()`

Get data for the given key, that was previously stored using set_data. 

**Arguments:**

- `key`: `object`
- `default_value`: `object`

**Returns:** `object`

#### `jump_in_running_session_clip()`

Jump forward or backward in the currently running Sessionclip (if any) by the specified relative amount in beats. Does nothing if no Session Clip is currently running. 

**Arguments:**

- `arg2`: `float`

**Returns:** `None`

#### `set_data()`

Store data for the given key in this object. The data is persistent and will be restored when loading the Live Set. 

**Arguments:**

- `key`: `object`
- `value`: `object`

**Returns:** `None`

#### `stop_all_clips()`

Stop running and triggered clip and slots on this track. 

**Arguments:**

- `Quantized`: `bool` *(default: True])*

**Returns:** `None`

### Sub-Class: Track.View

**Properties:**
- `canonical_parent`
- `device_insert_mode`
- `is_collapsed`
- `selected_device`

**Methods:**
- `select_instrument()`

---
