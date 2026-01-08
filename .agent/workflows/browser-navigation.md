---
description: How to navigate, filter, and preview items in the Ableton Browser
---

# Browser Search & Navigation

Deeply search and interact with the Ableton User Library, Core Library, and Plugins.

## Browser Visibility & State

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Toggle browser visible/hidden
conn.send_command("toggle_browser", {})

# Check current visibility and focus
state = conn.send_command("get_browser_state", {})
print(f"Browser Focused: {state.get('focused')}")
```

## Category Filtering

Narrow down your search to specific areas of the browser.

```python
# List available categories (Sounds, Drums, Instruments, Audio Effects, etc.)
categories = conn.send_command("get_browser_categories", {"category_type": "all"})

# Filter the browser view
conn.send_command("filter_browser", {"query": "Serum", "category": "Plugins"})
```

## Previewing Items

Audition sounds before loading them.

```python
# Preview an item by its internal URI
conn.send_command("preview_item_by_uri", {"uri": "ableton:user_library/samples/my_kick.wav"})

# Stop previewing
conn.send_command("stop_preview", {})
```

## Loading Items

```python
# Load an item directly to a track
conn.send_command("load_browser_item", {
    "uri": "ableton:core_library/devices/instruments/simpler",
    "track_index": 0
})
```
