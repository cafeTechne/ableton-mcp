# Live.MidiMap Module Reference

Auto-generated from Live 11 API documentation.

---

## Module-Level Functions

### `forward_midi_cc()`

**Arguments:**
- `arg2` (int)
- `arg3` (int)
- `arg4` (int)
- `ShouldConsumeEvent` (bool) = True]

**Returns:** `bool`

---

### `forward_midi_note()`

**Arguments:**
- `arg2` (int)
- `arg3` (int)
- `arg4` (int)
- `ShouldConsumeEvent` (bool) = True]

**Returns:** `bool`

---

### `forward_midi_pitchbend()`

**Arguments:**
- `arg2` (int)
- `arg3` (int)

**Returns:** `bool`

---

### `map_midi_cc()`

**Arguments:**
- `midi_map_handle` (int)
- `parameter` (DeviceParameter)
- `midi_channel` (int)
- `controller_number` (int)
- `map_mode` (MapMode)
- `avoid_takeover` (bool)
- `sensitivity` (float) = 1.0]

**Returns:** `bool`

---

### `map_midi_cc_with_feedback_map()`

**Arguments:**
- `midi_map_handle` (int)
- `parameter` (DeviceParameter)
- `midi_channel` (int)
- `controller_number` (int)
- `map_mode` (MapMode)
- `feedback_rule` (CCFeedbackRule)
- `avoid_takeover` (bool)
- `sensitivity` (float) = 1.0]

**Returns:** `bool`

---

### `map_midi_note()`

**Arguments:**
- `arg2` (DeviceParameter)
- `arg3` (int)
- `arg4` (int)

**Returns:** `bool`

---

### `map_midi_note_with_feedback_map()`

**Arguments:**
- `arg2` (DeviceParameter)
- `arg3` (int)
- `arg4` (int)
- `arg5` (NoteFeedbackRule)

**Returns:** `bool`

---

### `map_midi_pitchbend()`

**Arguments:**
- `arg2` (DeviceParameter)
- `arg3` (int)
- `arg4` (bool)

**Returns:** `bool`

---

### `map_midi_pitchbend_with_feedback_map()`

**Arguments:**
- `arg2` (DeviceParameter)
- `arg3` (int)
- `arg4` (PitchBendFeedbackRule)
- `arg5` (bool)

**Returns:** `bool`

---

### `send_feedback_for_parameter()`

**Arguments:**
- `arg2` (DeviceParameter)

**Returns:** `None`

---

## Class: CCFeedbackRule

*Structure to define feedback properties of MIDI mappings.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `cc_no` | unknown | ... | R |
| `cc_value_map` | unknown | ... | R |
| `channel` | unknown | ... | R |
| `delay_in_ms` | unknown | ... | R |

---

## Class: MapMode

---

## Class: NoteFeedbackRule

*Structure to define feedback properties of MIDI mappings.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `channel` | unknown | ... | R |
| `delay_in_ms` | unknown | ... | R |
| `note_no` | unknown | ... | R |
| `vel_map` | unknown | ... | R |

---

## Class: PitchBendFeedbackRule

*Structure to define feedback properties of MIDI mappings.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `channel` | unknown | ... | R |
| `delay_in_ms` | unknown | ... | R |
| `value_pair_map` | unknown | ... | R |

---
