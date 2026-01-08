# Live.Song Module Reference

Auto-generated from Live 11 API documentation.

---

## Module-Level Functions

### `get_all_scales_ordered()`

**Description:** Get an ordered tuple of tuples of all available scale names to intervals. 

**Returns:** `tuple`

---

## Class: BeatTime

*Represents a Time, splitted into Bars, Beats, SubDivision and Ticks.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `bars` | unknown | ... | R |
| `beats` | unknown | ... | R |
| `sub_division` | unknown | ... | R |
| `ticks` | unknown | ... | R |

---

## Class: CaptureDestination

*The destination for MIDI capture.*

---

## Class: CaptureMode

*The capture mode that is used for capture and insert scene.*

---

## Class: CuePoint

*Represents a ‘Marker’ in the arrangement.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `canonical_parent` | int | Get the canonical parent of the cue point.... | R |
| `name` | int | Get/Listen to the name of this CuePoint, as visible in the arranger.... | R |
| `time` | int | Get/Listen to the CuePoint’s time in beats.... | R |

### Methods

#### `jump()`

When the Song is playing, set the playing-position quantized to this Cuepoint’s time. When not playing, simply move the start playing position. 

**Returns:** `None`

---

## Class: Quantization

---

## Class: RecordingQuantization

---

## Class: SessionRecordStatus

---

## Class: SmptTime

*Represents a Time, split into Hours, Minutes, Seconds and Frames.The frame type must be specified when calling a function that returnsa SmptTime.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `frames` | unknown | ... | R |
| `hours` | unknown | ... | R |
| `minutes` | unknown | ... | R |
| `seconds` | unknown | ... | R |

---

## Class: Song

*This class represents a Live set.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `appointed_device` | int | Read, write, and listen access to the appointed Device... | R |
| `arrangement_overdub` | unknown | Get/Set the global arrangement overdub state.... | R/W |
| `back_to_arranger` | unknown | Get/Set if triggering a Clip in the Session, disabled the playback ofClips in the Arranger.... | R/W |
| `can_capture_midi` | unknown | Get whether there currently is material to be captured on any tracks.... | R |
| `can_jump_to_next_cue` | bool | Returns true when there is a cue marker right to the playing pos thatwe could jump to.... | R |
| `can_jump_to_prev_cue` | bool | Returns true when there is a cue marker left to the playing pos thatwe could jump to.... | R |
| `can_redo` | bool | Returns true if there is an undone action that we can redo.... | R |
| `can_undo` | bool | Returns true if there is an action that we can restore.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the song.... | R |
| `clip_trigger_quantization` | list | Get/Set access to the quantization settings that are used to fireClips in the Session.... | R/W |
| `count_in_duration` | unknown | Get the count in duration. Returns an index, mapped as follows: 0 - None, 1 - 1 Bar, 2 - 2 Bars, 3 -... | R |
| `cue_points` | int | Const access to a list of all cue points of the Live Song.... | R |
| `current_song_time` | list | Get/Set access to the songs current playing position in ms.... | R/W |
| `exclusive_arm` | unknown | Get if Tracks should be armed exclusively by default.... | R |
| `exclusive_solo` | unknown | Get if Tracks should be soloed exclusively by default.... | R |
| `groove_amount` | unknown | Get/Set the global groove amount, that adjust all setup groovesin all clips.... | R/W |
| `groove_pool` | unknown | Get the groove pool.... | R |
| `is_counting_in` | unknown | Get whether currently counting in.... | R |
| `is_playing` | bool | Returns true if the Song is currently playing.... | R |
| `last_event_time` | unknown | Return the time of the last set event in the song. In contrary tosong_length, this will not add some... | R |
| `loop` | unknown | Get/Set the looping flag that en/disables the usage of the globalloop markers in the song.... | R/W |
| `loop_length` | unknown | Get/Set the length of the global loop marker position in beats.... | R/W |
| `loop_start` | unknown | Get/Set the start of the global loop marker position in beats.... | R/W |
| `master_track` | list | Access to the Master Track (always available)... | R |
| `metronome` | unknown | Get/Set if the metronom is audible.... | R/W |
| `midi_recording_quantization` | list | Get/Set access to the settings that are used to quantizeMIDI recordings.... | R/W |
| `nudge_down` | unknown | Get/Set the status of the nudge down button.... | R/W |
| `nudge_up` | unknown | Get/Set the status of the nudge up button.... | R/W |
| `overdub` | unknown | Legacy hook for Live 8 overdub state. Now hooks tosession record, but never starts playback.... | R |
| `punch_in` | unknown | Get/Set the flag that will enable recording as soon as the Song playsand hits the global loop start ... | R/W |
| `punch_out` | unknown | Get/Set the flag that will disable recording as soon as the Song playsand hits the global loop end r... | R/W |
| `re_enable_automation_enabled` | bool | Returns true if some automated parameter has been overriden... | R |
| `record_mode` | unknown | Get/Set the state of the global recording flag.... | R/W |
| `return_tracks` | list | Const access to the list of available Return Tracks.... | R |
| `root_note` | unknown | Set and access the root note (i.e. key) of the song used for control surfaces. The root note can be ... | R |
| `scale_intervals` | int | Reports the current scale’s intervals as a list of integers, starting with the root note and represe... | R |
| `scale_name` | str | Set and access the last used scale name for control surfaces. The default scale names that can be sa... | R |
| `scenes` | list | Const access to a list of all Scenes in the Live Song.... | R |
| `select_on_launch` | unknown | Get if Scenes and Clips should be selected when fired.... | R |
| `session_automation_record` | bool | Returns true if automation recording is enabled.... | R |
| `session_record` | unknown | Get/Set the session record state.... | R/W |
| `session_record_status` | unknown | Get the session slot-recording state.... | R |
| `signature_denominator` | list | Get/Set access to the global signature denominator of the Song.... | R/W |
| `signature_numerator` | list | Get/Set access to the global signature numerator of the Song.... | R/W |
| `song_length` | unknown | Return the time of the last set event in the song, plus som extra beatsthat are usually added for be... | R |
| `swing_amount` | list | Get/Set access to the amount of swing that is applied when adding or quantizing notes to MIDI clips... | R/W |
| `tempo` | unknown | Get/Set the global project tempo.... | R/W |
| `tracks` | list | Const access to a list of all Player Tracks in the Live Song, exludingthe return and Master Track (s... | R |
| `view` | unknown | Representing the view aspects of a Live document: The Session and Arrangerview.... | R |
| `visible_tracks` | list | Const access to a list of all visible Player Tracks in the Live Song, exludingthe return and Master ... | R |

### Methods

#### `begin_undo_step()`

**Returns:** `None`

#### `capture_and_insert_scene()`

Capture currently playing clips and insert them as a new scene after the selected scene. Raises a runtime error if creating a new scene would exceed the limitations. 

**Arguments:**

- `CaptureMode`: `int` *(default: Song.CaptureMode.all])*

