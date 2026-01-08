"""
AbletonMCP Remote Script - Main Entry Point.

This Remote Script enables external control of Ableton Live via the Model
Context Protocol (MCP). It exposes a socket interface that receives JSON
commands and translates them into Live Object Model (LOM) API calls.

Architecture:
    MCP Server (Python) <-> Socket <-> AbletonMCP (ControlSurface)
                                           |
                                           +-> CommandDispatcher
                                                    |
                                                    +-> TrackHandler (tracks, clips, notes)
                                                    +-> SessionHandler (transport, scenes)
                                                    +-> DeviceHandler (browser, parameters)
                                                    +-> DrumRackHandler (drum pads)
                                                    +-> GrooveHandler (groove pool)
                                                    +-> SimplerHandler (sample manipulation)
                                                    +-> ArrangementHandler (timeline, cues)

For Future Agents:
    - This script runs inside Ableton Live's Python environment
    - All state modifications must occur on Live's main thread
    - The socket server runs in a background thread
    - Commands are queued and processed via update() tick
    - Access handlers via self.track_handler, self.session_handler, etc.
    
Installation:
    Copy the AbletonMCP_Remote_Script folder to:
    - macOS: ~/Library/Preferences/Ableton/Live X.X/User Remote Scripts/
    - Windows: \\Users\\<User>\\AppData\\Roaming\\Ableton\\Live X.X\\Preferences\\User Remote Scripts\\

Configuration:
    - Default port: 9877
    - Override via environment: ABLETON_MCP_PORT=9999
    - Host binding: ABLETON_MCP_HOST=localhost
"""
from __future__ import absolute_import, print_function, unicode_literals

from _Framework.ControlSurface import ControlSurface
import os
import socket
import json
import threading
import time
import traceback
from pathlib import Path

# Change queue import for Python 2
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3

from .mcp_socket import AbletonMCPServer
from .interface import CommandDispatcher
from .handlers.track import TrackHandler
from .handlers.session import SessionHandler
from .handlers.device import DeviceHandler
from .handlers.drum_rack import DrumRackHandler
from .handlers.groove import GrooveHandler
from .handlers.simpler import SimplerHandler
from .handlers.arrangement import ArrangementHandler
from .handlers.song import SongHandler
from .handlers.scene import SceneHandler
from .handlers.clip import ClipHandler
from .handlers.clip_slot import ClipSlotHandler
from .handlers.mixer import MixerHandler
from .handlers.application import ApplicationHandler
from .handlers.track_group import TrackGroupHandler
from .handlers.browser import BrowserHandler
from .handlers.conversion import ConversionHandler
from .handlers.specialized import SpecializedDeviceHandler
from .handlers.chain import ChainHandler
from .handlers.sample import SampleHandler

# Constants for socket communication
DEFAULT_PORT = 9877
HOST = os.environ.get("ABLETON_MCP_HOST", "localhost")
try:
    PORT = int(os.environ.get("ABLETON_MCP_PORT", DEFAULT_PORT))
except ValueError:
    PORT = DEFAULT_PORT

def create_instance(c_instance):
    """Create and return the AbletonMCP script instance"""
    return AbletonMCP(c_instance)

