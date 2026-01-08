# Ableton MCP Server

## Overview
This server exposes Ableton Live functionality via the Model Context Protocol (MCP). It communicates with the `AbletonMCP_Remote_Script` running inside Live.

## Configuration

### Caching Strategy (CRITICAL)
Live's browser is too large to search reliably in real-time. This server relies on **local caching** (`cache/*.json`) for all device and sample resolution.
- **Offline Planning**: `plan_load_device` checks these caches exclusively.
- **Loaders**: `load_simpler...` and `load_sampler...` check the cache *before* attempting any live lookup. Live lookup is a last-resort fallback and is often slow or unreliable.
- **Regeneration**: You must populate the cache (e.g. via `list_loadable_devices` during a setup phase) to ensure specific items are findable.
> [!IMPORTANT]
> **Seed Caches**: The included `cache/browser_*.json` files are seeded from a reference environment. If your Live library is different, usage of specific tools (like `starter_kit`'s default kit) might fail or require regeneration. Run `python MCP_Server/scripts/regenerate_cache.py` (requires active Live connection) to build your own.

### Trace Logging
Trace logging (performance profiling of MCP tools) is **disabled by default** to reduce log noise.
To enable it, set the environment variable:
```bash
ABLETON_MCP_TRACE=1
```
Logs will be written to `logs/trace_run.log`.

## Production Tools
`pattern_generator(track_index, clip_slot_index, pattern_type, bars, swing=0.0, humanize=0.0, fill=False)`
- Writes MIDI notes (Kick/Trap/DnB) to a clip.
- Supports `swing` (0.0-1.0), `humanize` (0.0-1.0), and automatic `fill` creation (appends to last bar).
- **Tip**: Recommended ranges: `swing` 0.1-0.3 for subtle groove, `humanize` 0.1-0.2 for realistic feel. Values >0.5 are extreme.

`starter_kit(tempo, genre)`
- Creates a 3-track scaffold (Drums, Bass, Keys) with basic naming and devices.

`audition_clip(sample_path, bars)`
- Loads a sample to "Audition" track, plays it.
- **Follow-up**: `confirm_audition(keep=True, target_track_index=N)` to move clip to a permanent track.

`setup_print_to_audio(source_track_index, name='Print')`
- Creates an Audio track, routes audio from Source track, and arms it. Ready for recording/bouncing.

### Music Theory & Automation
`generate_chord_progression(track_index, clip_index, key, scale, genre_progression, instrument_name=None)`
- Generates chord clips. Supports complex scales (e.g. `harmonic_minor`) and extensions (e.g. `jazz_minor` uses 7ths).
- `instrument_name`: Optional query (e.g. "Grand Piano") to load onto the track.

`generate_bassline(track_index, clip_index, key, scale, genre_progression, style, instrument_name=None)`
- Generates matching bassline. Styles: `follow`, `pulse`, `arpeggio`.
- `instrument_name`: Optional query (e.g. "Bass-Hip-Hop").

`apply_automation(track_index, clip_index, parameter_name, start_val, end_val, duration_bars)`
- Writes automation envelope points to the clip. **Requires script reload**.

### Offline Planning
`plan_load_device(query, category=None)`
- **Purpose**: Simulate what would happen if you tried to load a device or sample, without needing a valid Live connection.
- **Usage**: Useful for verifying simple queries against the local cache.
- **Diagnostics**: The returned JSON includes `sample_source` (user_cache vs fs_cache) and a `diagnostics` string explaining if items were found or if a Live connection is needed for deep search.

### Sample Loaders
`load_simpler_with_sample(track_index, file_path)`
`load_sampler_with_sample(track_index, file_path)`
- **Purpose**: Load a designated device (Simpler or Sampler) and populate it with a sample file.
- **Input**: `file_path` can be a full absolute path OR a "dirty" stem (e.g. `Kick_128bpm`). The server will attempt to resolve variants (like `Kick`) against the local cache.

## Troubleshooting
- **Updates not appearing?**
  If you modify `server.py` or the Remote Script, you must reload the script in Live:
  1. Copy `AbletonMCP_Remote_Script/__init__.py` to itself (touch the file) or restart Live.
  2. Toggle the "AbletonMCP" Control Surface in Link/Tempo/MIDI preferences (None -> AbletonMCP).

- **Connection Refused**: Ensure Live is running and the "AbletonMCP" script is selected in Control Surface settings.

## Known Issues
- **Live Search Latency**: Live's browser search API is slow and asynchronous. Tools like `starter_kit` default kit loading may fail if the database isn't indexed; retrying or using cached samples is recommended.
- **Audition Track Naming**: Rapidly creating/deleting "Audition" tracks may cause Live to auto-rename them (e.g. "Audition 15"). The `confirm_audition` tool now fuzzily matches the most recent track starting with "Audition" to mitigate this.

## Caches
The server maintains local JSON caches (`cache/`) to speed up resolution and enable offline planning.
- `browser_devices.json`: Index of devices.
- `browser_samples.json`: Index of samples.
- `routable_devices.json`: Index of valid routing targets.

**Regeneration**:
These caches are populated automatically when you use search/list tools (e.g., `list_loadable_devices`).
To regenerate them, ensure Live is connected and run:
```python
# scripts/regenerate_cache.py (mock example)
import server
ctx = MagicMock()
server.list_loadable_devices(ctx, category="all", max_items=1000)
# etc...
```
(See `task.md` for more details on cache enrichment).

**Git Strategy**:
`cache/` and `logs/` are gitignored to prevent pollution. Commit `cache/` only if you require shared deterministic offline planning for a team.