**Returns:** `None`

#### `capture_midi()`

Capture recently played MIDI material from audible tracks. If no Destination is given or Destination is set to CaptureDestination.auto, the captured material is inserted into the Session or Arrangement depending on which is visible. If Destination is set to CaptureDestination.session or CaptureDestination.arrangement, inserts the material into Session or Arrangement, respectively. Raises a limitation error when capturing into the Session and a new scene would have to be created but can’t because it would exceed the limitations. 

**Arguments:**

- `Destination`: `int` *(default: Song.CaptureDestination.auto])*

**Returns:** `None`

#### `continue_playing()`

Continue playing the song from the current position 

**Returns:** `None`

#### `create_audio_track()`

Create a new audio track at the optional given index and return it.If the index is -1, the new track is added at the end. It will create a default audio track if possible. If the index is invalid or the new track would exceed the limitations, a limitation error is raised.If the index is missing, the track is created after the last selected item 

**Arguments:**

- `Index`: `object` *(default: None])*

**Returns:** `Track`

#### `create_midi_track()`

Create a new midi track at the optional given index and return it.If the index is -1,  the new track is added at the end.It will create a default midi track if possible. If the index is invalid or the new track would exceed the limitations, a limitation error is raised.If the index is missing, the track is created after the last selected item 

**Arguments:**

- `Index`: `object` *(default: None])*

**Returns:** `Track`

#### `create_return_track()`

Create a new return track at the end and return it. If the new track would exceed  the limitations, a limitation error is raised.  If the maximum number of return tracks is exceeded, a RuntimeError is raised. 

**Returns:** `Track`

#### `create_scene()`

Create a new scene at the given index. If the index is -1, the new scene is added at the end. If the index is invalid or the new scene would exceed the limitations, a limitation error is raised. 

**Arguments:**

- `arg2`: `int`

**Returns:** `Scene`

#### `delete_return_track()`

Delete the return track with the given index. If no track with this index exists, an exception will be raised. 

**Arguments:**

- `arg2`: `int`

**Returns:** `None`

#### `delete_scene()`

Delete the scene with the given index. If no scene with this index exists, an exception will be raised. 

**Arguments:**

- `arg2`: `int`

**Returns:** `None`

#### `delete_track()`

Delete the track with the given index. If no track with this index exists, an exception will be raised. 

