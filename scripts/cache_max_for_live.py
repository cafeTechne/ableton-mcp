import json
import os
import socket
import time
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[1]

try:
    HOST = os.environ.get("ABLETON_MCP_HOST", "localhost")
    PORT = int(os.environ.get("ABLETON_MCP_PORT", "9877"))
except ValueError:
    HOST, PORT = "localhost", 9877

TRACK_INDEX = 6
SLEEP_SECONDS = 0.02

TARGET_CATEGORIES: Tuple[Tuple[str, str], ...] = (
    ("Max Audio Effect", "Max_Audio_Effect"),
    ("Max MIDI Effect", "Max_MIDI_Effect"),
    # Add ("Max Instrument", "Max_Instrument") if we want instruments again.
)

# Allowlist of device names to cache per subfolder; empty list means allow all.
ALLOWLIST: Dict[str, List[str]] = {
    "Max_Audio_Effect": [
        "Sidechain Modulator",
        "OSC Monitor",
        "OSC Send",
        "OSC TouchOSC",
        "JSON Video",
        "JSON Weather",
    ],
    "Max_MIDI_Effect": [
        "MPE",
        "MPE Note Off",
        "OSC Leap Motion",
        "OSC MIDI Send",
    ],
    # "Max_Instrument": [],
}

_ABLETON_CONNECTION = None


class AbletonConnection:
    """Minimal socket client for the AbletonMCP Remote Script."""

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock: Optional[socket.socket] = None

    def connect(self) -> None:
        if self.sock:
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def _receive_full(self, timeout: float) -> bytes:
        if not self.sock:
            raise ConnectionError("Socket is not connected")
        chunks: List[bytes] = []
        self.sock.settimeout(timeout)

        while True:
            chunk = self.sock.recv(8192)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                data = b"".join(chunks)
                json.loads(data.decode("utf-8"))
                return data
            except json.JSONDecodeError:
                continue

        if not chunks:
            raise RuntimeError("No data received from Ableton")
        data = b"".join(chunks)
        json.loads(data.decode("utf-8"))
        return data

    def send_command(self, command_type: str, params: Optional[dict] = None) -> dict:
        if not self.sock:
            self.connect()

        is_modifying = command_type in {
            "create_midi_track",
            "create_audio_track",
            "set_track_name",
            "delete_track",
            "duplicate_track",
            "set_track_io",
            "set_track_monitor",
            "set_track_arm",
            "set_track_solo",
            "set_track_mute",
            "set_track_volume",
            "set_track_panning",
            "set_send_level",
            "create_return_track",
            "delete_return_track",
            "set_return_track_name",
            "create_clip",
            "delete_clip",
            "duplicate_clip",
            "add_notes_to_clip",
            "set_clip_name",
            "set_clip_loop",
            "set_clip_length",
            "quantize_clip",
            "set_tempo",
            "set_time_signature",
            "fire_clip",
            "stop_clip",
            "set_device_parameter",
            "get_device_parameters",
            "start_playback",
            "stop_playback",
            "load_instrument_or_effect",
            "load_device",
            "set_device_sidechain_source",
            "save_device_snapshot",
            "apply_device_snapshot",
            "create_scene",
            "delete_scene",
            "duplicate_scene",
            "fire_scene",
            "stop_scene",
        }

        payload = {"type": command_type, "params": params or {}}
        self.sock.sendall(json.dumps(payload).encode("utf-8"))
        if is_modifying:
            time.sleep(0.1)

        response_data = self._receive_full(30.0 if is_modifying else 12.0)
        response = json.loads(response_data.decode("utf-8"))
        if response.get("status") == "error":
            raise RuntimeError(response.get("message", "Unknown error from Ableton"))

        if is_modifying:
            time.sleep(0.1)

        return response.get("result", {})


def get_ableton_connection() -> AbletonConnection:
    global _ABLETON_CONNECTION
    if _ABLETON_CONNECTION is None:
        _ABLETON_CONNECTION = AbletonConnection(HOST, PORT)
    return _ABLETON_CONNECTION


