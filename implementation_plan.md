## MCP Ableton sidechain/tooling expansion plan

- [x] Add Remote Script commands:
  - `load_device` (track index + device URI, optional slot position)
  - `set_device_parameter` (track/device param by index or name)
  - `set_device_sidechain_source` (enable sidechain, set source track, mono/pre-FX toggles)
- [x] Expose matching MCP tools in `MCP_Server/server.py` and mark as modifying commands.
- [x] Update README with new tool descriptions and example prompts.
- [ ] Add device discovery/search tools + caching so we can load by name without manual URIs.
- [ ] Run validation: doctor script, `get_session_info`, device discovery, load-by-name, and sidechain parameter calls.
