---
description: How to control application focus, zoom, scroll, and browser visibility
---

# Application View Control

The AI agent can control what the user sees in Ableton Live. This is useful for emphasizing specific actions or helping the user follow along.

## Focus Views

Switch between Session, Arrangement, and Detail views.

```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Focus main views
conn.send_command("focus_view", {"view": "Session"})
conn.send_command("focus_view", {"view": "Arranger"})

# Focus detail views
conn.send_command("focus_view", {"view": "Detail/Clip"}) # Clip View
conn.send_command("focus_view", {"view": "Detail/DeviceChain"}) # Device View
```

## Zoom & Scroll

Adjust the visual scaling and position.

```python
# Zoom (0.5 to 2.0 recommended)
conn.send_command("zoom_view", {"factor": 1.2})

# Scroll (direction: 0=Up, 1=Down, 2=Left, 3=Right)
conn.send_command("scroll_view", {"direction": 1, "view_name": "Session"})
```

## Browser Control

Toggle or query the browser state.

```python
# Toggle visibility
conn.send_command("toggle_browser", {})

# Check state
state = conn.send_command("get_browser_state", {})
print(f"Browser visible: {state.get('visible')}")
```

## View Information

```python
# List all views available for manipulation
views = conn.send_command("get_available_views", {})

# Get overview of whole app state
overview = conn.send_command("get_application_overview", {})
```