def _slug_filename(name: str, existing: Iterable[Path]) -> str:
    """Filesystem-safe version of the preset name (keeps dots for clarity) with de-dupe."""
    safe_chars: List[str] = []
    for ch in name:
        if ch.isalnum() or ch in ("-", "_", "."):
            safe_chars.append(ch)
        elif ch.isspace():
            safe_chars.append("_")
        else:
            safe_chars.append("_")
    base = "".join(safe_chars).strip("_") or "preset"
    candidate = base
    suffix = 2
    existing_names = {p.stem for p in existing}
    while candidate in existing_names:
        candidate = f"{base}_{suffix}"
        suffix += 1
    return candidate


def _sanitize_segment(text: str) -> str:
    return "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in text).strip("_") or "_"


def _gather_items(ableton: AbletonConnection, path: str, base_subfolder: str) -> List[Dict[str, str]]:
    """Recursively gather all loadable browser items under a path."""
    stack = [(path, base_subfolder)]
    seen_uris = set()
    loadables: List[Dict[str, str]] = []

    while stack:
        current_path, current_subfolder = stack.pop()
        resp = ableton.send_command("get_browser_items_at_path", {"path": current_path})
        items = resp.get("items", [])
        for item in items:
            uri = item.get("uri")
            name = item.get("name", "unknown")
            is_folder = item.get("is_folder", False)
            is_loadable = item.get("is_loadable", False)

            subfolder = current_subfolder
            if is_folder:
                subfolder = f"{current_subfolder}/{_sanitize_segment(name)}"
                stack.append((f"{current_path}/{name}", subfolder))

            if is_loadable and uri and uri not in seen_uris:
                seen_uris.add(uri)
                loadables.append(
                    {
                        "name": name,
                        "uri": uri,
                        "path_subfolder": subfolder,
                    }
                )
    return loadables


def _cache_items(ableton: AbletonConnection, items: List[Dict[str, str]]) -> Tuple[List[Tuple[str, str]], List[Path]]:
    """Load each item, pull parameters, and write to disk."""
    failures: List[Tuple[str, str]] = []
    written: List[Path] = []

    for item in items:
        name = item.get("name", "unknown")
        uri = item.get("uri")
        path_subfolder = item.get("path_subfolder", "max_for_live")
        out_dir = ROOT / "cache" / "devices" / "max_for_live" / path_subfolder
        out_dir.mkdir(parents=True, exist_ok=True)

        allow_names = ALLOWLIST.get(path_subfolder, [])
        if allow_names and name not in allow_names:
            continue

        if not uri:
            failures.append((name, "missing uri"))
            continue

        print(f"Loading {name} on track {TRACK_INDEX}...")
        try:
            load_resp = ableton.send_command(
                "load_device",
                {"track_index": TRACK_INDEX, "device_uri": uri, "device_slot": -1},
            )
        except Exception as e:
            failures.append((name, f"load error: {e}"))
            continue

        if not load_resp.get("loaded", False):
            failures.append((name, f"load failed: {load_resp}"))
            continue

        device_index = max(load_resp.get("device_count", 1) - 1, 0)
        try:
            params_resp = ableton.send_command(
                "get_device_parameters",
                {"track_index": TRACK_INDEX, "device_index": device_index},
            )
        except Exception as e:
            failures.append((name, f"param fetch error: {e}"))
            continue

        payload = {
            "path_category": "max_for_live",
            "path_subfolder": path_subfolder,
            "name": params_resp.get("device_name", name),
            "uri": uri,
            "parameters": params_resp.get("parameters"),
        }

        filename = f"{_slug_filename(name, out_dir.glob('*.json'))}.json"
        out_path = out_dir / filename
        out_path.write_text(json.dumps(payload, indent=2))
        written.append(out_path)
        time.sleep(SLEEP_SECONDS)

    return failures, written


def cache_all_m4l() -> None:
    ableton = get_ableton_connection()
    all_failures: List[Tuple[str, str]] = []
    all_written: List[Path] = []

    for display, subfolder in TARGET_CATEGORIES:
        root_path = f"Max_for_live/{display}"
        print(f"\nScanning {display}...")
        items = _gather_items(ableton, root_path, subfolder)
        failures, written = _cache_items(ableton, items)
        all_failures.extend(failures)
        all_written.extend(written)

    print("\nDone.")
    print(f"Saved {len(all_written)} files.")
    if all_failures:
        print("Failures:")
        for name, reason in all_failures:
            print(f" - {name}: {reason}")
    else:
        print("No failures.")


if __name__ == "__main__":
    cache_all_m4l()