**Arguments:**

- `arg2`: `int`

**Returns:** `None`

#### `duplicate_scene()`

Duplicates a scene and selects the new one. Raises a limitation error if creating a new scene would exceed the limitations. 

**Arguments:**

- `arg2`: `int`

**Returns:** `None`

#### `duplicate_track()`

Duplicates a track and selects the new one. If the track is inside a folded group track, the group track is unfolded. Raises a limitation error if creating a new track would exceed the limitations. 

**Arguments:**

- `arg2`: `int`

**Returns:** `None`

#### `end_undo_step()`

**Returns:** `None`

#### `find_device_position()`

Returns the closest possible position to the given target, where the device can be inserted. If inserting is not possible at all (i.e. if the device type is wrong), -1 is returned. 

**Arguments:**

- `device`: `Device`
- `target`: `LomObject`
- `target_position`: `int`

**Returns:** `int`

#### `force_link_beat_time()`

Force the Link timeline to jump to Lives current beat time. Danger: This can cause beat time discontinuities in other connected apps. 

**Returns:** `None`

#### `get_beats_loop_length()`

Get const access to the songs loop length, using a BeatTime class with the current global set signature. 

**Returns:** `BeatTime`

#### `get_beats_loop_start()`

Get const access to the songs loop start, using a BeatTime class with the current global set signature. 

**Returns:** `BeatTime`

#### `get_current_beats_song_time()`

Get const access to the songs current playing position, using a BeatTime class with the current global set signature. 

**Returns:** `BeatTime`

#### `get_current_smpte_song_time()`

Get const access to the songs current playing position, by specifying the SMPTE format in which you would like to receive the time. 

**Arguments:**

- `arg2`: `int`

**Returns:** `SmptTime`

#### `get_data()`

Get data for the given key, that was previously stored using set_data. 

**Arguments:**

- `key`: `object`
- `default_value`: `object`

**Returns:** `object`

#### `is_cue_point_selected()`

Return true if the global playing pos is currently on a cue point. 

**Returns:** `bool`

#### `jump_by()`

Set a new playing pos, relative to the current one. 

**Arguments:**

- `arg2`: `float`

**Returns:** `None`

#### `jump_to_next_cue()`

Jump to the next cue (marker) if possible. 

**Returns:** `None`

#### `jump_to_prev_cue()`

Jump to the prior cue (marker) if possible. 

**Returns:** `None`

#### `move_device()`

Move a device into the target at the given position, where 0 moves it before the first device and len(devices) moves it to the end of the device chain.If the device cannot be moved to this position, the nearest possible position is chosen. If the device type is not valid, a runtime error is raised.Returns the index, where the device was moved to. 

**Arguments:**

- `device`: `Device`
- `target`: `LomObject`
- `target_position`: `int`

**Returns:** `int`

#### `play_selection()`

Start playing the current set selection, or do nothing if no selection is set. 

**Returns:** `None`

#### `re_enable_automation()`

Discards overrides of automated parameters. 

**Returns:** `None`

#### `redo()`

Redo the last action that was undone. 

**Returns:** `None`

#### `scrub_by()`

Same as jump_by, but does not stop playback. 

**Arguments:**

- `arg2`: `float`

**Returns:** `None`

#### `set_data()`

Store data for the given key in this object. The data is persistent and will be restored when loading the Live Set. 

**Arguments:**

- `key`: `object`
- `value`: `object`

**Returns:** `None`

#### `set_or_delete_cue()`

When a cue is selected, it gets deleted. If no cue is selected, a new cue is created at the current global songtime. 

**Returns:** `None`

#### `start_playing()`

Start playing from the startmarker 

**Returns:** `None`

#### `stop_all_clips()`

Stop all playing Clips (if any) but continue playing the Song. 

**Arguments:**

- `Quantized`: `bool` *(default: True])*

**Returns:** `None`

#### `stop_playing()`

Stop playing the Song. 

**Returns:** `None`

#### `tap_tempo()`

Trigger the tap tempo function. 

**Returns:** `None`

#### `trigger_session_record()`

Triggers a new session recording. 

**Arguments:**

- `record_length`: `float` *(default: 1.7976931348623157e+308])*

**Returns:** `None`

#### `undo()`

Undo the last action that was made. 

**Returns:** `None`

### Sub-Class: Song.View

**Properties:**
- `canonical_parent`
- `detail_clip`
- `draw_mode`
- `follow_song`
- `highlighted_clip_slot`
- `selected_chain`
- `selected_parameter`
- `selected_scene`
- `selected_track`

**Methods:**
- `select_device()`

---

## Class: TimeFormat

---
