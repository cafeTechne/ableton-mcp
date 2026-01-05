## Near-term targets

- Sidechain helper: get `SidechainHelper_Advanced` indexed in the Live browser (user library preset path is `Presets/Audio Effects/Max Audio Effect/AbletonMCP`), then rerun `load_sidechain_helper` to validate routing on hidden-UI devices (Compressor/Glue).
- Parameter cache: load a spread of common Audio FX (Compressor, Glue Compressor, Gate, Limiter, EQ Eight, Auto Filter, Drum Buss, Echo, Reverb, Hybrid Reverb if available) and capture `get_device_parameters` to enrich `cache/browser_devices.json`.
- MPE/extended notes: verify probability/velocity deviation/release velocity survive round-trips (`add_notes_to_clip`, `quantize_clip`, `duplicate_clip`) on a MIDI clip.
- Scene stop regression: keep an eye on `stop_scene` behavior after the Live reload; ensure stopped slot counts look sane when more scenes exist.
- Form builder + clip loader: validate `form_builder` with generic public preset only; all show/band-specific forms should come from private JSON via `ABLETON_MCP_PRIVATE_PRESETS`. Validate `load_clip_by_name` and new `load_sample_by_name` slot targeting; expand starter pattern library as needed.
- Pump/duck polish: smoke `lfo_pump_helper` after the load-by-name fix and ensure ghost/duck presets stay stable after reloads.

## Progress (2026-01-04)

- Added `configure_track_routing` (arm/monitor/I-O/sends in one call) and `trigger_test_midi` (clip note + optional CC) MCP helpers for GameBus and other routes.
- Added `pump_helper` (Auto Pan/Compressor one-shot setup) and plugin sidechain routing helpers (`set_device_audio_input`, device routing detection); sidechain source routing works where devices expose routing types/channels.
- Added `ducking_tool` presets (duck/hard/soft/ghost) and `lfo_pump_helper` for LFO-style pump loads; auto_test_suite CLI wrapper (`scripts/auto_test.py`) and device loader (`scripts/device_loader.py`); routable device cache now at `cache/routable_devices.json`.
- Completed audio_effects parameter dumps: Delay_&_Loop (185), Drive_&_Color (114), Dynamics (91), EQ_&_Filters (107), Modulators (39), Pitch_&_Modulation (79), Reverb_&_Resonance (153), Utilities (32) now in `cache/devices/audio_effects`. Used track 6 for all loads; devices left in place.
- Remaining cache work (if needed): other categories (instruments, midi_effects, drums_paths, sounds, max_for_live) only have path inventories; no per-device parameter dumps yet.
- Sidechain helper and MPE/scene-stop checks still outstanding (see Near-term targets).
- Built `form_builder` MCP macro with only a generic public preset; song/band-specific presets are expected in a private JSON (set `ABLETON_MCP_PRIVATE_PRESETS`, default `../ableton-mcp-private/presets.json`). Added `load_clip_by_name` (browser clip resolver with scene slot targeting) plus Remote Script slot selection for deterministic loads.
- `auto_test_suite` now runs end-to-end after Live reload: creates/fires temp MIDI clip, loads Compressor on target track, sets sidechain, and snapshots routable devices to `cache/routable_devices.json`.
- Cached sample loader now resolves via cache → browser folder → root Samples fallback; added `search_cached_samples` helper and optional no-create flags on clip loads. Simpler/Sampler hotswap now also falls back to root Samples URIs (Live reload required for control surface changes).

## Nice-to-have follow-ups

- Add a quick CLI script for cache enrichment that loads devices by name, fetches parameters, and writes a short summary to logs/README.
- Optional: surface a thin MCP tool wrapper around the sidechain helper load path once the browser indexing confirms the preset is discoverable.
- Modular caching: if category scans hit `max_items`, split caching per category (audio_effects, instruments, midi_effects, drums, user content) and persist intermediate files so other agents can resume without repeating work.

## Routing & integration targets

- Scene/clip trigger macros for external event bridges (fire scenes/clips by name/pattern).
- Optional: echo GameBus input back to Live for LED feedback/clip triggers if desired.
- Preset recall helper for third-party plugins: load user presets by name/path since custom curves (LFO Tool, etc.) aren’t scriptable.

## Additional ideas / missing pieces

- Stability polish only if needed: socket timeout/logging tweaks from upstream PR50-style changes.
- Curate on-demand M4L param fetch: keep the high-value cached devices, fetch others live to reduce cache churn.
- Lightweight CLI to load any browser item and dump `get_device_parameters` on demand (no batch cache).
- Documentation: short how-to for GameBus routing (already in `docs/gamebus_integration.md`) and a quickstart for MCP routing helpers once added.
- Third-party plugin notes: no public API for Helm/Vital/Surge XT; we can load them, automate exposed parameters, and recall presets, but curve drawing/UI-only features need manual preset creation.
