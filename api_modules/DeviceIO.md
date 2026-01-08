# Live.DeviceIO Module Reference

Auto-generated from Live 11 API documentation.

---

## Class: DeviceIO

*This class represents a specific input or output bus of a device.*

### Properties

| Property | Type | Description | Access |
|----------|------|-------------|--------|
| `available_routing_channels` | int | Return a list of channels for this IO endpoint.... | R |
| `available_routing_types` | int | Return a list of available routing types for this IO endpoint.... | R |
| `canonical_parent` | unknown | Get the canonical parent of the device IO.... | R |
| `default_external_routing_channel_is_none` | unknown | Get and set whether the default routing channel for External routing types is none.... | R |
| `routing_channel` | unknown | Get and set the current routing channel.Raises ValueError if the channel isn’t one of the current va... | R |
| `routing_type` | unknown | Get and set the current routing type.Raises ValueError if the type isn’t one of the current values i... | R |

---
