# Live.Chain Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: Chain

*This class represents a group device chain in Live.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `canonical_parent` | unknown | Get the canonical parent of the chain.... | R |
| `color` | unknown | Access the color index of the Chain.... | R |
| `color_index` | unknown | Access the color index of the Chain.... | R |
| `devices` | list | Return const access to all available Devices that are present in the chains... | R |
| `has_audio_input` | bool | return True, if this Chain can be feed with an Audio signal. This istrue for all Audio Chains.... | R |
| `has_audio_output` | bool | return True, if this Chain sends out an Audio signal. This istrue for all Audio Chains, and MIDI cha... | R |
| `has_midi_input` | bool | return True, if this Chain can be feed with an Audio signal. This istrue for all MIDI Chains.... | R |
| `has_midi_output` | bool | return True, if this Chain sends out MIDI events. This istrue for all MIDI Chains with no Instrument... | R |
| `is_auto_colored` | bool | Get/set access to the auto color flag of the Chain.If True, the Chain will always have the same colo... | R |
| `mixer_device` | list | Return access to the mixer device that holds the chain’s mixer parameters:the Volume, Pan, and Senda... | R |
| `mute` | unknown | Mute/unmute the chain.... | R |
| `muted_via_solo` | list | Return const access to whether this chain is muted due to some other chainbeing soloed.... | R |
| `name` | str | Read/write access to the name of the Chain, as visible in the track header.... | R/W |
| `solo` | unknown | Get/Set the solo status of the chain. Note that this will not disable thesolo state of any other Cha... | R/W |

### Methods

#### `delete_device()`

Remove a device identified by its index from the chain. Throws runtime error if bad index.  

**Arguments:**

- `arg2`: `int`

**Returns:** `None`

---
