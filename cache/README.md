## Cache structure (canonical)

- This folder is the single source of truth for discovery data; consolidated master lists are removed.
- Category trees:
  - `audio_effects/`, `midi_effects/`, `drums_paths/`, `instruments/`, `sounds/`, `max_for_live/` — each holds `_index.json` files per path.
- Device parameters:
  - Use `devices/` to store per-device parameter dumps (suggested: `devices/<category>/<sanitized_name>.json`).

## How to enrich parameters (suggested flow)

1) Pick devices from the category `_index.json` files.
2) Load a device on a temp track (`load_device`), then call `get_device_parameters`.
3) Save the result into `devices/<category>/<device>.json` with name, uri, and parameters.
4) Remove the temp track; repeat in batches.

## Coordination notes

- Keep all new cache artifacts under `cache/`. Avoid consolidated master lists to reduce token use.
- If a category query times out, keep partial path dumps and resume; do not delete partial caches.