class AbletonMCP(ControlSurface):
    """AbletonMCP Remote Script for Ableton Live"""
    
    def __init__(self, c_instance):
        """Initialize the control surface"""
        ControlSurface.__init__(self, c_instance)
        self.log_message("AbletonMCP Remote Script initializing...")
        
        # Initialize handlers (core)
        self.track_handler = TrackHandler(self)
        self.session_handler = SessionHandler(self)
        self.device_handler = DeviceHandler(self)
        
        # Initialize handlers (modular - new)
        self.drum_rack_handler = DrumRackHandler(self)
        self.groove_handler = GrooveHandler(self)
        self.simpler_handler = SimplerHandler(self)
        self.arrangement_handler = ArrangementHandler(self)
        self.song_handler = SongHandler(self)
        self.scene_handler = SceneHandler(self)
        self.clip_handler = ClipHandler(self)
        self.clip_slot_handler = ClipSlotHandler(self)
        self.mixer_handler = MixerHandler(self)
        self.application_handler = ApplicationHandler(self)
        self.track_group_handler = TrackGroupHandler(self)
        self.browser_handler = BrowserHandler(self)
        self.conversion_handler = ConversionHandler(self)
        self.specialized_device_handler = SpecializedDeviceHandler(self)
        self.chain_handler = ChainHandler(self)
        self.sample_handler = SampleHandler(self)
        
        # Command dispatcher
        self.dispatcher = CommandDispatcher(self)
        
        # Socket server
        self.server = AbletonMCPServer(
            port=PORT,
            log_callback=self.log_message,
            command_callback=self._process_command
        )
        self.running = False
        
        # Cache the song reference for easier access
        self._song = self.song()
        
        # Start the socket server
        if self.server.start():
            self.running = True
            self.show_message("AbletonMCP: Listening on port " + str(PORT))
        else:
            self.show_message("AbletonMCP: Failed to start server")
        
        self.log_message("AbletonMCP initialized")
    
    def disconnect(self):
        """Called when Ableton closes or the control surface is removed"""
        self.log_message("AbletonMCP disconnecting...")
        
        if self.server:
            self.server.stop()
        
        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP disconnected")
    
    # Server logic moved to mcp_socket.py
    # Dispatch logic moved to interface.py
    
    def _process_command(self, command):
        """Process a command from the client via the dispatcher"""
        return self.dispatcher.dispatch(command)
    
    # Command implementations
    



    


























    

    
    

    



    


    def _get_device_parameters(self, track_index, device_index):
        """Return metadata for all parameters on a device."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            params = []
            for idx, param in enumerate(device.parameters):
                meta = self._parameter_meta(param)
                meta["index"] = idx
                params.append(meta)
            return {
                "device_name": getattr(device, "name", "Unknown"),
                "parameter_count": len(params),
                "parameters": params
            }
        except Exception as e:
            self.log_message("Error getting device parameters: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _save_device_snapshot(self, track_index, device_index):
        """Capture parameter values for a device."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            snapshot = {}
            for param in device.parameters:
                name = getattr(param, "name", None)
                if name:
                    snapshot[name] = getattr(param, "value", None)
            return {
                "device_name": getattr(device, "name", "Unknown"),
                "track_name": track.name,
                "snapshot": snapshot
            }
        except Exception as e:
            self.log_message("Error saving device snapshot: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _apply_device_snapshot(self, track_index, device_index, snapshot):
        """Apply a snapshot of parameter values to a device."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            if not isinstance(snapshot, dict):
                raise ValueError("Snapshot must be a dict of parameter name -> value")
            applied = []
            for name, target_value in snapshot.items():
                try:
                    param = self._resolve_parameter(device, name)
                    param.value = self._normalize_param_value(param, target_value)
                    applied.append({"parameter": getattr(param, "name", name), "value": param.value})
                except Exception as inner_err:
                    applied.append({"parameter": name, "error": str(inner_err)})
            return {"device_name": getattr(device, "name", "Unknown"), "applied": applied}
        except Exception as e:
            self.log_message("Error applying device snapshot: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _set_device_sidechain_source(self, track_index, device_index, source_track_index, pre_fx=True, mono=True):
        """
        Enable sidechain on a device (e.g., Compressor) and set the source track.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            if source_track_index < 0 or source_track_index >= len(self._song.tracks):
                raise IndexError("Source track index out of range")

            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]
            available_params = [getattr(p, "name", "unknown") for p in device.parameters]
            routing_set = False
            routing_detail = {}

            # Prefer device-level routing if exposed (Compressor, plugins)
            try:
                available_types = getattr(device, "available_input_routing_types", [])
                available_channels = getattr(device, "available_input_routing_channels", [])
                matched_type = self._match_routing_option(available_types, source_track_index if isinstance(source_track_index, str) else None) or \
                               self._match_routing_option(available_types, None if isinstance(source_track_index, str) else "Ext.")
                matched_channel = self._match_routing_option(available_channels, source_track_index if isinstance(source_track_index, str) else source_track_index)
                if matched_type:
                    device.input_routing_type = matched_type
                if matched_channel:
                    device.input_routing_channel = matched_in_channel
                if matched_type or matched_channel:
                    routing_set = True
                    routing_detail = {
                        "type": self._display(getattr(device, "input_routing_type", None)),
                        "channel": self._display(getattr(device, "input_routing_channel", None)),
                        "available_types": [self._display(t) for t in available_types],
                        "available_channels": [self._display(c) for c in available_channels]
                    }
            except Exception:
                pass

            # Toggle sidechain on if available
            sidechain_toggle = self._find_param_by_keywords(device, ["sidechain", "on"]) or \
                               self._find_param_by_keywords(device, ["sidechain"])
            if sidechain_toggle:
                sidechain_toggle.value = 1.0

            source_param = self._find_param_by_keywords(device, ["audio", "from"]) or \
                           self._find_param_by_keywords(device, ["sidechain", "audio"])
            if source_param:
                # Live enumerations are typically 1-based with 0 = None
                source_param.value = source_track_index + 1
                routing_set = True

            mono_param = self._find_param_by_keywords(device, ["mono"])
            if mono_param is not None:
                mono_param.value = 1.0 if mono else 0.0

            prefx_param = self._find_param_by_keywords(device, ["pre", "fx"])
            if prefx_param is not None:
                prefx_param.value = 1.0 if pre_fx else 0.0

            # Best-effort S/C Listen off if present
            listen_param = self._find_param_by_keywords(device, ["s/c", "listen"]) or \
                           self._find_param_by_keywords(device, ["sidechain", "listen"])
            if listen_param is not None:
                try:
                    listen_param.value = 0.0
                except Exception:
                    pass

            return {
                "device_name": getattr(device, "name", "Unknown"),
                "sidechain_enabled": bool(sidechain_toggle),
                "source_track_index": source_track_index if routing_set else None,
                "mono_set": bool(mono_param),
                "pre_fx_set": bool(prefx_param),
                "routing_set": routing_set,
                "routing_detail": routing_detail,
                "routing_message": None if routing_set else "Sidechain routing not exposed on this device; routing not set",
                "available_parameters": available_params
            }
        except Exception as e:
            self.log_message("Error setting device sidechain source: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _display(self, item):
        """Unified display helper for routing options."""
        if item is None:
            return None
        return getattr(item, "display_name", None) or getattr(item, "name", None) or str(item)

    def _set_device_audio_input(self, track_index, device_index, input_type=None, input_channel=None):
        """Set a device's audio input routing (useful for plugin sidechain inputs)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]

            routing_applied = False
            detail = None

            # Prefer DeviceIO endpoints when present (DeviceIOClass from Live API)
            io_endpoints = getattr(device, "input_routings", None)
            if io_endpoints:
                try:
                    for io in io_endpoints:
                        available_types = getattr(io, "available_routing_types", [])
                        available_channels = getattr(io, "available_routing_channels", [])
                        matched_type = self._match_routing_option(available_types, input_type)
                        matched_channel = self._match_routing_option(available_channels, input_channel)
                        if matched_type:
                            io.routing_type = matched_type
                        if matched_channel:
                            io.routing_channel = matched_channel
                        if matched_type or matched_channel:
                            routing_applied = True
                            detail = {
                                "type": self._display(matched_type) if matched_type else self._display(getattr(io, "routing_type", None)),
                                "channel": self._display(matched_channel) if matched_channel else self._display(getattr(io, "routing_channel", None)),
                                "available_types": [self._display(t) for t in available_types],
                                "available_channels": [self._display(c) for c in available_channels]
                            }
                            break
                except Exception as io_err:
                    detail = {"error": str(io_err)}

            # Fallback to device-level routing properties
            if not routing_applied:
                available_types = getattr(device, "available_input_routing_types", [])
                available_channels = getattr(device, "available_input_routing_channels", [])
                matched_type = self._match_routing_option(available_types, input_type)
                matched_channel = self._match_routing_option(available_channels, input_channel)
                if matched_type:
                    device.input_routing_type = matched_type
                if matched_channel:
                    device.input_routing_channel = matched_channel
                if matched_type or matched_channel:
                    routing_applied = True
                detail = {
                    "type": self._display(matched_type) if matched_type else self._display(getattr(device, "input_routing_type", None)),
                    "channel": self._display(matched_channel) if matched_channel else self._display(getattr(device, "input_routing_channel", None)),
                    "available_types": [self._display(t) for t in available_types],
                    "available_channels": [self._display(c) for c in available_channels]
                }

            return {
                "device_name": getattr(device, "name", "Unknown"),
                "routing_applied": routing_applied,
                "detail": detail,
                "message": None if routing_applied else "Device did not expose routable inputs; no routing applied"
            }
        except Exception as e:
            self.log_message("Error setting device audio input: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _describe_device_routing(self, device):
        """Return available input routing options for a device."""
        try:
            available_types = []
            available_channels = []
            try:
                available_types = getattr(device, "available_input_routing_types", []) or []
                available_channels = getattr(device, "available_input_routing_channels", []) or []
            except Exception:
                available_types = []
                available_channels = []
            return {
                "device_name": getattr(device, "name", "Unknown"),
                "available_types": [self._display(t) for t in available_types],
                "available_channels": [self._display(c) for c in available_channels]
            }
        except Exception as e:
            self.log_message("Error describing device routing: {0}".format(str(e)))
            return {"error": str(e)}

    def _list_routable_devices(self):
        """List devices in the set that expose input routing types/channels."""
        try:
            routable = []
            for t_idx, track in enumerate(self._song.tracks):
                for d_idx, device in enumerate(track.devices):
                    info = self._describe_device_routing(device)
                    if info.get("available_types") or info.get("available_channels"):
                        info.update({"track_index": t_idx, "device_index": d_idx, "track_name": track.name})
                        routable.append(info)
            return {"routable_devices": routable}
        except Exception as e:
            self.log_message("Error listing routable devices: {0}".format(str(e)))
            raise

    def _ensure_clip(self, track_index, clip_index, length):
        """Create a clip if missing and return the clip reference."""
        track = self._song.tracks[track_index]
        if clip_index < 0 or clip_index >= len(track.clip_slots):
            raise IndexError("Clip index out of range")
        slot = track.clip_slots[clip_index]
        if not slot.has_clip:
            slot.create_clip(length)
        return slot.clip

    def _add_basic_drum_pattern(self, track_index, clip_index, length=4.0, velocity=100, style="four_on_floor"):
        """Write a simple drum pattern to a clip."""
        try:
            clip = self._ensure_clip(track_index, clip_index, length)
            style_lower = (style or "").lower()
            notes = []
            bars = int(length)
            for bar in range(bars):
                base = bar * 1.0
                if style_lower == "trap":
                    notes.append((36, base, 0.2, velocity, False))
                    notes.append((36, base + 0.75, 0.2, velocity - 10, False))
                    notes.append((38, base + 0.5, 0.2, velocity + 5, False))
                    for step in range(8):
                        notes.append((42, base + step * 0.125, 0.1, velocity - 20, False))
                    notes.append((42, base + 0.48, 0.05, velocity - 25, False))
                    notes.append((42, base + 0.52, 0.05, velocity - 25, False))
                else:
                    for beat in range(4):
                        notes.append((36, base + beat * 0.25, 0.2, velocity, False))
                    notes.append((38, base + 0.5, 0.2, velocity + 5, False))
                    notes.append((38, base + 1.5, 0.2, velocity + 5, False))
                    for step in range(8):
                        notes.append((42, base + step * 0.125, 0.1, velocity - 20, False))
            self._write_clip_notes(clip, notes, replace=True)
            clip.deselect_all_notes()
            return {"note_count": len(notes), "style": style_lower}
        except Exception as e:
            self.log_message("Error adding drum pattern: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _add_chord_stack(self, track_index, clip_index, root_midi=60, quality="major", bars=4, chord_length=1.0):
        """Write a repeating chord stack into a clip."""
        try:
            clip = self._ensure_clip(track_index, clip_index, float(bars))
            quality_map = {
                "major": [0, 4, 7],
                "minor": [0, 3, 7],
                "sus2": [0, 2, 7],
                "sus4": [0, 5, 7],
                "7": [0, 4, 7, 10],
                "maj7": [0, 4, 7, 11],
                "min7": [0, 3, 7, 10]
            }
            intervals = quality_map.get((quality or "major").lower(), quality_map["major"])
            notes = []
            for bar in range(int(bars)):
                start = float(bar)
                for interval in intervals:
                    notes.append((root_midi + interval, start, chord_length, 100, False))
            self._write_clip_notes(clip, notes, replace=True)
            clip.deselect_all_notes()
            return {"note_count": len(notes), "quality": quality}
        except Exception as e:
            self.log_message("Error adding chord stack: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _set_clip_envelope(self, track_index, clip_index, device_index, parameter_name, points):
        """Set automation envelope for a device parameter on a clip."""
        try:
            # Resolve Clip
            track = self._song.tracks[track_index]
            # Ensure clip exists? Or fail? The tool 'apply_automation' should ensure clip via 'add_notes' or similar first?
            # We'll use _ensure_clip logic with default length 4 if missing
            clip = self._ensure_clip(track_index, clip_index, 4.0)
            
            # Resolve Device/Param
            if device_index < 0 or device_index >= len(track.devices):
                 raise IndexError("Device index out of range")
            device = track.devices[device_index]
            param = self._resolve_parameter(device, parameter_name)
            
            # Helper to clear existing envelope?
            # clip.clear_envelope(param) ?
            
            # Set Envelope
            # Points format: [(time, value), ...]
            # Note: Live expects values normalized 0.0-1.0 usually? Or real values? 
            # DeviceParameter.value is 0.0-1.0 usually? NO. value is range-dependent (e.g. Hz).
            # But envelopes in Clip View?
            # Usually automation is normalized? Or not?
            # LOM `DeviceParameter` `value` is raw.
            # `min` and `max` properties exist.
            # `clip.set_envelope` usually expects values in valid range.
            # Let's assume input `points` contains valid values for the parameter.
            
            safe_points = []
            for p in points:
                safe_points.append(tuple([float(p[0]), float(p[1])]))
                
            # Sort by time
            safe_points.sort(key=lambda x: x[0])
            
            # Create Tuple for LOM
            points_tuple = tuple(safe_points)
            
            # API Call (Live 11)
            # Check if supported
            if not hasattr(clip, "set_envelope"):
                 # Legacy or fail
                 pass 
                 # Actually `set_envelope` might not exist on `Live.Clip.Clip` directly in older versions.
                 # But in LOM 11 it does.
                 
            clip.set_envelope(param, points_tuple)
            
            return {
                "status": "success", 
                "parameter": param.name, 
                "points_count": len(points_tuple)
            }
        except Exception as e:
            self.log_message("Error setting clip envelope: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _search_browser_category(self, root_item, query, max_items=200, max_depth=10):
        """Breadth-first search for loadable items matching query."""
        results = []
        if not root_item: return results
        queue_items = [(root_item, getattr(root_item, "name", ""), 0)]
        query_lower = query.lower()
        
        while queue_items and len(results) < max_items:
            current, path, depth = queue_items.pop(0)
            c_name = getattr(current, "name", "Unknown")
            
            # Check match
            if hasattr(current, "is_loadable") and current.is_loadable:
                if query_lower in c_name.lower():
                    results.append({
                        "name": c_name,
                        "uri": getattr(current, "uri", None),
                        "path": path,
                        "is_device": getattr(current, "is_device", False)
                    })
            
            if depth < max_depth and hasattr(current, "children"):
                children = getattr(current, "children", [])
                for child in children:
                    c_path = path + "/" + getattr(child, "name", "") if path else getattr(child, "name", "")
                    queue_items.append((child, c_path, depth + 1))
        return results

    def _search_loadable_devices(self, query, category="all", max_items=200):
        """Search for devices matching query."""
        try:
            app = self.application()
            if not app or not hasattr(app, "browser") or app.browser is None:
                raise RuntimeError("Browser is not available")

            categories = []
            if category == "all":
                categories = [
                    ("instruments", getattr(app.browser, "instruments", None)),
                    ("sounds", getattr(app.browser, "sounds", None)),
                    ("drums", getattr(app.browser, "drums", None)),
                    ("audio_effects", getattr(app.browser, "audio_effects", None)),
                    ("midi_effects", getattr(app.browser, "midi_effects", None)),
                    ("packs", getattr(app.browser, "packs", None)),
                    ("user_library", getattr(app.browser, "user_library", None))
                ]
            else:
                cat_obj = getattr(app.browser, category, None)
                categories = [(category, cat_obj)]

            results = []
            for cat_name, cat_item in categories:
                if not cat_item: continue
                items = self._search_browser_category(cat_item, query, max_items=max_items)
                for item in items:
                    item["category"] = cat_name
                results.extend(items)
                if len(results) >= max_items:
                    break
            
            return {
                "count": len(results),
                "items": results[:max_items]
            }
        except Exception as e:
            self.log_message("Error searching loadable devices: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    
    def _get_clip_notes(self, track_index, clip_index):
        """Get all notes from a clip."""
        try:
            clip = self._ensure_clip(track_index, clip_index)
            # Live 11 API: calls get_notes(start_time, time_span, start_pitch, pitch_span)
            # We want ALL notes. Clip length is needed.
            length = clip.length
            # Grab all notes
            notes = clip.get_notes(0, 100000, 0, 128)
            # Convert to dict list
            result = []
            for n in notes:
                result.append({
                    "pitch": n.pitch,
                    "start_time": n.start_time,
                    "duration": n.duration,
                    "velocity": n.velocity,
                    "mute": n.mute
                })
            return result
        except Exception as e:
            self.log_message("Error getting clip notes: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _find_browser_item_by_uri(self, browser_or_item, uri, max_depth=10, current_depth=0):
        """Find a browser item by its URI"""
        try:
            # Check if this is the item we're looking for
            if hasattr(browser_or_item, 'uri') and browser_or_item.uri == uri:
                return browser_or_item
            
            # Stop recursion if we've reached max depth
            if current_depth >= max_depth:
                return None
            
            # Check if this is a browser with root categories
            if hasattr(browser_or_item, 'instruments'):
                # Check all main categories (include optional ones when available)
                categories = [
                    browser_or_item.instruments,
                    browser_or_item.sounds,
                    browser_or_item.drums,
                    browser_or_item.audio_effects,
                    browser_or_item.midi_effects
                ]
                optional = [
                    getattr(browser_or_item, 'max_for_live', None),
                    getattr(browser_or_item, 'plug_ins', None),
                    getattr(browser_or_item, 'plugins', None),
                    getattr(browser_or_item, 'packs', None),
                    getattr(browser_or_item, 'samples', None),
                    getattr(browser_or_item, 'clips', None),
                    getattr(browser_or_item, 'user_library', None),
                    getattr(browser_or_item, 'current_project', None),
                ]
                categories.extend([c for c in optional if c])
                
                for category in categories:
                    item = self._find_browser_item_by_uri(category, uri, max_depth, current_depth + 1)
                    if item:
                        return item
            
            # Check if this item has children
            if hasattr(browser_or_item, 'children') and browser_or_item.children:
                for child in browser_or_item.children:
                    item = self._find_browser_item_by_uri(child, uri, max_depth, current_depth + 1)
                    if item:
                        return item
            
            return None
        except Exception as e:
            self.log_message("Error finding browser item by URI: {0}".format(str(e)))
            return None

    def _find_sample_uri_by_stem(self, stem):
        """Best-effort lookup for a sample URI in the root Samples category by stem."""
        try:
            items = self.get_browser_items_at_path("Samples")
            if isinstance(items, dict):
                for it in items.get("items", []):
                    if not it.get("is_loadable", False):
                        continue
                    name_lower = str(it.get("name", "")).lower()
                    if name_lower == stem or name_lower == f"{stem}.wav" or name_lower == f"{stem}.aif" or name_lower == f"{stem}.aiff":
                        return it.get("uri")
        except Exception:
            pass
        return None

    def _hotswap_device_with_uri(self, device, target_uri):
        """Set hotswap target and load a browser item by URI."""
        if not target_uri:
            return False
        try:
            app = self.application()
            if not app or not hasattr(app, "browser"):
                return False
            try:
                app.browser.hotswap_target = device
            except Exception:
                pass
            item = self._find_browser_item_by_uri(app.browser, target_uri)
            if item:
                app.browser.load_item(item)
                return True
            return False
        except Exception:
            return False
    
    # Helper methods
    def _find_param_by_keywords(self, device, keywords):
        """
        Search for a parameter on a device that matches all provided keywords in its name.
        """
        if not device or not hasattr(device, 'parameters'):
            return None
        
        keywords = [k.lower() for k in keywords]
        for param in device.parameters:
            name_lower = getattr(param, 'name', '').lower()
            if all(k in name_lower for k in keywords):
                return param
        return None
    

    
    def get_browser_tree(self, category_type="all"):
        """
        Get a simplified tree of browser categories.
        
        Args:
            category_type: Type of categories to get ('all', 'instruments', 'sounds', etc.)
            
        Returns:
            Dictionary with the browser tree structure
        """
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")
                
            # Check if browser is available
            if not hasattr(app, 'browser') or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")
            
            # Log available browser attributes to help diagnose issues
            browser_attrs = [attr for attr in dir(app.browser) if not attr.startswith('_')]
            self.log_message("Available browser attributes: {0}".format(browser_attrs))
            
            result = {
                "type": category_type,
                "categories": [],
                "available_categories": browser_attrs
            }
            
            # Helper function to process a browser item and its children
            def process_item(item, depth=0):
                if not item:
                    return None
                
                result = {
                    "name": item.name if hasattr(item, 'name') else "Unknown",
                    "is_folder": hasattr(item, 'children') and bool(item.children),
                    "is_device": hasattr(item, 'is_device') and item.is_device,
                    "is_loadable": hasattr(item, 'is_loadable') and item.is_loadable,
                    "uri": item.uri if hasattr(item, 'uri') else None,
                    "children": []
                }
                
                
                return result
            
            # Process based on category type and available attributes
            if (category_type == "all" or category_type == "instruments") and hasattr(app.browser, 'instruments'):
                try:
                    instruments = process_item(app.browser.instruments)
                    if instruments:
                        instruments["name"] = "Instruments"  # Ensure consistent naming
                        result["categories"].append(instruments)
                except Exception as e:
                    self.log_message("Error processing instruments: {0}".format(str(e)))
            
            if (category_type == "all" or category_type == "sounds") and hasattr(app.browser, 'sounds'):
                try:
                    sounds = process_item(app.browser.sounds)
                    if sounds:
                        sounds["name"] = "Sounds"  # Ensure consistent naming
                        result["categories"].append(sounds)
                except Exception as e:
                    self.log_message("Error processing sounds: {0}".format(str(e)))
            
            if (category_type == "all" or category_type == "drums") and hasattr(app.browser, 'drums'):
                try:
                    drums = process_item(app.browser.drums)
                    if drums:
                        drums["name"] = "Drums"  # Ensure consistent naming
                        result["categories"].append(drums)
                except Exception as e:
                    self.log_message("Error processing drums: {0}".format(str(e)))
            
            if (category_type == "all" or category_type == "audio_effects") and hasattr(app.browser, 'audio_effects'):
                try:
                    audio_effects = process_item(app.browser.audio_effects)
                    if audio_effects:
                        audio_effects["name"] = "Audio Effects"  # Ensure consistent naming
                        result["categories"].append(audio_effects)
                except Exception as e:
                    self.log_message("Error processing audio_effects: {0}".format(str(e)))
            
            if (category_type == "all" or category_type == "midi_effects") and hasattr(app.browser, 'midi_effects'):
                try:
                    midi_effects = process_item(app.browser.midi_effects)
                    if midi_effects:
                        midi_effects["name"] = "MIDI Effects"
                        result["categories"].append(midi_effects)
                except Exception as e:
                    self.log_message("Error processing midi_effects: {0}".format(str(e)))
            
            # Try to process other potentially available categories
            for attr in browser_attrs:
                if attr not in ['instruments', 'sounds', 'drums', 'audio_effects', 'midi_effects'] and \
                   (category_type == "all" or category_type == attr):
                    try:
                        item = getattr(app.browser, attr)
                        if hasattr(item, 'children') or hasattr(item, 'name'):
                            category = process_item(item)
                            if category:
                                category["name"] = attr.capitalize()
                                result["categories"].append(category)
                    except Exception as e:
                        self.log_message("Error processing {0}: {1}".format(attr, str(e)))
            
            self.log_message("Browser tree generated for {0} with {1} root categories".format(
                category_type, len(result['categories'])))
            return result
            
        except Exception as e:
            self.log_message("Error getting browser tree: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise
    
    def get_browser_items_at_path(self, path):
        """
        Get browser items at a specific path.
        
        Args:
            path: Path in the format "category/folder/subfolder"
                 where category is one of: instruments, sounds, drums, audio_effects, midi_effects
                 or any other available browser category
                 
        Returns:
            Dictionary with items at the specified path
        """
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")
                
            # Check if browser is available
            if not hasattr(app, 'browser') or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")
            
            # Log available browser attributes to help diagnose issues
            browser_attrs = [attr for attr in dir(app.browser) if not attr.startswith('_')]
            self.log_message("Available browser attributes: {0}".format(browser_attrs))
                
            # Parse the path
            path_parts = path.split("/")
            if not path_parts:
                raise ValueError("Invalid path")
            
            # Determine the root category
            root_category = path_parts[0].lower()
            current_item = None
            
            # Check standard categories first
            if root_category == "instruments" and hasattr(app.browser, 'instruments'):
                current_item = app.browser.instruments
            elif root_category == "sounds" and hasattr(app.browser, 'sounds'):
                current_item = app.browser.sounds
            elif root_category == "drums" and hasattr(app.browser, 'drums'):
                current_item = app.browser.drums
            elif root_category == "audio_effects" and hasattr(app.browser, 'audio_effects'):
                current_item = app.browser.audio_effects
            elif root_category == "midi_effects" and hasattr(app.browser, 'midi_effects'):
                current_item = app.browser.midi_effects
            else:
                # Try to find the category in other browser attributes
                found = False
                for attr in browser_attrs:
                    if attr.lower() == root_category:
                        try:
                            current_item = getattr(app.browser, attr)
                            found = True
                            break
                        except Exception as e:
                            self.log_message("Error accessing browser attribute {0}: {1}".format(attr, str(e)))
                
                if not found:
                    # If we still haven't found the category, return available categories
                    return {
                        "path": path,
                        "error": "Unknown or unavailable category: {0}".format(root_category),
                        "available_categories": browser_attrs,
                        "items": []
                    }
            
            # Navigate through the path
            for i in range(1, len(path_parts)):
                part = path_parts[i]
                if not part:  # Skip empty parts
                    continue
                
                if not hasattr(current_item, 'children'):
                    return {
                        "path": path,
                        "error": "Item at '{0}' has no children".format('/'.join(path_parts[:i])),
                        "items": []
                    }
                
                found = False
                for child in current_item.children:
                    if hasattr(child, 'name') and child.name.lower() == part.lower():
                        current_item = child
                        found = True
                        break
                
                if not found:
                    return {
                        "path": path,
                        "error": "Path part '{0}' not found".format(part),
                        "items": []
                    }
            
            # Get items at the current path
            items = []
            if hasattr(current_item, 'children'):
                for child in current_item.children:
                    item_info = {
                        "name": child.name if hasattr(child, 'name') else "Unknown",
                        "is_folder": hasattr(child, 'children') and bool(child.children),
                        "is_device": hasattr(child, 'is_device') and child.is_device,
                        "is_loadable": hasattr(child, 'is_loadable') and child.is_loadable,
                        "uri": child.uri if hasattr(child, 'uri') else None
                    }
                    items.append(item_info)
            
            result = {
                "path": path,
                "name": current_item.name if hasattr(current_item, 'name') else "Unknown",
                "uri": current_item.uri if hasattr(current_item, 'uri') else None,
                "is_folder": hasattr(current_item, 'children') and bool(current_item.children),
                "is_device": hasattr(current_item, 'is_device') and current_item.is_device,
                "is_loadable": hasattr(current_item, 'is_loadable') and current_item.is_loadable,
                "items": items
            }
            
            self.log_message("Retrieved {0} items at path: {1}".format(len(items), path))
            return result
            
        except Exception as e:
            self.log_message("Error getting browser items at path: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _get_session_info(self):
        """Get general session information"""
        self.log_message("Requesting session info")
        song = self.song()
        return {
            "track_count": len(song.tracks),
            "return_track_count": len(song.return_tracks),
            "scenes_count": len(song.scenes),
            "tempo": song.tempo,
            "signature_numerator": song.signature_numerator,
            "signature_denominator": song.signature_denominator,
            "is_playing": song.is_playing,
            "current_song_time": song.current_song_time
        }
