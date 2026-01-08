# Live.DrumPad Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: DrumPad

*This class represents a drum group device pad in Live.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `canonical_parent` | unknown | Get the canonical parent of the drum pad.... | R |
| `chains` | list | Return const access to the list of chains in this drum pad.... | R |
| `mute` | unknown | Mute/unmute the pad.... | R |
| `name` | str | Return const access to the drum pad’s name. It depends on the contained chains.... | R |
| `note` | unknown | Get the MIDI note of the drum pad.... | R |
| `solo` | unknown | Solo/unsolo the pad.... | R |

### Methods

#### `delete_all_chains()`

Deletes all chains associated with a drum pad. This is equivalent to deleting a drum rack pad in Live. 

**Returns:** `None`

---
