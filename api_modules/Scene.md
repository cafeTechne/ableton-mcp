# Live.Scene Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: Scene

*This class represents an series of ClipSlots in Lives Sessionview matrix.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `canonical_parent` | unknown | Get the canonical parent of the scene.... | R |
| `clip_slots` | list | return a list of clipslots (see class AClipSlot) that this scene covers.... | R |
| `color` | list | Get/set access to the color of the Scene (RGB).... | R |
| `color_index` | list | Get/set access to the color index of the Scene. Can be None for no color.... | R |
| `is_empty` | bool | Returns True if all clip slots of this scene are empty.... | R |
| `is_triggered` | list | Const access to the scene’s trigger state.... | R |
| `name` | str | Get/Set the name of the scene. Might contain the substring BPM, whichidentifies that the scene will ... | R/W |
| `tempo` | unknown | Get/Set the tempo value of the scene.The Song will use the Scenes tempo as soon as the Scene is fire... | R/W |

### Methods

#### `fire()`

Fire the scene directly. Will fire all clipslots that this scene owns and select the scene itself. 

**Arguments:**

- `force_legato`: `bool` *(default: False [)*
- `can_select_scene_on_launch`: `bool` *(default: True]])*

**Returns:** `None`

#### `fire_as_selected()`

Fire the selected scene. Will fire all clipslots that this scene owns and select the next scene if necessary. 

**Arguments:**

- `force_legato`: `bool` *(default: False])*

**Returns:** `None`

#### `set_fire_button_state()`

Set the scene’s fire button state directly. Supports all launch modes. 

**Arguments:**

- `arg2`: `bool`

**Returns:** `None`

---
