# Live.Application Module Reference

Auto-generated from Live 11 API documentation.

---

## Module-Level Functions

### `combine_apcs()`

**Description:** Returns true if multiple APCs should be combined. 

**Returns:** `bool`

---

### `encrypt_challenge()`

**Description:** Returns an encrypted challenge based on the TEA algortithm 

**Arguments:**
- `dongle1` (int)
- `dongle2` (int)
- `key_index` (int) = 0]

**Returns:** `tuple`

---

### `encrypt_challenge2()`

**Description:** Returns the UMAC hash for the given challenge. 

**Returns:** `int`

---

### `get_application()`

**Description:** Returns the application instance. 

**Returns:** `Application`

---

### `get_random_int()`

**Description:** Returns a random integer from the given range. 

**Arguments:**
- `arg2` (int)

**Returns:** `int`

---

## Class: Application

*This class represents the Live application.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `browser` | int | Returns an interface to the browser.... | R |
| `canonical_parent` | unknown | Returns the canonical parent of the application.... | R |
| `control_surfaces` | list | Const access to a list of the control surfaces selected in preferences, in the same order.The list c... | R |
| `current_dialog_button_count` | unknown | Number of buttons on the current dialog.... | R |
| `current_dialog_message` | unknown | Text of the last dialog that appeared; Empty if all dialogs just disappeared.... | R |
| `open_dialog_count` | unknown | The number of open dialogs in Live. 0 if not dialog is open.... | R |
| `unavailable_features` | list | List of features that are unavailable due to limitations of the current Live edition.... | R |
| `view` | unknown | Returns the applications view component.... | R |

### Methods

#### `get_bugfix_version()`

Returns an integer representing the bugfix version of Live. 

**Returns:** `int`

#### `get_document()`

Returns the current Live Set. 

**Returns:** `Song`

#### `get_major_version()`

Returns an integer representing the major version of Live. 

**Returns:** `int`

#### `get_minor_version()`

Returns an integer representing the minor version of Live. 

**Returns:** `int`

#### `has_option()`

Returns True if the given entry exists in Options.txt, False otherwise. 

**Arguments:**

- `arg2`: `object`

**Returns:** `bool`

#### `press_current_dialog_button()`

Press a button, by index, on the current message box. 

**Arguments:**

- `arg2`: `int`

**Returns:** `None`

### Sub-Class: Application.View

**Properties:**
- `browse_mode`
- `canonical_parent`
- `focused_document_view`

**Methods:**
- `available_main_views()`
- `focus_view()`
- `hide_view()`
- `is_view_visible()`
- `scroll_view()`
- `show_view()`
- `toggle_browse()`
- `zoom_view()`

---

## Class: UnavailableFeature

---
