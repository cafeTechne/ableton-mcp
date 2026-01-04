## Near-term targets

- Sidechain helper: get `SidechainHelper_Advanced` indexed in the Live browser (user library preset path is `Presets/Audio Effects/Max Audio Effect/AbletonMCP`), then rerun `load_sidechain_helper` to validate routing on hidden-UI devices (Compressor/Glue).
- Parameter cache: load a spread of common Audio FX (Compressor, Glue Compressor, Gate, Limiter, EQ Eight, Auto Filter, Drum Buss, Echo, Reverb, Hybrid Reverb if available) and capture `get_device_parameters` to enrich `cache/browser_devices.json`.
- MPE/extended notes: verify probability/velocity deviation/release velocity survive round-trips (`add_notes_to_clip`, `quantize_clip`, `duplicate_clip`) on a MIDI clip.
- Scene stop regression: keep an eye on `stop_scene` behavior after the Live reload; ensure stopped slot counts look sane when more scenes exist.

## Progress (2026-01-04)

- Completed audio_effects parameter dumps: Delay_&_Loop (185), Drive_&_Color (114), Dynamics (91), EQ_&_Filters (107), Modulators (39), Pitch_&_Modulation (79), Reverb_&_Resonance (153), Utilities (32) now in `cache/devices/audio_effects/…`. Used track 6 for all loads; devices left in place.
- Remaining cache work (if needed): other categories (instruments, midi_effects, drums_paths, sounds, max_for_live) only have path inventories; no per-device parameter dumps yet.
- Sidechain helper and MPE/scene-stop checks still outstanding (see Near-term targets).

## Nice-to-have follow-ups

- Add a quick CLI script for cache enrichment that loads devices by name, fetches parameters, and writes a short summary to logs/README.
- Optional: surface a thin MCP tool wrapper around the sidechain helper load path once the browser indexing confirms the preset is discoverable.
- Modular caching: if category scans hit `max_items`, split caching per category (audio_effects, instruments, midi_effects, drums, user content) and persist intermediate files so other agents can resume without repeating work.
