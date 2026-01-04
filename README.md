# AbletonMCP - Ableton Live Model Context Protocol Integration
[![smithery badge](https://smithery.ai/badge/@ahujasid/ableton-mcp)](https://smithery.ai/server/@ahujasid/ableton-mcp)

AbletonMCP connects Ableton Live to Claude AI through the Model Context Protocol (MCP), allowing Claude to interact with and control Ableton Live for prompt-assisted music production.

### Join the Community

Give feedback, get inspired, and build on top of the MCP: [Discord](https://discord.gg/3ZrMyGKnaU). Made by [Siddharth](https://x.com/sidahuj)

## Features

- Two-way communication between Ableton Live and MCP over a local socket
- Track and routing control: create/duplicate/delete tracks and scenes, set I/O, monitoring, arm/mute/solo, sends, and returns
- Clip control: create/delete/duplicate, set loop/length, quantize MIDI notes, and launch/stop clips or scenes
- Device loading and parameter writes with normalization (percent/dB strings, clamping to min/max, sidechain helper)
- Presets and patterns: save/load device snapshots to disk, drop quick drum and chord patterns
- Browser search/cache for instruments, MIDI/audio effects, racks, and user content

## Components

1. **Ableton Remote Script** (`AbletonMCP_Remote_Script/__init__.py`): Starts a TCP socket inside Ableton Live and executes commands received from the MCP server. Host/port default to `localhost:9877` and can be overridden with `ABLETON_MCP_HOST` / `ABLETON_MCP_PORT`.
2. **MCP Server** (`MCP_Server/server.py`): FastMCP STDIO server that speaks to the Remote Script socket. Logs to stderr and `logs/ableton-mcp.log`.

## Connection overview

- When Ableton loads the **AbletonMCP** control surface, the Remote Script opens a socket on `ABLETON_MCP_HOST:ABLETON_MCP_PORT` (default `localhost:9877`).
- The MCP server connects to that socket when a tool is invoked.
- Start Ableton Live first (so the socket is listening), then launch the MCP server.

## Prerequisites

- Ableton Live 10 or newer (Windows 10/11 steps below)
- Python 3.10 or newer
- [uv package manager](https://astral.sh/uv) installed and on PATH

## MCP client command (Codex, Claude Desktop, Cursor)

Use the local repo as the package source so the `ableton-mcp` console entrypoint is available:

```json
{
  "mcpServers": {
    "AbletonMCP": {
      "command": "uvx",
      "args": [
        "--from",
        "C:\\\\path\\\\to\\\\ableton-mcp",
        "ableton-mcp"
      ]
    }
  }
}
```

- Replace `C:\\path\\to\\ableton-mcp` with the absolute path of this repo.
- The server runs over STDIO (no HTTP) and writes logs to stderr and `logs/ableton-mcp.log`.
- Run only one MCP server instance at a time.

## Installing the Ableton Remote Script (Windows)

1. Close Ableton Live.
2. Create `AbletonMCP` inside one of these locations (replace `XX` with your Live version):
   - User Library: `C:\Users\<you>\AppData\Roaming\Ableton\Live XX\Preferences\User Remote Scripts\AbletonMCP`
   - Shared install: `C:\ProgramData\Ableton\Live XX\Resources\MIDI Remote Scripts\AbletonMCP`
3. Copy `AbletonMCP_Remote_Script\__init__.py` from this repo into that `AbletonMCP` folder.
4. Launch Ableton Live.
5. Open Preferences > Link, Tempo & MIDI.
6. In Control Surface, choose **AbletonMCP**; set Input and Output to **None**.
7. Confirm it loaded: Ableton’s status bar briefly shows “AbletonMCP: Listening for commands on port 9877” (or your `ABLETON_MCP_PORT`). You can also run `scripts/doctor.ps1` to verify the folder and port.

## Running the MCP server locally

- Preferred (from this repo): `uvx --from "C:\path\to\ableton-mcp" ableton-mcp`
- Alternative: `uv run python -m MCP_Server.server` (from the repo root)
- Environment variables:
  - `ABLETON_MCP_HOST` (default `localhost`)
  - `ABLETON_MCP_PORT` (default `9877`)
- Logs: stderr and `logs/ableton-mcp.log`

## Doctor script (Windows)

Run a quick health check from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/doctor.ps1
```

It verifies `uv`/`uvx`/Python visibility, lists expected Remote Script install paths, checks for the `AbletonMCP` folder and `__init__.py`, and tests the TCP port (`localhost:9877` by default).

## Usage

1. Install the Remote Script and select **AbletonMCP** as the control surface.
2. Start Ableton Live (which opens the socket).
3. Start the MCP server via `uvx --from "<repo>" ableton-mcp`.
4. In Codex/Claude/Cursor, trigger a tool such as `get_session_info`.

## MCP tool highlights

- Routing / I-O: `set_track_io`, `set_track_monitor`, `set_track_arm`, `set_track_solo`, `set_track_mute`, `set_send_level`, `create_return_track`, `delete_return_track`, `set_return_track_name`
- Tracks / scenes: `create_midi_track`, `create_audio_track`, `delete_track`, `duplicate_track`, `set_track_name`, `create_scene`, `delete_scene`, `duplicate_scene`, `fire_scene`, `stop_scene`
- Clips: `create_clip`, `delete_clip`, `duplicate_clip`, `set_clip_name`, `set_clip_loop`, `set_clip_length`, `quantize_clip`, `fire_clip`, `stop_clip`
- Devices: `load_device`, `load_device_by_name` (supports category + optional path), `set_device_parameter` (accepts numbers, `%`, `-12 dB`, `min/max`), `get_device_parameters`, `save_device_preset`, `load_device_preset`, `set_device_sidechain_source`, `load_sidechain_helper`
- Browser: `list_loadable_devices`, `search_loadable_devices`, `get_browser_tree`, `get_browser_items_at_path`
- Patterns: `add_basic_drum_pattern`, `add_chord_stack`
- Transport: `start_playback`, `stop_playback`, `set_tempo`, `set_time_signature`

Example prompts:
- “Route track 2 input to Ext. In 1/2, set monitor to In, and arm it.”
- “Duplicate clip 0 from track 0 into track 1 slot 2 and quantize to 1/16th.”
- “Save a preset of track 3 device 0 as ‘bass-glue’ and reload it on track 5.”

## Parameter normalization, presets, and safety

- Parameter writes accept numbers or strings: `-20 dB`, `75%`, `min`, `max`, or value item names for quantized lists. Values are clamped to each parameter’s min/max and rounded if quantized.
- Use `get_device_parameters` to see ranges, units, and value items before writing.
- `save_device_preset`/`load_device_preset` persist snapshots to `presets/*.json` (override with `ABLETON_MCP_PRESET_DIR`).
- Clip quantization operates on MIDI notes only; audio clips are left untouched.

## Known limitations

- Sidechain routing relies on device parameters named like "Audio From"; if they are hidden, use `load_sidechain_helper` to drop the bundled Max device or set the source once manually in the UI.
- MPE/probability note data is written when Live exposes `set_notes_extended`; on older Live builds those extra attributes are ignored.
- Audio clip duplication is not automatic (MIDI clips copy notes; audio clips duplicate length only).
- Routing option names come from Live and vary by interface/driver; use `get_track_info`/`set_track_io` output to see available strings.
- Tested against Ableton Live 11.x on Windows; older versions may expose fewer routing parameters.
## Happy Path (Windows + Codex)

1. Copy `AbletonMCP_Remote_Script\__init__.py` into `C:\Users\<you>\AppData\Roaming\Ableton\Live XX\Preferences\User Remote Scripts\AbletonMCP`.
2. In Ableton: Preferences > Link, Tempo & MIDI > Control Surface = **AbletonMCP**, Input/Output = **None**.
3. Run the doctor: `powershell -ExecutionPolicy Bypass -File scripts/doctor.ps1`.
4. Start the MCP server: `uvx --from "C:\path\to\ableton-mcp" ableton-mcp`.
5. Reload Codex/Claude so it picks up the command above.
6. Ask Codex/Claude to run `get_session_info`. Success = no connection errors, and track/session JSON is returned.

## Example commands to ask Claude/Codex

- Create an 80s synthwave track
- Create a Metro Boomin style hip-hop beat
- Route track 2 input to Ext. In 1/2, set monitor to In, and arm it
- Create a 4-bar MIDI clip on track 1 slot 0, drop a four-on-the-floor drum pattern, and quantize to 1/16th
- Load Glue Compressor on track 3, sidechain to track 0 kick, and set Threshold to -20 dB
- Save a preset of track 4 device 0 called “bass-glue” and apply it to track 6
- Fire scene 1 and stop it after 4 bars
- List loadable audio effects and load the first Reverb on track 5
- Set the tempo to 120 BPM and time signature to 7/8
- Get information about the current Ableton session

## Validation checklist (manual)

- Browser discovery: `list_loadable_devices` or `search_loadable_devices` returns items and caches `cache/browser_devices.json`.
- Load by name: `load_device_by_name` for a common effect (e.g., Compressor) succeeds without providing a URI.
- Parameter normalization: `set_device_parameter` on a Compressor with `value="-20 dB"` clamps and reports before/after plus min/max.
- Sidechain: `set_device_sidechain_source` targets a device and reports available parameters; if "Audio From" is missing, confirm in UI or load the helper device.
- Routing: `set_track_io`, `set_track_monitor`, and `set_send_level` reflect changes in Ableton and `get_track_info`.
- Clips/scenes: `create_clip`, `add_basic_drum_pattern`, `quantize_clip`, `duplicate_clip`, `fire_clip`, and `fire_scene` all return success.
- Presets: `save_device_preset` then `load_device_preset` applies stored parameter values.

## Troubleshooting

- Use `scripts/doctor.ps1` to check uv/python availability, Remote Script folder, and whether the TCP port is open.
- If the port is closed, ensure Ableton is running and the **AbletonMCP** control surface is selected.
- Check `logs/ableton-mcp.log` for MCP server errors when launched via Codex/Claude.
- Only one MCP server should run at a time; stop any stray instances.

## Technical details

- Commands are sent as JSON objects with a `type` and optional `params`.
- Responses are JSON with a `status` and `result` or `message`.
- TCP socket between MCP server and Ableton Remote Script; STDIO between MCP server and MCP clients.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Disclaimer

This is a third-party integration and not made by Ableton.
