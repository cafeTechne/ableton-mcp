# AbletonMCP/init.py
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
        
        # Socket server for communication
        self.server = None
        self.client_threads = []
        self.server_thread = None
        self.running = False
        
        # Cache the song reference for easier access
        self._song = self.song()
        
        # Start the socket server
        self.start_server()
        
        self.log_message("AbletonMCP initialized")
        
        # Show a message in Ableton
        self.show_message("AbletonMCP: Listening for commands on port " + str(PORT))
    
    def disconnect(self):
        """Called when Ableton closes or the control surface is removed"""
        self.log_message("AbletonMCP disconnecting...")
        self.running = False
        
        # Stop the server
        if self.server:
            try:
                self.server.close()
            except:
                pass
        
        # Wait for the server thread to exit
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(1.0)
            
        # Clean up any client threads
        for client_thread in self.client_threads[:]:
            if client_thread.is_alive():
                # We don't join them as they might be stuck
                self.log_message("Client thread still alive during disconnect")
        
        ControlSurface.disconnect(self)
        self.log_message("AbletonMCP disconnected")
    
    def start_server(self):
        """Start the socket server in a separate thread"""
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server.bind((HOST, PORT))
            self.server.listen(5)  # Allow up to 5 pending connections
            
            self.running = True
            self.server_thread = threading.Thread(target=self._server_thread)
            self.server_thread.daemon = True
            self.server_thread.start()
            
            self.log_message("Server started on port " + str(PORT))
        except Exception as e:
            self.log_message("Error starting server: " + str(e))
            self.show_message("AbletonMCP: Error starting server - " + str(e))
    
    def _server_thread(self):
        """Server thread implementation - handles client connections"""
        try:
            self.log_message("Server thread started")
            # Set a timeout to allow regular checking of running flag
            self.server.settimeout(1.0)
            
            while self.running:
                try:
                    # Accept connections with timeout
                    client, address = self.server.accept()
                    self.log_message("Connection accepted from " + str(address))
                    self.show_message("AbletonMCP: Client connected")
                    
                    # Handle client in a separate thread
                    client_thread = threading.Thread(
                        target=self._handle_client,
                        args=(client,)
                    )
                    client_thread.daemon = True
                    client_thread.start()
                    
                    # Keep track of client threads
                    self.client_threads.append(client_thread)
                    
                    # Clean up finished client threads
                    self.client_threads = [t for t in self.client_threads if t.is_alive()]
                    
                except socket.timeout:
                    # No connection yet, just continue
                    continue
                except Exception as e:
                    if self.running:  # Only log if still running
                        self.log_message("Server accept error: " + str(e))
                    time.sleep(0.5)
            
            self.log_message("Server thread stopped")
        except Exception as e:
            self.log_message("Server thread error: " + str(e))
    
    def _handle_client(self, client):
        """Handle communication with a connected client"""
        self.log_message("Client handler started")
        client.settimeout(None)  # No timeout for client socket
        buffer = ''  # Changed from b'' to '' for Python 2
        
        try:
            while self.running:
                try:
                    # Receive data
                    data = client.recv(8192)
                    
                    if not data:
                        # Client disconnected
                        self.log_message("Client disconnected")
                        break
                    
                    # Accumulate data in buffer with explicit encoding/decoding
                    try:
                        # Python 3: data is bytes, decode to string
                        buffer += data.decode('utf-8')
                    except AttributeError:
                        # Python 2: data is already string
                        buffer += data
                    
                    try:
                        # Try to parse command from buffer
                        command = json.loads(buffer)  # Removed decode('utf-8')
                        buffer = ''  # Clear buffer after successful parse
                        
                        self.log_message("Received command: " + str(command.get("type", "unknown")))
                        
                        # Process the command and get response
                        response = self._process_command(command)
                        
                        # Send the response with explicit encoding
                        try:
                            # Python 3: encode string to bytes
                            client.sendall(json.dumps(response).encode('utf-8'))
                        except AttributeError:
                            # Python 2: string is already bytes
                            client.sendall(json.dumps(response))
                    except ValueError:
                        # Incomplete data, wait for more
                        continue
                        
                except Exception as e:
                    self.log_message("Error handling client data: " + str(e))
                    self.log_message(traceback.format_exc())
                    
                    # Send error response if possible
                    error_response = {
                        "status": "error",
                        "message": str(e)
                    }
                    try:
                        # Python 3: encode string to bytes
                        client.sendall(json.dumps(error_response).encode('utf-8'))
                    except AttributeError:
                        # Python 2: string is already bytes
                        client.sendall(json.dumps(error_response))
                    except:
                        # If we can't send the error, the connection is probably dead
                        break
                    
                    # For serious errors, break the loop
                    if not isinstance(e, ValueError):
                        break
        except Exception as e:
            self.log_message("Error in client handler: " + str(e))
        finally:
            try:
                client.close()
            except:
                pass
            self.log_message("Client handler stopped")
    
    def _process_command(self, command):
        """Process a command from the client and return a response"""
        command_type = command.get("type", "")
        params = command.get("params", {})
        
        # Initialize response
        response = {
            "status": "success",
            "result": {}
        }
        
        try:
            # Commands that modify Live's state should be scheduled on the main thread
            main_thread_commands = {
                "create_midi_track": lambda: self._create_midi_track(params.get("index", -1)),
                "create_audio_track": lambda: self._create_audio_track(params.get("index", -1)),
                "delete_track": lambda: self._delete_track(params.get("track_index", -1)),
                "duplicate_track": lambda: self._duplicate_track(params.get("track_index", -1), params.get("target_index", None)),
                "set_track_name": lambda: self._set_track_name(params.get("track_index", 0), params.get("name", "")),
                "configure_track_routing": lambda: self._configure_track_routing(
                    params.get("track_index", 0),
                    params.get("input_type", None),
                    params.get("input_channel", None),
                    params.get("output_type", None),
                    params.get("output_channel", None),
                    params.get("monitor_state", None),
                    params.get("arm", None),
                    params.get("sends", None)
                ),
                "set_track_io": lambda: self._set_track_io(
                    params.get("track_index", 0),
                    params.get("input_type", None),
                    params.get("input_channel", None),
                    params.get("output_type", None),
                    params.get("output_channel", None)
                ),
                "set_track_monitor": lambda: self._set_track_monitor(params.get("track_index", 0), params.get("state", "auto")),
                "set_track_arm": lambda: self._set_track_bool(params.get("track_index", 0), "arm", params.get("arm", True)),
                "set_track_solo": lambda: self._set_track_bool(params.get("track_index", 0), "solo", params.get("solo", True)),
                "set_track_mute": lambda: self._set_track_bool(params.get("track_index", 0), "mute", params.get("mute", True)),
                "set_track_volume": lambda: self._set_track_volume(params.get("track_index", 0), params.get("volume", 0.0)),
                "set_track_panning": lambda: self._set_track_panning(params.get("track_index", 0), params.get("panning", 0.0)),
                "set_send_level": lambda: self._set_send_level(params.get("track_index", 0), params.get("send_index", 0), params.get("level", 0.0)),
                "create_return_track": lambda: self._create_return_track(params.get("name", None)),
                "delete_return_track": lambda: self._delete_return_track(params.get("index", -1)),
                "set_return_track_name": lambda: self._set_return_track_name(params.get("index", 0), params.get("name", "")),
                "create_clip": lambda: self._create_clip(params.get("track_index", 0), params.get("clip_index", 0), params.get("length", 4.0)),
                "delete_clip": lambda: self._delete_clip(params.get("track_index", 0), params.get("clip_index", 0)),
                "duplicate_clip": lambda: self._duplicate_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("target_track_index", None),
                    params.get("target_clip_index", None)
                ),
                "add_notes_to_clip": lambda: self._add_notes_to_clip(params.get("track_index", 0), params.get("clip_index", 0), params.get("notes", [])),
                "set_clip_name": lambda: self._set_clip_name(params.get("track_index", 0), params.get("clip_index", 0), params.get("name", "")),
                "set_clip_loop": lambda: self._set_clip_loop(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("start", None),
                    params.get("end", None),
                    params.get("loop_on", True)
                ),
                "set_clip_length": lambda: self._set_clip_length(params.get("track_index", 0), params.get("clip_index", 0), params.get("length", None)),
                "quantize_clip": lambda: self._quantize_clip(params.get("track_index", 0), params.get("clip_index", 0), params.get("grid", 16), params.get("amount", 1.0)),
                "set_tempo": lambda: self._set_tempo(params.get("tempo", 120.0)),
                "set_time_signature": lambda: self._set_time_signature(params.get("numerator", 4), params.get("denominator", 4)),
                "fire_clip": lambda: self._fire_clip(params.get("track_index", 0), params.get("clip_index", 0)),
                "list_clips": lambda: self._list_clips(
                    params.get("track_pattern", None),
                    params.get("match_mode", "contains")
                ),
                "fire_clip_by_name": lambda: self._fire_clip_by_name(
                    params.get("clip_pattern", ""),
                    params.get("track_pattern", None),
                    params.get("match_mode", "contains"),
                    params.get("first_only", True)
                ),
                "trigger_test_midi": lambda: self._trigger_test_midi(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("length", 1.0),
                    params.get("pitch", 60),
                    params.get("velocity", 100),
                    params.get("duration", 0.5),
                    params.get("start_time", 0.0),
                    params.get("overwrite_clip", False),
                    params.get("fire_clip", True),
                    params.get("cc_number", None),
                    params.get("cc_value", 64),
                    params.get("channel", 0)
                ),
                "stop_clip": lambda: self._stop_clip(params.get("track_index", 0), params.get("clip_index", 0)),
                "start_playback": lambda: self._start_playback(),
                "stop_playback": lambda: self._stop_playback(),
                "create_scene": lambda: self._create_scene(params.get("index", -1), params.get("name", None)),
                "delete_scene": lambda: self._delete_scene(params.get("index", -1)),
                "duplicate_scene": lambda: self._duplicate_scene(params.get("index", -1)),
                "fire_scene": lambda: self._fire_scene(params.get("index", -1)),
                "fire_scene_by_name": lambda: self._fire_scene_by_name(
                    params.get("pattern", ""),
                    params.get("match_mode", "contains"),
                    params.get("first_only", True)
                ),
                "stop_scene": lambda: self._stop_scene(params.get("index", -1)),
                "load_browser_item": lambda: self._load_browser_item(
                    params.get("track_index", 0),
                    params.get("item_uri", ""),
                    params.get("clip_index", None)
                ),
                "load_simpler_with_sample": lambda: self._load_simpler_with_sample(
                    params.get("track_index", 0),
                    params.get("file_path", ""),
                    params.get("device_slot", -1)
                ),
                "load_sampler_with_sample": lambda: self._load_sampler_with_sample(
                    params.get("track_index", 0),
                    params.get("file_path", ""),
                    params.get("device_slot", -1)
                ),
                "load_device": lambda: self._load_device(params.get("track_index", 0), params.get("device_uri", ""), params.get("device_slot", -1)),
                "set_device_parameter": lambda: self._set_device_parameter(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("parameter", 0),
                    params.get("value", 0.0)
                ),
                "set_device_parameters": lambda: self._set_device_parameters(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("parameters", None)
                ),
                "set_device_audio_input": lambda: self._set_device_audio_input(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("input_type", None),
                    params.get("input_channel", None)
                ),
                "get_device_parameters": lambda: self._get_device_parameters(params.get("track_index", 0), params.get("device_index", 0)),
                "set_device_sidechain_source": lambda: self._set_device_sidechain_source(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("source_track_index", 0),
                    params.get("pre_fx", True),
                    params.get("mono", True)
                ),
                "list_routable_devices": lambda: self._list_routable_devices(),
                "save_device_snapshot": lambda: self._save_device_snapshot(params.get("track_index", 0), params.get("device_index", 0)),
                "save_device_preset": lambda: self._save_device_snapshot(params.get("track_index", 0), params.get("device_index", 0)),
                "apply_device_snapshot": lambda: self._apply_device_snapshot(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("snapshot", {})
                ),
                "add_basic_drum_pattern": lambda: self._add_basic_drum_pattern(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("length", 4.0),
                    params.get("velocity", 100),
                    params.get("style", "four_on_floor")
                ),
                "add_chord_stack": lambda: self._add_chord_stack(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("root_midi", 60),
                    params.get("quality", "major"),
                    params.get("bars", 4),
                    params.get("chord_length", 1.0)
                )
            }

            if command_type == "get_session_info":
                response["result"] = self._get_session_info()
            elif command_type == "get_track_info":
                track_index = params.get("track_index", 0)
                response["result"] = self._get_track_info(track_index)
            elif command_type == "list_clips":
                track_pattern = params.get("track_pattern", None)
                match_mode = params.get("match_mode", "contains")
                response["result"] = self._list_clips(track_pattern, match_mode)
            elif command_type in main_thread_commands:
                # Use a thread-safe approach with a response queue
                response_queue = queue.Queue()

                def main_thread_task():
                    try:
                        result = main_thread_commands[command_type]()
                        response_queue.put({"status": "success", "result": result})
                    except Exception as e:
                        self.log_message("Error in main thread task: " + str(e))
                        self.log_message(traceback.format_exc())
                        response_queue.put({"status": "error", "message": str(e)})

                # Schedule the task to run on the main thread
                try:
                    self.schedule_message(0, main_thread_task)
                except AssertionError:
                    # If we're already on the main thread, execute directly
                    main_thread_task()

                # Wait for the response with a timeout
                try:
                    task_response = response_queue.get(timeout=10.0)
                    if task_response.get("status") == "error":
                        response["status"] = "error"
                        response["message"] = task_response.get("message", "Unknown error")
                    else:
                        response["result"] = task_response.get("result", {})
                except queue.Empty:
                    response["status"] = "error"
                    response["message"] = "Timeout waiting for operation to complete"
            elif command_type == "get_browser_item":
                uri = params.get("uri", None)
                path = params.get("path", None)
                response["result"] = self._get_browser_item(uri, path)
            elif command_type == "get_browser_categories":
                category_type = params.get("category_type", "all")
                response["result"] = self._get_browser_categories(category_type)
            elif command_type == "get_browser_items":
                path = params.get("path", "")
                item_type = params.get("item_type", "all")
                response["result"] = self._get_browser_items(path, item_type)
            # Add the new browser commands
            elif command_type == "get_browser_tree":
                category_type = params.get("category_type", "all")
                response["result"] = self.get_browser_tree(category_type)
            elif command_type == "get_browser_items_at_path":
                path = params.get("path", "")
                response["result"] = self.get_browser_items_at_path(path)
            elif command_type == "list_loadable_devices":
                category = params.get("category", "all")
                max_items = params.get("max_items", 200)
                response["result"] = self.list_loadable_devices(category, max_items)
            elif command_type == "search_loadable_devices":
                query = params.get("query", "")
                category = params.get("category", "all")
                max_items = params.get("max_items", 50)
                response["result"] = self.search_loadable_devices(query, category, max_items)
            else:
                response["status"] = "error"
                response["message"] = "Unknown command: " + command_type
        except Exception as e:
            self.log_message("Error processing command: " + str(e))
            self.log_message(traceback.format_exc())
            response["status"] = "error"
            response["message"] = str(e)
        
        return response
    
    # Command implementations
    
    def _get_session_info(self):
        """Get information about the current session"""
        try:
            result = {
                "tempo": self._song.tempo,
                "signature_numerator": self._song.signature_numerator,
                "signature_denominator": self._song.signature_denominator,
                "track_count": len(self._song.tracks),
                "return_track_count": len(self._song.return_tracks),
                "master_track": {
                    "name": "Master",
                    "volume": self._song.master_track.mixer_device.volume.value,
                    "panning": self._song.master_track.mixer_device.panning.value
                }
            }
            return result
        except Exception as e:
            self.log_message("Error getting session info: " + str(e))
            raise

    def _list_clips(self, track_pattern=None, match_mode="contains"):
        """List all named clips across tracks, optionally filtering by track name."""
        try:
            results = []
            def _match(name, pattern):
                if pattern is None:
                    return True
                name_l = name.lower()
                patt_l = pattern.lower()
                if match_mode == "equals":
                    return name_l == patt_l
                if match_mode == "startswith":
                    return name_l.startswith(patt_l)
                return patt_l in name_l

            for t_idx, track in enumerate(self._song.tracks):
                track_name = getattr(track, "name", f"Track {t_idx}")
                if not _match(track_name, track_pattern):
                    continue
                for c_idx, slot in enumerate(track.clip_slots):
                    try:
                        if slot.has_clip:
                            clip = slot.clip
                            clip_name = getattr(clip, "name", f"Clip {c_idx}")
                            results.append({
                                "track_index": t_idx,
                                "track_name": track_name,
                                "clip_index": c_idx,
                                "clip_name": clip_name,
                                "length": getattr(clip, "length", None)
                            })
                    except Exception as clip_err:
                        self.log_message("Error reading clip at {0}:{1}: {2}".format(t_idx, c_idx, str(clip_err)))
                        continue
            return {"clips": results, "count": len(results)}
        except Exception as e:
            self.log_message("Error listing clips: " + str(e))
            raise
    
    def _get_track_info(self, track_index):
        """Get information about a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            # Get clip slots
            clip_slots = []
            for slot_index, slot in enumerate(track.clip_slots):
                clip_info = None
                if slot.has_clip:
                    clip = slot.clip
                    clip_info = {
                        "name": clip.name,
                        "length": clip.length,
                        "is_playing": clip.is_playing,
                        "is_recording": clip.is_recording
                    }
                
                clip_slots.append({
                    "index": slot_index,
                    "has_clip": slot.has_clip,
                    "clip": clip_info
                })
            
            # Get devices
            devices = []
            for device_index, device in enumerate(track.devices):
                devices.append({
                    "index": device_index,
                    "name": device.name,
                    "class_name": device.class_name,
                    "type": self._get_device_type(device)
                })
            
            send_levels = []
            try:
                return_names = [r.name for r in self._song.return_tracks]
                for idx, send in enumerate(track.mixer_device.sends):
                    send_levels.append({
                        "index": idx,
                        "name": return_names[idx] if idx < len(return_names) else "Send {0}".format(idx),
                        "value": send.value,
                        "min": getattr(send, "min", 0.0),
                        "max": getattr(send, "max", 1.0)
                    })
            except Exception as routing_error:
                self.log_message("Send level introspection failed: {0}".format(str(routing_error)))

            routing_info = self._describe_track_routing(track)

            result = {
                "index": track_index,
                "name": track.name,
                "is_audio_track": track.has_audio_input,
                "is_midi_track": track.has_midi_input,
                "mute": track.mute,
                "solo": track.solo,
                "arm": track.arm,
                "volume": track.mixer_device.volume.value,
                "panning": track.mixer_device.panning.value,
                "clip_slots": clip_slots,
                "devices": devices,
                "routing": routing_info,
                "sends": send_levels
            }
            return result
        except Exception as e:
            self.log_message("Error getting track info: " + str(e))
            raise

    def _describe_track_routing(self, track):
        """Return input/output routing metadata for a track."""
        try:
            input_type = getattr(track, "input_routing_type", None)
            input_channel = getattr(track, "input_routing_channel", None)
            output_type = getattr(track, "output_routing_type", None)
            output_channel = getattr(track, "output_routing_channel", None)
            monitoring_state = getattr(track, "monitoring_state", None)

            def _display(item):
                if item is None:
                    return None
                return getattr(item, "display_name", None) or getattr(item, "name", None) or str(item)

            monitoring_labels = {0: "in", 1: "auto", 2: "off"}
            return {
                "input": {
                    "type": _display(input_type),
                    "channel": _display(input_channel)
                },
                "output": {
                    "type": _display(output_type),
                    "channel": _display(output_channel)
                },
                "monitoring_state": monitoring_labels.get(monitoring_state, monitoring_state)
            }
        except Exception as e:
            self.log_message("Failed to describe track routing: {0}".format(str(e)))
            return {}

    def _match_routing_option(self, options, target):
        """Resolve a routing option by index or name substring."""
        if target is None:
            return None
        if options is None:
            return None

        try:
            if isinstance(target, int):
                return options[target]
        except Exception:
            pass

        try:
            target_lower = str(target).lower()
            for opt in options:
                name = getattr(opt, "display_name", None) or getattr(opt, "name", None) or str(opt)
                if name and target_lower in name.lower():
                    return opt
        except Exception:
            pass
        return None

    def _name_matches(self, name, pattern, match_mode="contains"):
        """Case-insensitive matcher supporting contains/startswith/equals."""
        if pattern is None or pattern == "":
            return True
        try:
            hay = (name or "").lower()
            needle = str(pattern).lower()
            if match_mode == "equals":
                return hay == needle
            if match_mode == "startswith":
                return hay.startswith(needle)
            return needle in hay
        except Exception:
            return False

    def _resolve_send_index(self, track, target):
        """Resolve a send index using numeric index or name substring."""
        try:
            sends = getattr(track.mixer_device, "sends", [])
            if target is None or sends is None:
                return None
            if isinstance(target, int):
                if 0 <= target < len(sends):
                    return target
                return None
            target_lower = str(target).lower()
            for idx, send_param in enumerate(sends):
                name = getattr(send_param, "name", None) or getattr(send_param, "short_name", None) or str(send_param)
                if name and target_lower in name.lower():
                    return idx
            try:
                for idx, return_track in enumerate(getattr(self._song, "return_tracks", [])):
                    name = getattr(return_track, "name", None)
                    if name and target_lower in name.lower():
                        return idx
            except Exception:
                pass
        except Exception:
            pass
        return None

    def _describe_send_levels(self, track):
        """Return current send levels with names for a track."""
        sends = getattr(track.mixer_device, "sends", [])
        send_info = []
        try:
            return_tracks = getattr(self._song, "return_tracks", [])
        except Exception:
            return_tracks = []
        for idx, send_param in enumerate(sends):
            try:
                name = getattr(send_param, "name", None)
                if not name and idx < len(return_tracks):
                    name = getattr(return_tracks[idx], "name", None)
            except Exception:
                name = None
            try:
                value = send_param.value
                send_min = send_param.min
                send_max = send_param.max
            except Exception:
                value = None
                send_min = None
                send_max = None
            send_info.append({
                "index": idx,
                "name": name,
                "value": value,
                "min": send_min,
                "max": send_max
            })
        return send_info

    def _set_multiple_send_levels(self, track_index, send_levels):
        """Apply multiple send levels using flexible payloads."""
        if send_levels is None:
            return {"updated": [], "errors": [], "current": []}
        if track_index < 0 or track_index >= len(self._song.tracks):
            raise IndexError("Track index out of range")
        track = self._song.tracks[track_index]
        sends = getattr(track.mixer_device, "sends", [])
        updates = []
        errors = []

        def _apply_send(idx, level, label):
            if idx is None or idx < 0 or idx >= len(sends):
                errors.append({"target": label, "reason": "send_not_found"})
                return
            try:
                send_param = sends[idx]
                value = float(level)
                clamped = max(send_param.min, min(send_param.max, value))
                send_param.value = clamped
                updates.append({
                    "index": idx,
                    "name": getattr(send_param, "name", None),
                    "value": clamped,
                    "min": send_param.min,
                    "max": send_param.max
                })
            except Exception as e:
                errors.append({"target": label, "reason": str(e)})

        if isinstance(send_levels, dict):
            for key, value in send_levels.items():
                idx = self._resolve_send_index(track, key)
                _apply_send(idx, value, key)
        elif isinstance(send_levels, (list, tuple)):
            for idx, entry in enumerate(send_levels):
                if isinstance(entry, dict):
                    target = entry.get("index", entry.get("send", entry.get("name", None)))
                    level = entry.get("level", entry.get("value", None))
                    resolved_idx = self._resolve_send_index(track, target if target is not None else idx)
                    _apply_send(resolved_idx, level, target if target is not None else idx)
                elif isinstance(entry, (list, tuple)) and len(entry) == 2:
                    resolved_idx = self._resolve_send_index(track, entry[0])
                    _apply_send(resolved_idx, entry[1], entry[0])
                else:
                    _apply_send(idx, entry, idx)
        else:
            errors.append({"target": "payload", "reason": "unsupported_type"})

        return {"updated": updates, "errors": errors, "current": self._describe_send_levels(track)}

    def _configure_track_routing(
        self,
        track_index,
        input_type=None,
        input_channel=None,
        output_type=None,
        output_channel=None,
        monitor_state=None,
        arm=None,
        sends=None
    ):
        """Set I/O, monitoring, arm, and multiple sends in one call."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]

            routing = self._describe_track_routing(track)
            if any(value is not None for value in (input_type, input_channel, output_type, output_channel)):
                routing = self._set_track_io(track_index, input_type, input_channel, output_type, output_channel)

            monitoring_state = routing.get("monitoring_state")
            if monitor_state is not None:
                monitor_result = self._set_track_monitor(track_index, monitor_state)
                monitoring_state = monitor_result.get("monitoring_state")

            arm_state = bool(getattr(track, "arm", False))
            if arm is not None:
                arm_result = self._set_track_bool(track_index, "arm", arm)
                arm_state = arm_result.get("arm", arm_state)

            send_result = {"updated": [], "errors": [], "current": self._describe_send_levels(track)}
            if sends is not None:
                send_result = self._set_multiple_send_levels(track_index, sends)

            return {
                "track_index": track_index,
                "track_name": track.name,
                "routing": routing,
                "monitoring_state": monitoring_state,
                "arm": arm_state,
                "sends": send_result
            }
        except Exception as e:
            self.log_message("Error configuring track routing: " + str(e))
            raise

    def _create_audio_track(self, index):
        """Create a new audio track at the specified index."""
        try:
            self._song.create_audio_track(index)
            new_track_index = len(self._song.tracks) - 1 if index == -1 else index
            new_track = self._song.tracks[new_track_index]
            return {"index": new_track_index, "name": new_track.name}
        except Exception as e:
            self.log_message("Error creating audio track: " + str(e))
            raise

    def _delete_track(self, track_index):
        """Delete a track by index."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track_name = self._song.tracks[track_index].name
            self._song.delete_track(track_index)
            return {"deleted": True, "index": track_index, "name": track_name}
        except Exception as e:
            self.log_message("Error deleting track: " + str(e))
            raise

    def _duplicate_track(self, track_index, target_index=None):
        """Duplicate a track and report the new index."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            self._song.duplicate_track(track_index)
            duplicated_index = track_index + 1
            track = self._song.tracks[duplicated_index]
            result = {"duplicated_from": track_index, "index": duplicated_index, "name": track.name}
            if target_index is not None:
                result["note"] = "Target index move not supported via API; duplicated next to source"
            return result
        except Exception as e:
            self.log_message("Error duplicating track: " + str(e))
            raise

    def _set_track_io(self, track_index, input_type, input_channel, output_type, output_channel):
        """Set track input/output routing values."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]

            # Input routing
            available_in_types = getattr(track, "available_input_routing_types", [])
            available_in_channels = getattr(track, "available_input_routing_channels", [])
            matched_in_type = self._match_routing_option(available_in_types, input_type)
            matched_in_channel = self._match_routing_option(available_in_channels, input_channel)
            if matched_in_type:
                track.input_routing_type = matched_in_type
            if matched_in_channel:
                track.input_routing_channel = matched_in_channel

            # Output routing
            available_out_types = getattr(track, "available_output_routing_types", [])
            available_out_channels = getattr(track, "available_output_routing_channels", [])
            matched_out_type = self._match_routing_option(available_out_types, output_type)
            matched_out_channel = self._match_routing_option(available_out_channels, output_channel)
            if matched_out_type:
                track.output_routing_type = matched_out_type
            if matched_out_channel:
                track.output_routing_channel = matched_out_channel

            routing_info = self._describe_track_routing(track)
            routing_info["available_inputs"] = [getattr(t, "display_name", getattr(t, "name", str(t))) for t in available_in_types]
            routing_info["available_input_channels"] = [getattr(t, "display_name", getattr(t, "name", str(t))) for t in available_in_channels]
            routing_info["available_outputs"] = [getattr(t, "display_name", getattr(t, "name", str(t))) for t in available_out_types]
            routing_info["available_output_channels"] = [getattr(t, "display_name", getattr(t, "name", str(t))) for t in available_out_channels]
            return routing_info
        except Exception as e:
            self.log_message("Error setting track routing: " + str(e))
            raise

    def _set_track_monitor(self, track_index, state):
        """Set monitoring state (in/auto/off)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            state_map = {"in": 0, "auto": 1, "off": 2}
            if isinstance(state, str):
                state_value = state_map.get(state.lower(), None)
            else:
                state_value = state
            if state_value is None:
                raise ValueError("Invalid monitoring state: {0}".format(state))
            track.monitoring_state = state_value
            return {"monitoring_state": self._describe_track_routing(track).get("monitoring_state")}
        except Exception as e:
            self.log_message("Error setting monitoring state: " + str(e))
            raise

    def _set_track_bool(self, track_index, attr_name, value):
        """Set boolean properties like arm/mute/solo."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            setattr(track, attr_name, bool(value))
            return {attr_name: bool(getattr(track, attr_name))}
        except Exception as e:
            self.log_message("Error setting track attribute {0}: {1}".format(attr_name, str(e)))
            raise

    def _set_track_volume(self, track_index, volume):
        """Set mixer volume for a track."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            param = track.mixer_device.volume
            param.value = max(param.min, min(param.max, volume))
            return {"volume": param.value, "min": param.min, "max": param.max}
        except Exception as e:
            self.log_message("Error setting track volume: " + str(e))
            raise

    def _set_track_panning(self, track_index, panning):
        """Set mixer panning for a track."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            param = track.mixer_device.panning
            param.value = max(param.min, min(param.max, panning))
            return {"panning": param.value, "min": param.min, "max": param.max}
        except Exception as e:
            self.log_message("Error setting track panning: " + str(e))
            raise

    def _set_send_level(self, track_index, send_index, level):
        """Adjust send level to a return track."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            sends = track.mixer_device.sends
            if send_index < 0 or send_index >= len(sends):
                raise IndexError("Send index out of range")
            send_param = sends[send_index]
            send_param.value = max(send_param.min, min(send_param.max, level))
            return {
                "send_index": send_index,
                "value": send_param.value,
                "min": send_param.min,
                "max": send_param.max
            }
        except Exception as e:
            self.log_message("Error setting send level: " + str(e))
            raise

    def _create_return_track(self, name=None):
        """Create a new return track and optionally name it."""
        try:
            self._song.create_return_track()
            new_return = self._song.return_tracks[-1]
            if name:
                new_return.name = name
            return {"index": len(self._song.return_tracks) - 1, "name": new_return.name}
        except Exception as e:
            self.log_message("Error creating return track: " + str(e))
            raise

    def _delete_return_track(self, index):
        """Delete a return track by index."""
        try:
            if index < 0 or index >= len(self._song.return_tracks):
                raise IndexError("Return track index out of range")
            name = self._song.return_tracks[index].name
            self._song.delete_return_track(index)
            return {"deleted": True, "index": index, "name": name}
        except Exception as e:
            self.log_message("Error deleting return track: " + str(e))
            raise

    def _set_return_track_name(self, index, name):
        """Rename a return track."""
        try:
            if index < 0 or index >= len(self._song.return_tracks):
                raise IndexError("Return track index out of range")
            self._song.return_tracks[index].name = name
            return {"index": index, "name": self._song.return_tracks[index].name}
        except Exception as e:
            self.log_message("Error renaming return track: " + str(e))
            raise
    
    def _create_midi_track(self, index):
        """Create a new MIDI track at the specified index"""
        try:
            # Create the track
            self._song.create_midi_track(index)
            
            # Get the new track
            new_track_index = len(self._song.tracks) - 1 if index == -1 else index
            new_track = self._song.tracks[new_track_index]
            
            result = {
                "index": new_track_index,
                "name": new_track.name
            }
            return result
        except Exception as e:
            self.log_message("Error creating MIDI track: " + str(e))
            raise
    
    
    def _set_track_name(self, track_index, name):
        """Set the name of a track"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            # Set the name
            track = self._song.tracks[track_index]
            track.name = name
            
            result = {
                "name": track.name
            }
            return result
        except Exception as e:
            self.log_message("Error setting track name: " + str(e))
            raise
    
    def _create_clip(self, track_index, clip_index, length):
        """Create a new MIDI clip in the specified track and clip slot"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            # Check if the clip slot already has a clip
            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")
            
            # Create the clip
            clip_slot.create_clip(length)
            
            result = {
                "name": clip_slot.clip.name,
                "length": clip_slot.clip.length
            }
            return result
        except Exception as e:
            self.log_message("Error creating clip: " + str(e))
            raise

    def _delete_clip(self, track_index, clip_index):
        """Delete a clip from a slot."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            if not slot.has_clip:
                return {"deleted": False, "reason": "slot_empty"}
            clip_name = slot.clip.name
            slot.delete_clip()
            return {"deleted": True, "track_index": track_index, "clip_index": clip_index, "name": clip_name}
        except Exception as e:
            self.log_message("Error deleting clip: " + str(e))
            raise

    def _duplicate_clip(self, track_index, clip_index, target_track_index=None, target_clip_index=None):
        """Duplicate a MIDI clip by copying its notes and loop to a target slot."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            source_track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(source_track.clip_slots):
                raise IndexError("Clip index out of range")
            source_slot = source_track.clip_slots[clip_index]
            if not source_slot.has_clip:
                raise ValueError("No clip in source slot")

            if target_track_index is None:
                target_track = source_track
            else:
                if target_track_index < 0 or target_track_index >= len(self._song.tracks):
                    raise IndexError("Target track index out of range")
                target_track = self._song.tracks[target_track_index]
            target_slot_index = clip_index if target_clip_index is None else target_clip_index
            if target_slot_index < 0 or target_slot_index >= len(target_track.clip_slots):
                raise IndexError("Target clip index out of range")
            target_slot = target_track.clip_slots[target_slot_index]
            if target_slot.has_clip:
                raise ValueError("Target slot already has a clip")

            source_clip = source_slot.clip
            clip_length = source_clip.length
            target_slot.create_clip(clip_length)
            new_clip = target_slot.clip
            new_clip.name = source_clip.name + " (Copy)"
            new_clip.looping = source_clip.looping
            new_clip.loop_start = source_clip.loop_start
            new_clip.loop_end = source_clip.loop_end

            if getattr(source_clip, "is_midi_clip", False):
                notes = self._read_clip_notes(source_clip)
                self._write_clip_notes(new_clip, notes, replace=True)
                new_clip.deselect_all_notes()
            else:
                # Audio duplication is not directly supported without user interaction
                new_clip.name = source_clip.name + " (Copy - audio)"
            return {
                "duplicated_from": {"track_index": track_index, "clip_index": clip_index},
                "target": {"track_index": target_track_index if target_track_index is not None else track_index, "clip_index": target_slot_index},
                "length": clip_length,
                "is_midi": getattr(source_clip, "is_midi_clip", False)
            }
        except Exception as e:
            self.log_message("Error duplicating clip: " + str(e))
            raise

    def _supports_extended_notes(self, clip):
        """Return True if the Live API exposes the extended note API (MPE/probability)."""
        try:
            return hasattr(clip, "set_notes_extended") and hasattr(clip, "get_notes_extended")
        except Exception:
            return False

    def _note_to_dict(self, note):
        """Normalize Live note objects/tuples/dicts into a dict."""
        if isinstance(note, dict):
            return dict(note)
        if hasattr(note, "pitch"):
            return {
                "pitch": getattr(note, "pitch", None),
                "start_time": getattr(note, "start_time", None),
                "duration": getattr(note, "duration", None),
                "velocity": getattr(note, "velocity", None),
                "mute": getattr(note, "mute", None),
                "velocity_deviation": getattr(note, "velocity_deviation", None) if hasattr(note, "velocity_deviation") else None,
                "probability": getattr(note, "probability", None) if hasattr(note, "probability") else None,
                "release_velocity": getattr(note, "release_velocity", None) if hasattr(note, "release_velocity") else None,
                "note_id": getattr(note, "note_id", None) if hasattr(note, "note_id") else None
            }
        try:
            pitch, start_time, duration, velocity, mute = note
            return {
                "pitch": pitch,
                "start_time": start_time,
                "duration": duration,
                "velocity": velocity,
                "mute": mute
            }
        except Exception:
            return {}

    def _clear_clip_notes(self, clip):
        """Remove all notes from a clip using the richest API available."""
        try:
            if hasattr(clip, "remove_notes_extended"):
                clip.remove_notes_extended(0.0, 0, clip.length, 128)
                return
        except Exception:
            pass
        try:
            clip.remove_notes(0.0, 0, clip.length, 128)
        except Exception as e:
            self.log_message("Error clearing clip notes: {0}".format(e))
            raise

    def _write_clip_notes(self, clip, notes, replace=False):
        """Write notes to a clip, using extended note data when available."""
        try:
            if replace:
                self._clear_clip_notes(clip)

            if self._supports_extended_notes(clip):
                live_notes = []
                for note in notes:
                    data = self._note_to_dict(note)
                    payload = {
                        "pitch": int(data.get("pitch", 60)),
                        "start_time": float(data.get("start_time", 0.0)),
                        "duration": float(max(data.get("duration", 0.01), 0.001)),
                        "velocity": int(data.get("velocity", 100)),
                        "mute": bool(data.get("mute", False))
                    }
                    for key in ("probability", "velocity_deviation", "release_velocity"):
                        if data.get(key) is not None:
                            payload[key] = data.get(key)
                    live_notes.append(payload)
                clip.set_notes_extended(tuple(live_notes))
            else:
                live_notes = []
                for note in notes:
                    data = self._note_to_dict(note)
                    live_notes.append((
                        int(data.get("pitch", 60)),
                        float(data.get("start_time", 0.0)),
                        float(max(data.get("duration", 0.01), 0.001)),
                        int(data.get("velocity", 100)),
                        bool(data.get("mute", False))
                    ))
                clip.set_notes(tuple(live_notes))
        except Exception as e:
            self.log_message("Error writing clip notes: {0}".format(e))
            raise

    def _read_clip_notes(self, clip):
        """Read all notes from a clip, preferring extended/MPE data when available."""
        try:
            if self._supports_extended_notes(clip):
                raw_notes = clip.get_notes_extended(0.0, 0, clip.length, 128)
            else:
                raw_notes = clip.get_notes(0.0, 0, clip.length, 128)
            return [self._note_to_dict(n) for n in raw_notes]
        except Exception as e:
            self.log_message("Error reading clip notes: {0}".format(e))
            raise
    
    def _add_notes_to_clip(self, track_index, clip_index, notes):
        """Add MIDI notes to a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip = clip_slot.clip
            self._write_clip_notes(clip, notes, replace=False)
            
            result = {
                "note_count": len(notes)
            }
            return result
        except Exception as e:
            self.log_message("Error adding notes to clip: " + str(e))
            raise
    
    def _set_clip_name(self, track_index, clip_index, name):
        """Set the name of a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip = clip_slot.clip
            clip.name = name
            
            result = {
                "name": clip.name
            }
            return result
        except Exception as e:
            self.log_message("Error setting clip name: " + str(e))
            raise

    def _set_clip_loop(self, track_index, clip_index, start, end, loop_on=True):
        """Set loop boundaries and enable/disable looping for a clip."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            if not slot.has_clip:
                raise ValueError("No clip in slot")
            clip = slot.clip
            if start is not None and end is not None and end <= start:
                raise ValueError("Loop end must be greater than loop start")
            if start is not None:
                clip.loop_start = start
            if end is not None:
                clip.loop_end = end
            clip.looping = bool(loop_on)
            return {"loop_start": clip.loop_start, "loop_end": clip.loop_end, "looping": clip.looping}
        except Exception as e:
            self.log_message("Error setting clip loop: " + str(e))
            raise

    def _set_clip_length(self, track_index, clip_index, length):
        """Resize a clip's loop length."""
        try:
            if length is None or length <= 0:
                raise ValueError("Length must be positive")
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            if not slot.has_clip:
                raise ValueError("No clip in slot")
            clip = slot.clip
            clip.loop_end = clip.loop_start + length
            try:
                clip.end_marker = clip.loop_end
            except Exception:
                pass
            return {"length": length, "loop_start": clip.loop_start, "loop_end": clip.loop_end}
        except Exception as e:
            self.log_message("Error setting clip length: " + str(e))
            raise

    def _quantize_clip(self, track_index, clip_index, grid, amount):
        """Quantize MIDI clip notes by a simple grid size (e.g., 16 for 1/16th notes)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            if not slot.has_clip:
                raise ValueError("No clip in slot")
            clip = slot.clip
            if not getattr(clip, "is_midi_clip", False):
                raise ValueError("Quantize is only supported for MIDI clips")

            grid_size = 4.0 / float(grid) if grid else 0.25
            amount = max(0.0, min(1.0, float(amount)))

            notes = self._read_clip_notes(clip)
            quantized = []
            for note in notes:
                pitch = note.get("pitch", 60)
                start_time = note.get("start_time", 0.0)
                duration = note.get("duration", 0.25)
                velocity = note.get("velocity", 100)
                mute = note.get("mute", False)
                target_start = round(start_time / grid_size) * grid_size
                new_start = (start_time * (1 - amount)) + (target_start * amount)
                target_duration = round(duration / grid_size) * grid_size
                new_duration = (duration * (1 - amount)) + (target_duration * amount)
                updated = dict(note)
                updated["pitch"] = pitch
                updated["start_time"] = new_start
                updated["duration"] = max(new_duration, 0.01)
                updated["velocity"] = velocity
                updated["mute"] = mute
                quantized.append(updated)
            self._write_clip_notes(clip, quantized, replace=True)
            clip.deselect_all_notes()
            return {"note_count": len(quantized), "grid": grid_size, "amount": amount}
        except Exception as e:
            self.log_message("Error quantizing clip: " + str(e))
            raise
    
    def _set_tempo(self, tempo):
        """Set the tempo of the session"""
        try:
            self._song.tempo = tempo
            
            result = {
                "tempo": self._song.tempo
            }
            return result
        except Exception as e:
            self.log_message("Error setting tempo: " + str(e))
            raise

    def _set_time_signature(self, numerator, denominator):
        """Set the global time signature."""
        try:
            self._song.signature_numerator = int(numerator)
            self._song.signature_denominator = int(denominator)
            return {
                "signature_numerator": self._song.signature_numerator,
                "signature_denominator": self._song.signature_denominator
            }
        except Exception as e:
            self.log_message("Error setting time signature: " + str(e))
            raise
    
    def _fire_clip(self, track_index, clip_index):
        """Fire a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip_slot.fire()
            
            result = {
                "fired": True
            }
            return result
        except Exception as e:
            self.log_message("Error firing clip: " + str(e))
            raise

    def _fire_clip_by_name(self, clip_pattern, track_pattern=None, match_mode="contains", first_only=True):
        """Fire clips whose names match a pattern (optionally filter by track name)."""
        try:
            if clip_pattern is None or clip_pattern == "":
                raise ValueError("clip_pattern is required")
            fired = []
            for t_idx, track in enumerate(self._song.tracks):
                if track_pattern and not self._name_matches(track.name, track_pattern, match_mode):
                    continue
                for c_idx, slot in enumerate(track.clip_slots):
                    if not slot.has_clip:
                        continue
                    clip = slot.clip
                    if self._name_matches(getattr(clip, "name", ""), clip_pattern, match_mode):
                        slot.fire()
                        fired.append({
                            "track_index": t_idx,
                            "track_name": track.name,
                            "clip_index": c_idx,
                            "clip_name": clip.name
                        })
                        if first_only:
                            return {"fired": fired}
            if not fired:
                raise ValueError("No clips matched pattern '{0}'".format(clip_pattern))
            return {"fired": fired}
        except Exception as e:
            self.log_message("Error firing clip by name: " + str(e))
            raise

    def _trigger_test_midi(
        self,
        track_index,
        clip_index,
        length,
        pitch,
        velocity,
        duration,
        start_time,
        overwrite_clip,
        fire_clip,
        cc_number,
        cc_value,
        channel
    ):
        """Create/reuse a short MIDI clip and fire a test note/optional CC."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if not getattr(track, "has_midi_input", False) and not getattr(track, "has_midi_output", False):
                raise ValueError("Track does not support MIDI")
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")

            clip_slot = track.clip_slots[clip_index]
            created_clip = False
            if not clip_slot.has_clip:
                clip_slot.create_clip(length)
                created_clip = True
            elif not overwrite_clip:
                raise Exception("Clip slot already has a clip; set overwrite_clip=True to reuse it")

            clip = clip_slot.clip
            if not getattr(clip, "is_midi_clip", False):
                raise Exception("Target clip slot is not a MIDI clip")

            self._write_clip_notes(clip, [{
                "pitch": int(pitch),
                "start_time": float(start_time),
                "duration": float(max(duration, 0.01)),
                "velocity": int(velocity),
                "mute": False
            }], replace=True)

            cc_result = None
            if cc_number is not None:
                try:
                    status = 176 + max(min(int(channel), 15), 0)
                    data = (status, int(cc_number), int(cc_value))
                    self._send_midi(data)
                    cc_result = {"sent": True, "status": status, "cc_number": int(cc_number), "value": int(cc_value)}
                except Exception as cc_err:
                    cc_result = {"sent": False, "error": str(cc_err)}

            if fire_clip:
                clip_slot.fire()

            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "created_clip": created_clip,
                "note": {"pitch": int(pitch), "velocity": int(velocity), "duration": float(duration), "start_time": float(start_time)},
                "fired": bool(fire_clip),
                "cc": cc_result
            }
        except Exception as e:
            self.log_message("Error triggering test MIDI: " + str(e))
            raise
    
    def _stop_clip(self, track_index, clip_index):
        """Stop a clip"""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            clip_slot.stop()
            
            result = {
                "stopped": True
            }
            return result
        except Exception as e:
            self.log_message("Error stopping clip: " + str(e))
            raise

    def _create_scene(self, index=-1, name=None):
        """Create a new scene."""
        try:
            if index is None or index < 0:
                index = len(self._song.scenes)
            self._song.create_scene(index)
            created_index = min(index, len(self._song.scenes) - 1)
            scene = self._song.scenes[created_index]
            if name:
                scene.name = name
            return {"index": created_index, "name": scene.name}
        except Exception as e:
            self.log_message("Error creating scene: " + str(e))
            raise

    def _delete_scene(self, index):
        """Delete a scene by index."""
        try:
            if index < 0 or index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            name = self._song.scenes[index].name
            self._song.delete_scene(index)
            return {"deleted": True, "index": index, "name": name}
        except Exception as e:
            self.log_message("Error deleting scene: " + str(e))
            raise

    def _duplicate_scene(self, index):
        """Duplicate a scene."""
        try:
            if index < 0 or index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            self._song.duplicate_scene(index)
            new_index = index + 1
            scene = self._song.scenes[new_index]
            return {"index": new_index, "name": scene.name, "duplicated_from": index}
        except Exception as e:
            self.log_message("Error duplicating scene: " + str(e))
            raise

    def _fire_scene(self, index):
        """Launch a scene."""
        try:
            if index < 0 or index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            scene = self._song.scenes[index]
            scene.fire()
            return {"index": index, "name": scene.name, "fired": True}
        except Exception as e:
            self.log_message("Error firing scene: " + str(e))
            raise

    def _fire_scene_by_name(self, pattern, match_mode="contains", first_only=True):
        """Launch scenes matching a name pattern."""
        try:
            if pattern is None or pattern == "":
                raise ValueError("pattern is required")
            fired = []
            for idx, scene in enumerate(self._song.scenes):
                if self._name_matches(scene.name, pattern, match_mode):
                    scene.fire()
                    fired.append({"index": idx, "name": scene.name})
                    if first_only:
                        return {"fired": fired}
            if not fired:
                raise ValueError("No scenes matched pattern '{0}'".format(pattern))
            return {"fired": fired}
        except Exception as e:
            self.log_message("Error firing scene by name: " + str(e))
            raise

    def _stop_scene(self, index):
        """Stop all clips in a scene."""
        try:
            if index < 0 or index >= len(self._song.scenes):
                raise IndexError("Scene index out of range")
            scene = self._song.scenes[index]

            stopped_slots = 0
            for track in self._song.tracks:
                try:
                    if index < len(track.clip_slots):
                        track.clip_slots[index].stop()
                        stopped_slots += 1
                except Exception as slot_err:
                    self.log_message("Error stopping slot {0} on track {1}: {2}".format(index, getattr(track, "name", "unknown"), slot_err))

            try:
                if getattr(self._song.view, "selected_scene", None) == scene:
                    self._song.stop_all_clips()
            except Exception as global_stop_err:
                self.log_message("Error issuing global stop_all_clips: {0}".format(global_stop_err))

            return {"index": index, "name": scene.name, "stopped": True, "stopped_slots": stopped_slots}
        except Exception as e:
            self.log_message("Error stopping scene: " + str(e))
            raise
    
    
    def _start_playback(self):
        """Start playing the session"""
        try:
            self._song.start_playing()
            
            result = {
                "playing": self._song.is_playing
            }
            return result
        except Exception as e:
            self.log_message("Error starting playback: " + str(e))
            raise
    
    def _stop_playback(self):
        """Stop playing the session"""
        try:
            self._song.stop_playing()
            
            result = {
                "playing": self._song.is_playing
            }
            return result
        except Exception as e:
            self.log_message("Error stopping playback: " + str(e))
            raise
    
    def _get_browser_item(self, uri, path):
        """Get a browser item by URI or path"""
        try:
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            if not app:
                raise RuntimeError("Could not access Live application")
                
            result = {
                "uri": uri,
                "path": path,
                "found": False
            }
            
            # Try to find by URI first if provided
            if uri:
                item = self._find_browser_item_by_uri(app.browser, uri)
                if item:
                    result["found"] = True
                    result["item"] = {
                        "name": item.name,
                        "is_folder": item.is_folder,
                        "is_device": item.is_device,
                        "is_loadable": item.is_loadable,
                        "uri": item.uri
                    }
                    return result
            
            # If URI not provided or not found, try by path
            if path:
                # Parse the path and navigate to the specified item
                path_parts = path.split("/")
                
                # Determine the root based on the first part
                current_item = None
                if path_parts[0].lower() == "nstruments":
                    current_item = app.browser.instruments
                elif path_parts[0].lower() == "sounds":
                    current_item = app.browser.sounds
                elif path_parts[0].lower() == "drums":
                    current_item = app.browser.drums
                elif path_parts[0].lower() == "audio_effects":
                    current_item = app.browser.audio_effects
                elif path_parts[0].lower() == "midi_effects":
                    current_item = app.browser.midi_effects
                else:
                    # Default to instruments if not specified
                    current_item = app.browser.instruments
                    # Don't skip the first part in this case
                    path_parts = ["instruments"] + path_parts
                
                # Navigate through the path
                for i in range(1, len(path_parts)):
                    part = path_parts[i]
                    if not part:  # Skip empty parts
                        continue
                    
                    found = False
                    for child in current_item.children:
                        if child.name.lower() == part.lower():
                            current_item = child
                            found = True
                            break
                    
                    if not found:
                        result["error"] = "Path part '{0}' not found".format(part)
                        return result
                
                # Found the item
                result["found"] = True
                result["item"] = {
                    "name": current_item.name,
                    "is_folder": current_item.is_folder,
                    "is_device": current_item.is_device,
                    "is_loadable": current_item.is_loadable,
                    "uri": current_item.uri
                }
            
            return result
        except Exception as e:
            self.log_message("Error getting browser item: " + str(e))
            self.log_message(traceback.format_exc())
            raise   
    
    
    
    def _load_browser_item(self, track_index, item_uri, clip_index=None):
        """Load a browser item onto a track by its URI (optionally target a clip slot)."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            
            track = self._song.tracks[track_index]
            
            # Access the application's browser instance instead of creating a new one
            app = self.application()
            
            # Find the browser item by URI
            item = self._find_browser_item_by_uri(app.browser, item_uri)
            
            if not item:
                raise ValueError("Browser item with URI '{0}' not found".format(item_uri))
            
            # Select the track
            self._song.view.selected_track = track
            try:
                if clip_index is not None and clip_index >= 0:
                    scene_count = len(self._song.scenes)
                    # Clamp to available scenes (clip slots mirror scenes)
                    if clip_index >= scene_count:
                        clip_index = scene_count - 1
                    if clip_index >= 0:
                        target_slot = track.clip_slots[clip_index]
                        self._song.view.highlighted_clip_slot = target_slot
                        self._song.view.selected_scene = self._song.scenes[clip_index]
            except Exception as slot_err:
                self.log_message("Unable to set target clip slot: {0}".format(slot_err))
            
            # Load the item
            app.browser.load_item(item)
            
            result = {
                "loaded": True,
                "item_name": item.name,
                "track_name": track.name,
                "uri": item_uri
            }
            return result
        except Exception as e:
            self.log_message("Error loading browser item: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _load_simpler_with_sample(self, track_index, file_path, device_slot=-1):
        """
        Load Simpler on a track and set its sample.file_path directly to the given path.
        Returns device_index and sample metadata.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            if not file_path:
                raise ValueError("file_path is required")

            track = self._song.tracks[track_index]
            stem = Path(file_path).stem.lower() if Path else file_path.split("/")[-1].rsplit(".", 1)[0].lower()
            # Load Simpler via browser if needed
            # Try to find an existing Simpler at device_slot
            device = None
            if device_slot >= 0 and device_slot < len(track.devices):
                dev = track.devices[device_slot]
                if hasattr(dev, "class_name") and dev.class_name == "OriginalSimpler":
                    device = dev
            if device is None:
                # Find Simpler in browser by name and load it
                app = self.application()
                if not app or not hasattr(app, "browser"):
                    raise ValueError("Could not access Live browser")

                def _find_simpler(root):
                    stack = [root]
                    while stack:
                        item = stack.pop()
                        try:
                            name = getattr(item, "name", "").lower()
                            is_device = getattr(item, "is_device", False)
                            is_loadable = getattr(item, "is_loadable", False)
                            if is_device and is_loadable and name == "simpler":
                                return item
                            for child in getattr(item, "children", []):
                                stack.append(child)
                        except Exception:
                            continue
                    return None

                simpler_item = None
                try:
                    if hasattr(app.browser, "instruments"):
                        simpler_item = _find_simpler(app.browser.instruments)
                except Exception:
                    simpler_item = None
                if simpler_item is None and hasattr(app.browser, "sounds"):
                    try:
                        simpler_item = _find_simpler(app.browser.sounds)
                    except Exception:
                        simpler_item = None
                if simpler_item is None:
                    raise ValueError("Could not find Simpler in browser")

                self._song.view.selected_track = track
                app.browser.load_item(simpler_item)
                if len(track.devices) == 0:
                    raise IndexError("No devices after loading Simpler")
                device = track.devices[-1]
            # Load sample via browser hotswap if possible
            loaded = False
            try:
                app = self.application()
                browser_path = None
                parts = file_path.replace("\\", "/").split("/")
                if "Core Library" in parts:
                    idx = parts.index("Core Library")
                    browser_path = "/".join(parts[idx:-1])
                elif "Factory Packs" in parts:
                    idx = parts.index("Factory Packs")
                    browser_path = "/".join(parts[idx:-1])
                elif "User Library" in parts:
                    idx = parts.index("User Library")
                    browser_path = "/".join(parts[idx:-1])
                if browser_path:
                    items = self.get_browser_items_at_path(browser_path)
                    target_uri = None
                    for it in items.get("items", []):
                        if str(it.get("name", "")).lower() == stem and it.get("is_loadable", False):
                            target_uri = it.get("uri")
                            break
                    # Fallback: search root Samples if folder lookup fails
                    if not target_uri:
                        target_uri = self._find_sample_uri_by_stem(stem)
                    if target_uri:
                        try:
                            app.browser.hotswap_target = device
                        except Exception:
                            pass
                        target_item = self._find_browser_item_by_uri(app.browser, target_uri)
                        if target_item:
                            app.browser.load_item(target_item)
                            loaded = True
            except Exception:
                loaded = False

            warn = None
            if not loaded:
                # Last resort: try direct hotswap by root Samples URI
                fallback_uri = self._find_sample_uri_by_stem(stem)
                if fallback_uri:
                    loaded = self._hotswap_device_with_uri(device, fallback_uri)
            if not loaded:
                warn = "Unable to load sample via browser or hotswap"
            result = {
                "track_index": track_index,
                "device_index": list(track.devices).index(device),
                "file_path": file_path,
                "loaded": loaded,
                "warping": getattr(getattr(device, "sample", None), "warping", None),
                "warp_mode": getattr(getattr(device, "sample", None), "warp_mode", None)
            }
            if warn:
                result["warning"] = warn
            return result
        except Exception as e:
            self.log_message("Error loading Simpler with sample: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _load_sampler_with_sample(self, track_index, file_path, device_slot=-1):
        """
        Load Sampler on a track and try to load a sample via browser hotswap; fallback to file_path.
        """
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            if not file_path:
                raise ValueError("file_path is required")

            track = self._song.tracks[track_index]
            stem = Path(file_path).stem.lower() if Path else file_path.split("/")[-1].rsplit(".", 1)[0].lower()
            device = None
            if device_slot >= 0 and device_slot < len(track.devices):
                dev = track.devices[device_slot]
                if hasattr(dev, "class_name") and dev.class_name.lower() == "sampler":
                    device = dev

            if device is None:
                app = self.application()
                if not app or not hasattr(app, "browser"):
                    raise ValueError("Could not access Live browser")

                def _find_sampler(root):
                    stack = [root]
                    while stack:
                        item = stack.pop()
                        try:
                            name = getattr(item, "name", "").lower()
                            is_device = getattr(item, "is_device", False)
                            is_loadable = getattr(item, "is_loadable", False)
                            if is_device and is_loadable and name == "sampler":
                                return item
                            for child in getattr(item, "children", []):
                                stack.append(child)
                        except Exception:
                            continue
                    return None

                sampler_item = None
                try:
                    if hasattr(app.browser, "instruments"):
                        sampler_item = _find_sampler(app.browser.instruments)
                except Exception:
                    sampler_item = None
                if sampler_item is None and hasattr(app.browser, "sounds"):
                    try:
                        sampler_item = _find_sampler(app.browser.sounds)
                    except Exception:
                        sampler_item = None
                if sampler_item is None:
                    raise ValueError("Could not find Sampler in browser")

                self._song.view.selected_track = track
                app.browser.load_item(sampler_item)
                if len(track.devices) == 0:
                    raise IndexError("No devices after loading Sampler")
                device = track.devices[-1]

            loaded = False
            warn = None
            try:
                app = self.application()
                browser_path = None
                parts = file_path.replace("\\", "/").split("/")
                if "Core Library" in parts:
                    idx = parts.index("Core Library")
                    browser_path = "/".join(parts[idx:-1])
                elif "Factory Packs" in parts:
                    idx = parts.index("Factory Packs")
                    browser_path = "/".join(parts[idx:-1])
                elif "User Library" in parts:
                    idx = parts.index("User Library")
                    browser_path = "/".join(parts[idx:-1])
                if browser_path and app and hasattr(app, "browser"):
                    items = self.get_browser_items_at_path(browser_path)
                    target_uri = None
                    for it in items.get("items", []):
                        if str(it.get("name", "")).lower() == stem and it.get("is_loadable", False):
                            target_uri = it.get("uri")
                            break
                    # Fallback: search root Samples if folder lookup fails
                    if not target_uri:
                        target_uri = self._find_sample_uri_by_stem(stem)
                    if target_uri:
                        loaded = self._hotswap_device_with_uri(device, target_uri)
            except Exception:
                loaded = False

            if not loaded:
                # Last resort: try direct hotswap by root Samples URI
                fallback_uri = self._find_sample_uri_by_stem(stem)
                if fallback_uri:
                    loaded = self._hotswap_device_with_uri(device, fallback_uri)
                if not loaded:
                    warn = "Unable to load sample via browser or hotswap"

            result = {
                "track_index": track_index,
                "device_index": list(track.devices).index(device),
                "file_path": file_path,
                "loaded": loaded
            }
            if warn:
                result["warning"] = warn
            return result
        except Exception as e:
            self.log_message("Error loading Sampler with sample: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _resolve_parameter(self, device, param_spec):
        """Resolve a device parameter by index or case-insensitive name."""
        try:
            if isinstance(param_spec, int):
                return device.parameters[param_spec]
            if isinstance(param_spec, str):
                target = param_spec.lower()
                for p in device.parameters:
                    if hasattr(p, 'name') and p.name.lower() == target:
                        return p
            raise ValueError("Parameter '{0}' not found on device. Available: {1}".format(
                param_spec, [getattr(p, 'name', 'unknown') for p in device.parameters]
            ))
        except IndexError:
            raise ValueError("Parameter index {0} out of range".format(param_spec))

    def _parameter_meta(self, param):
        """Return metadata for a Live device parameter."""
        value_items = None
        try:
            if getattr(param, "is_quantized", False) and hasattr(param, "value_items"):
                value_items = list(getattr(param, "value_items", []))
        except Exception:
            value_items = None
        return {
            "name": getattr(param, "name", "Unknown"),
            "min": getattr(param, "min", None),
            "max": getattr(param, "max", None),
            "value": getattr(param, "value", None),
            "is_quantized": bool(getattr(param, "is_quantized", False)),
            "value_items": value_items,
            "unit": getattr(param, "unit", None)
        }

    def _normalize_param_value(self, param, target):
        """Normalize human-friendly values (%, dB text, names) into Live parameter space."""
        try:
            # Direct numeric passthrough
            if isinstance(target, (int, float)):
                value = float(target)
            elif isinstance(target, str):
                raw = target.strip()
                lower = raw.lower()
                value_items = None
                try:
                    if getattr(param, "is_quantized", False) and hasattr(param, "value_items"):
                        value_items = getattr(param, "value_items", [])
                except Exception:
                    value_items = None
                if value_items:
                    for idx, item in enumerate(value_items):
                        if lower == str(item).lower():
                            return idx
                if lower in ["min", "minimum"]:
                    return getattr(param, "min", 0.0)
                if lower in ["max", "maximum"]:
                    return getattr(param, "max", 1.0)
                if lower.endswith("%"):
                    pct = float(lower.replace("%", "")) / 100.0
                    value = getattr(param, "min", 0.0) + pct * (getattr(param, "max", 1.0) - getattr(param, "min", 0.0))
                elif lower.endswith("db"):
                    value = float(lower.replace("db", ""))
                else:
                    value = float(raw)
            else:
                raise ValueError("Unsupported parameter value type: {0}".format(type(target)))

            # Clamp
            try:
                param_min = getattr(param, "min", None)
                param_max = getattr(param, "max", None)
                if param_min is not None and param_max is not None:
                    value = max(param_min, min(param_max, value))
            except Exception:
                pass

            # Quantize if needed
            if getattr(param, "is_quantized", False):
                value = round(value)
            return value
        except Exception as e:
            raise ValueError("Could not normalize value '{0}' for parameter {1}: {2}".format(target, getattr(param, "name", "unknown"), str(e)))

    def _find_param_by_keywords(self, device, keywords):
        """Find the first parameter whose name contains all keywords."""
        for p in device.parameters:
            name = getattr(p, 'name', '') or ''
            lower_name = name.lower()
            if all(k in lower_name for k in keywords):
                return p
        return None

    def _load_device(self, track_index, device_uri, device_slot=-1):
        """Load a device onto a track using its browser URI."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            app = self.application()
            item = self._find_browser_item_by_uri(app.browser, device_uri)

            if not item:
                raise ValueError("Browser item with URI '{0}' not found".format(device_uri))

            # Select the track and load the device
            self._song.view.selected_track = track
            app.browser.load_item(item)

            # Capture device count after load for reference
            parameter_names = []
            try:
                last_device = track.devices[-1]
                parameter_names = [getattr(p, "name", "Unknown") for p in last_device.parameters]
            except Exception:
                parameter_names = []

            result = {
                "loaded": True,
                "item_name": item.name,
                "track_name": track.name,
                "uri": device_uri,
                "device_count": len(track.devices),
                "requested_slot": device_slot,
                "parameters": parameter_names
            }
            return result
        except Exception as e:
            self.log_message("Error loading device: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _set_device_parameter(self, track_index, device_index, parameter, value):
        """Set a parameter on a device by index or name."""
        try:
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")

            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")

            device = track.devices[device_index]
            param = self._resolve_parameter(device, parameter)
            before = param.value
            normalized_value = self._normalize_param_value(param, value)
            param.value = normalized_value

            meta = self._parameter_meta(param)
            meta["before"] = before
            meta["after"] = param.value
            meta["device_name"] = getattr(device, "name", "Unknown")
            return meta
        except Exception as e:
            self.log_message("Error setting device parameter: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def _set_device_parameters(self, track_index, device_index, parameters):
        """Set multiple parameters on a device from a dict or list payload."""
        try:
            if parameters is None:
                return {"updated": [], "errors": []}
            if track_index < 0 or track_index >= len(self._song.tracks):
                raise IndexError("Track index out of range")
            track = self._song.tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]

            updates = []
            errors = []

            def _apply(param_spec, value):
                try:
                    param = self._resolve_parameter(device, param_spec)
                    before = param.value
                    param.value = self._normalize_param_value(param, value)
                    meta = self._parameter_meta(param)
                    meta["before"] = before
                    meta["after"] = param.value
                    meta["device_name"] = getattr(device, "name", "Unknown")
                    meta["index"] = list(device.parameters).index(param)
                    updates.append(meta)
                except Exception as err:
                    errors.append({"parameter": param_spec, "error": str(err)})

            if isinstance(parameters, dict):
                for key, val in parameters.items():
                    _apply(key, val)
            elif isinstance(parameters, (list, tuple)):
                for entry in parameters:
                    if isinstance(entry, dict):
                        _apply(entry.get("parameter", entry.get("name", entry.get("index", None))), entry.get("value", None))
                    elif isinstance(entry, (list, tuple)) and len(entry) == 2:
                        _apply(entry[0], entry[1])
            else:
                errors.append({"parameter": "payload", "error": "unsupported_type"})

            return {"updated": updates, "errors": errors}
        except Exception as e:
            self.log_message("Error setting multiple device parameters: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

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
                    device.input_routing_channel = matched_channel
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
    def _walk_browser_category(self, root_item, max_items=200, max_depth=4):
        """Breadth-first traversal to collect loadable items."""
        results = []
        queue_items = [(root_item, root_item.name if hasattr(root_item, "name") else "", 0)]
        while queue_items and len(results) < max_items:
            current, path, depth = queue_items.pop(0)
            if hasattr(current, "is_loadable") and current.is_loadable:
                results.append({
                    "name": getattr(current, "name", "Unknown"),
                    "uri": getattr(current, "uri", None),
                    "path": path,
                    "is_device": getattr(current, "is_device", False)
                })
            if depth < max_depth and hasattr(current, "children") and current.children:
                for child in current.children:
                    child_name = getattr(child, "name", "Unknown")
                    queue_items.append((child, path + "/" + child_name if path else child_name, depth + 1))
        return results

    def list_loadable_devices(self, category="all", max_items=200):
        """List loadable devices from a browser category."""
        try:
            app = self.application()
            if not app or not hasattr(app, "browser") or app.browser is None:
                raise RuntimeError("Browser is not available in the Live application")

            categories = []
            if category == "all":
                categories = [
                    ("instruments", getattr(app.browser, "instruments", None)),
                    ("sounds", getattr(app.browser, "sounds", None)),
                    ("drums", getattr(app.browser, "drums", None)),
                    ("audio_effects", getattr(app.browser, "audio_effects", None)),
                    ("midi_effects", getattr(app.browser, "midi_effects", None)),
                ]
            else:
                cat_obj = getattr(app.browser, category, None)
                categories = [(category, cat_obj)]

            results = []
            for cat_name, cat_item in categories:
                if not cat_item:
                    continue
                items = self._walk_browser_category(cat_item, max_items=max_items, max_depth=4)
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
            self.log_message("Error listing loadable devices: {0}".format(str(e)))
            self.log_message(traceback.format_exc())
            raise

    def search_loadable_devices(self, query, category="all", max_items=50):
        """Search loadable devices by name substring."""
        try:
            if not query:
                return {"count": 0, "items": []}
            listed = self.list_loadable_devices(category, max_items=max_items * 3)
            matches = []
            q = query.lower()
            for item in listed.get("items", []):
                if q in (item.get("name", "").lower()):
                    matches.append(item)
                if len(matches) >= max_items:
                    break
            return {
                "count": len(matches),
                "items": matches
            }
        except Exception as e:
            self.log_message("Error searching loadable devices: {0}".format(str(e)))
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
    
    def _get_device_type(self, device):
        """Get the type of a device"""
        try:
            # Simple heuristic - in a real implementation you'd look at the device class
            if device.can_have_drum_pads:
                return "drum_machine"
            elif device.can_have_chains:
                return "rack"
            elif "instrument" in device.class_display_name.lower():
                return "instrument"
            elif "audio_effect" in device.class_name.lower():
                return "audio_effect"
            elif "midi_effect" in device.class_name.lower():
                return "midi_effect"
            else:
                return "unknown"
        except:
            return "unknown"
    
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
