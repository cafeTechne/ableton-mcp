# Live.DeviceParameter Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: AutomationState

---

## Class: DeviceParameter

*This class represents a (automatable) parameter within a MIDI orAudio DSP-Device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `automation_state` | unknown | Returns state of type AutomationState.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the device parameter.... | R |
| `default_value` | unknown | Return the default value for this parameter.  A Default value is onlyavailable for non-quantized par... | R |
| `is_enabled` | bool | Returns false if the parameter has been macro mapped or disabled by Max.... | R |
| `is_quantized` | bool | Returns True, if this value is a boolean or integer like switch.Non quantized values are continues f... | R |
| `max` | list | Returns const access to the upper value of the allowed range forthis parameter... | R |
| `min` | list | Returns const access to the lower value of the allowed range forthis parameter... | R |
| `name` | str | Returns const access the name of this parameter, as visible in Livesautomation choosers.... | R |
| `original_name` | str | Returns const access the original name of this parameter, unaffected ofany renamings.... | R |
| `state` | unknown | Returns the state of the parameter:- enabled - the parameter’s value can be changed, - irrelevant - ... | R |
| `value` | unknown | Get/Set the current value (as visible in the GUI) this parameter.The value must be inside the min/ma... | R/W |
| `value_items` | bool | Return the list of possible values for this parameter. Raises an error if ‘is_quantized’ is False.... | R |

### Methods

#### `begin_gesture()`

Notify the begin of a modification of the parameter, when a sequence of modifications have to be consider a consistent group — for Sexample, when recording automation. 

**Returns:** `None`

#### `end_gesture()`

Notify the end of a modification of the parameter. See begin_gesture. 

**Returns:** `None`

#### `re_enable_automation()`

Reenable automation for this parameter. 

**Returns:** `None`

#### `str_for_value()`

Return a string representation of the given value. To be used for display purposes only.  This value can include characters like ‘db’ or ‘hz’, depending on the type of the parameter. 

**Arguments:**

- `arg2`: `float`

**Returns:** `unicode`

---

## Class: ParameterState

---
