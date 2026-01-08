# Live.Browser Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: Browser

*This class represents the live browser data base.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `audio_effects` | list | Returns a browser item with access to all the Audio Effects content.... | R |
| `clips` | list | Returns a browser item with access to all the Clips content.... | R |
| `colors` | list | Returns a list of browser items containing the configured colors.... | R |
| `current_project` | list | Returns a browser item with access to all the Current Project content.... | R |
| `drums` | list | Returns a browser item with access to all the Drums content.... | R |
| `filter_type` | unknown | Bang triggered when the hotswap target has changed.... | R |
| `hotswap_target` | unknown | Bang triggered when the hotswap target has changed.... | R |
| `instruments` | list | Returns a browser item with access to all the Instruments content.... | R |
| `legacy_libraries` | list | Returns a list of browser items containing the installed legacy libraries. The list is always empty ... | R |
| `max_for_live` | list | Returns a browser item with access to all the Max For Live content.... | R |
| `midi_effects` | list | Returns a browser item with access to all the Midi Effects content.... | R |
| `packs` | list | Returns a browser item with access to all the Packs content.... | R |
| `plugins` | list | Returns a browser item with access to all the Plugins content.... | R |
| `samples` | list | Returns a browser item with access to all the Samples content.... | R |
| `sounds` | list | Returns a browser item with access to all the Sounds content.... | R |
| `user_folders` | list | Returns a list of browser items containing all the user folders.... | R |
| `user_library` | list | Returns a browser item with access to all the User Library content.... | R |

### Methods

#### `load_item()`

Loads the provided browser item. 

**Arguments:**

- `arg2`: `BrowserItem`

**Returns:** `None`

#### `preview_item()`

Previews the provided browser item. 

**Arguments:**

- `arg2`: `BrowserItem`

**Returns:** `None`

#### `relation_to_hotswap_target()`

Returns the relation between the given browser item and the current hotswap target 

**Arguments:**

- `arg2`: `BrowserItem`

**Returns:** `Relation`

#### `stop_preview()`

Stop the current preview. 

**Returns:** `None`

---

## Class: BrowserItem

*This class represents an item of the browser hierarchy.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `children` | list | Const access to the descendants of this browser item.... | R |
| `is_device` | unknown | Indicates if the browser item represents a device.... | R |
| `is_folder` | unknown | Indicates if the browser item represents folder.... | R |
| `is_loadable` | bool | True if item can be loaded via the Browser’s ‘load_item’ method.... | R |
| `is_selected` | bool | True if the item is ancestor of or the actual selection.... | R |
| `iter_children` | list | Const iterable access to the descendants of this browser item.... | R |
| `name` | str | Const access to the canonical display name of this browser item.... | R |
| `source` | unknown | Specifies where does item come from — i.e. Live pack, user library…... | R |
| `uri` | unknown | The uri describes a unique identifier for a browser item.... | R |

---

## Class: BrowserItemIterator

*This class iterates over children of another BrowserItem.*

### Methods

#### `next()`

Retrieve next item 

**Returns:** `BrowserItem`

---

## Class: FilterType

---

## Class: Relation

---
