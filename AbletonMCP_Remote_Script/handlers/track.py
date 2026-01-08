"""
Track Handler Module for AbletonMCP Remote Script.

This is the primary handler for track and clip operations. It contains the core
functionality for creating, editing, and manipulating tracks and MIDI clips.

Key Responsibilities:
    - Track CRUD (create, rename, delete, duplicate)
    - Track routing (I/O, monitoring, arm)
    - Track mixer (volume, pan, sends)
    - Clip CRUD (create, delete, duplicate)
    - Note manipulation (add, get, clear notes)
    - Extended note features (probability, velocity_deviation, release_velocity)
    - Clip properties (loop, length, quantize)
    - Automation envelopes

For Future Agents:
    - This handler is instantiated as `track_handler` on the main MCP
    - Access via interface.py command dispatcher
    - All methods that modify Live state must run on the main thread
    - Notes support extended attributes via Live's set_notes_extended() API
    
Common Patterns:
    >>> # Get a clip reference
    >>> clip = self._ensure_clip(track_index, clip_index, length)
    
    >>> # Write notes to a clip
    >>> self._write_clip_notes(clip, notes, replace=True)
    
    >>> # Check for extended note support
    >>> if self._supports_extended_notes(clip):
    ...     clip.set_notes_extended(notes_tuple)
"""
from __future__ import absolute_import, print_function, unicode_literals
import logging


class TrackHandler(object):
    """
    Primary handler for track and clip operations in AbletonMCP.
    
    This class manages all track-related functionality including:
        - Track creation/deletion/duplication
        - Track routing and mixer settings
        - Clip CRUD operations
        - MIDI note manipulation with extended attributes
        - Automation envelope support
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
        song: Property that returns the Live Song object
        
    Note:
        The duplicated code from Drum Rack, Groove, Simpler, and Arrangement
        sections remains for backward compatibility. New development should
        use the dedicated handler modules instead.
    """
    def __init__(self, mcp):
        self.mcp = mcp

    def _log(self, message):
        self.mcp.log_message(message)

    @property
    def song(self):
        return self.mcp._song

    def _match_routing_option(self, options, target):
        """Helper to find a routing input/output/channel by string name match."""
        if not target:
            return None
        target_lower = str(target).lower()
        # Direct match (object)
        if target in options:
            return target
        # Name match
        for opt in options:
            opt_name = getattr(opt, "display_name", getattr(opt, "name", str(opt)))
            if opt_name.lower() == target_lower:
                return opt
        return None

    def _describe_track_routing(self, track):
        """Get routing info for a track."""
        return {
            "input_routing_type": getattr(track.input_routing_type, "display_name", getattr(track.input_routing_type, "name", str(track.input_routing_type))) if hasattr(track, "input_routing_type") else None,
            "input_routing_channel": getattr(track.input_routing_channel, "display_name", getattr(track.input_routing_channel, "name", str(track.input_routing_channel))) if hasattr(track, "input_routing_channel") else None,
            "output_routing_type": getattr(track.output_routing_type, "display_name", getattr(track.output_routing_type, "name", str(track.output_routing_type))) if hasattr(track, "output_routing_type") else None,
            "output_routing_channel": getattr(track.output_routing_channel, "display_name", getattr(track.output_routing_channel, "name", str(track.output_routing_channel))) if hasattr(track, "output_routing_channel") else None,
            "monitoring_state": getattr(track, "monitoring_state", None) if hasattr(track, "monitoring_state") else None
        }

    def _describe_send_levels(self, track):
        """Get all send levels for a track."""
        sends = getattr(track.mixer_device, "sends", [])
        return [s.value for s in sends]

    def _set_multiple_send_levels(self, track_index, sends_dict):
        """Helper to set multiple sends from a dictionary {index: level}."""
        result = {"updated": [], "errors": [], "current": []}
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index {0} out of range".format(track_index))
            track = self.song.tracks[track_index]
            track_sends = track.mixer_device.sends
            
            for send_idx_str, level in sends_dict.items():
                try:
                    send_idx = int(send_idx_str)
                    if send_idx < 0 or send_idx >= len(track_sends):
                        result["errors"].append("Send index {0} out of range".format(send_idx))
                        continue
                    send_param = track_sends[send_idx]
                    send_param.value = max(send_param.min, min(send_param.max, float(level)))
                    result["updated"].append(send_idx)
                except Exception as e:
                    result["errors"].append("Error setting send {0}: {1}".format(send_idx_str, str(e)))
            
            result["current"] = [s.value for s in track_sends]
            return result
        except Exception as e:
            self._log("Error setting multiple sends: " + str(e))
            raise

    def create_midi_track(self, index):
        """Create a new MIDI track at the specified index"""
        try:
            # Create the track
            self.song.create_midi_track(index)
            
            # Get the new track
            new_track_index = len(self.song.tracks) - 1 if index == -1 else index
            new_track = self.song.tracks[new_track_index]
            
            result = {
                "index": new_track_index,
                "name": new_track.name
            }
            return result
        except Exception as e:
            self._log("Error creating MIDI track: " + str(e))
            raise

    def create_audio_track(self, index):
        """Create a new audio track at the specified index."""
        try:
            self.song.create_audio_track(index)
            new_track_index = len(self.song.tracks) - 1 if index == -1 else index
            new_track = self.song.tracks[new_track_index]
            return {"index": new_track_index, "name": new_track.name}
        except Exception as e:
            self._log("Error creating audio track: " + str(e))
            raise

    def delete_track(self, track_index):
        """Delete a track by index."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track_name = self.song.tracks[track_index].name
            self.song.delete_track(track_index)
            return {"deleted": True, "index": track_index, "name": track_name}
        except Exception as e:
            self._log("Error deleting track: " + str(e))
            raise

    def duplicate_track(self, track_index, target_index=None):
        """Duplicate a track and report the new index."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            self.song.duplicate_track(track_index)
            duplicated_index = track_index + 1
            track = self.song.tracks[duplicated_index]
            result = {"duplicated_from": track_index, "index": duplicated_index, "name": track.name}
            if target_index is not None:
                result["note"] = "Target index move not supported via API; duplicated next to source"
            return result
        except Exception as e:
            self._log("Error duplicating track: " + str(e))
            raise

    def set_track_name(self, track_index, name):
        """Set the name of a track"""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            
            track = self.song.tracks[track_index]
            track.name = name
            
            result = {
                "name": track.name
            }
            return result
        except Exception as e:
            self._log("Error setting track name: " + str(e))
            raise

    def configure_track_routing(self, track_index, input_type=None, input_channel=None, output_type=None, output_channel=None, monitor_state=None, arm=None, sends=None):
        """Set I/O, monitoring, arm, and multiple sends in one call."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]

            routing = self._describe_track_routing(track)
            if any(value is not None for value in (input_type, input_channel, output_type, output_channel)):
                routing = self.set_track_io(track_index, input_type, input_channel, output_type, output_channel)

            monitoring_state = routing.get("monitoring_state")
            if monitor_state is not None:
                monitor_result = self.set_track_monitor(track_index, monitor_state)
                monitoring_state = monitor_result.get("monitoring_state")

            arm_state = bool(getattr(track, "arm", False))
            if arm is not None:
                arm_result = self.set_track_bool(track_index, "arm", arm)
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
            self._log("Error configuring track routing: " + str(e))
            raise

    def set_track_io(self, track_index, input_type, input_channel, output_type, output_channel):
        """Set track input/output routing values."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]

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
            self._log("Error setting track routing: " + str(e))
            raise

    def set_track_monitor(self, track_index, state):
        """Set monitoring state (in/auto/off)."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
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
            self._log("Error setting monitoring state: " + str(e))
            raise

    def set_track_bool(self, track_index, attr_name, value):
        """Set boolean properties like arm/mute/solo."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            setattr(track, attr_name, bool(value))
            return {attr_name: bool(getattr(track, attr_name))}
        except Exception as e:
            self._log("Error setting track attribute {0}: {1}".format(attr_name, str(e)))
            raise

    def set_track_volume(self, track_index, volume):
        """Set mixer volume for a track."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            param = track.mixer_device.volume
            param.value = max(param.min, min(param.max, volume))
            return {"volume": param.value, "min": param.min, "max": param.max}
        except Exception as e:
            self._log("Error setting track volume: " + str(e))
            raise

    def set_track_panning(self, track_index, panning):
        """Set mixer panning for a track."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            param = track.mixer_device.panning
            param.value = max(param.min, min(param.max, panning))
            return {"panning": param.value, "min": param.min, "max": param.max}
        except Exception as e:
            self._log("Error setting track panning: " + str(e))
            raise

    def set_send_level(self, track_index, send_index, level):
        """Adjust send level to a return track."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
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
            self._log("Error setting send level: " + str(e))
            raise

    def create_return_track(self, name=None):
        """Create a new return track and optionally name it."""
        try:
            self.song.create_return_track()
            new_return = self.song.return_tracks[-1]
            if name:
                new_return.name = name
            return {"index": len(self.song.return_tracks) - 1, "name": new_return.name}
        except Exception as e:
            self._log("Error creating return track: " + str(e))
            raise

    def delete_return_track(self, index):
        """Delete a return track by index."""
        try:
            if index < 0 or index >= len(self.song.return_tracks):
                raise IndexError("Return track index out of range")
            name = self.song.return_tracks[index].name
            self.song.delete_return_track(index)
            return {"deleted": True, "index": index, "name": name}
        except Exception as e:
            self._log("Error deleting return track: " + str(e))
            raise

    def set_return_track_name(self, index, name):
        """Rename a return track."""
        try:
            if index < 0 or index >= len(self.song.return_tracks):
                raise IndexError("Return track index out of range")
            self.song.return_tracks[index].name = name
            return {"index": index, "name": self.song.return_tracks[index].name}
        except Exception as e:
            self._log("Error renaming return track: " + str(e))
            raise

    def get_routing_options(self, track_index):
        """
        Get available input and output routing options for a track.
        
        Args:
            track_index: Track index
        
        Returns:
            Dict with input_types, output_types, input_channels, output_channels
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            
            result = {
                "track_index": track_index,
                "track_name": track.name,
            }
            
            # Input routing types (e.g., "Ext. In", "No Input", other track names)
            try:
                input_types = []
                for rt in getattr(track, "available_input_routing_types", []):
                    input_types.append({
                        "display_name": getattr(rt, "display_name", str(rt)),
                        "identifier": str(rt) if hasattr(rt, "__str__") else None
                    })
                result["input_types"] = input_types
                result["current_input_type"] = getattr(track.input_routing_type, "display_name", None)
            except Exception as e:
                result["input_types_error"] = str(e)
            
            # Output routing types (e.g., "Master", "Sends Only", other track names)
            try:
                output_types = []
                for rt in getattr(track, "available_output_routing_types", []):
                    output_types.append({
                        "display_name": getattr(rt, "display_name", str(rt)),
                        "identifier": str(rt) if hasattr(rt, "__str__") else None
                    })
                result["output_types"] = output_types
                result["current_output_type"] = getattr(track.output_routing_type, "display_name", None)
            except Exception as e:
                result["output_types_error"] = str(e)
            
            # Input channels
            try:
                input_channels = []
                for ch in getattr(track, "available_input_routing_channels", []):
                    input_channels.append({
                        "display_name": getattr(ch, "display_name", str(ch))
                    })
                result["input_channels"] = input_channels
            except Exception as e:
                result["input_channels_error"] = str(e)
            
            # Output channels
            try:
                output_channels = []
                for ch in getattr(track, "available_output_routing_channels", []):
                    output_channels.append({
                        "display_name": getattr(ch, "display_name", str(ch))
                    })
                result["output_channels"] = output_channels
            except Exception as e:
                result["output_channels_error"] = str(e)
            
            return result
        except Exception as e:
            self._log("Error getting routing options: " + str(e))
            raise

    def set_track_output(self, track_index, output_name):
        """
        Set the output routing for a track.
        
        Args:
            track_index: Track index
            output_name: Name of output destination (e.g., "Master", "Sends Only", track name)
        
        Returns:
            Dict with new output routing info
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            
            # Find matching output routing type
            output_name_lower = output_name.lower()
            matched_type = None
            
            for rt in getattr(track, "available_output_routing_types", []):
                display_name = getattr(rt, "display_name", str(rt))
                if display_name.lower() == output_name_lower or output_name_lower in display_name.lower():
                    matched_type = rt
                    break
            
            if matched_type is None:
                available = [getattr(rt, "display_name", str(rt)) for rt in getattr(track, "available_output_routing_types", [])]
                raise ValueError("Output '{0}' not found. Available: {1}".format(output_name, available))
            
            track.output_routing_type = matched_type
            
            return {
                "track_index": track_index,
                "output_routing": getattr(track.output_routing_type, "display_name", str(track.output_routing_type))
            }
        except Exception as e:
            self._log("Error setting track output: " + str(e))
            raise


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
                for idx, return_track in enumerate(getattr(self.song, "return_tracks", [])):
                    name = getattr(return_track, "name", None)
                    if name and target_lower in name.lower():
                        return idx
            except Exception:
                pass
        except Exception:
            pass
        return None

    def _get_device_type(self, device):
        """Get the type of a device"""
        try:
            if getattr(device, "can_have_drum_pads", False):
                return "drum_machine"
            elif getattr(device, "can_have_chains", False):
                return "rack"
            elif "instrument" in getattr(device, "class_display_name", "").lower():
                return "instrument"
            elif "audio_effect" in getattr(device, "class_name", "").lower():
                return "audio_effect"
            elif "midi_effect" in getattr(device, "class_name", "").lower():
                return "midi_effect"
            else:
                return "unknown"
        except:
            return "unknown"

    def get_track_info(self, track_index):
        """Get information about a track"""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            
            track = self.song.tracks[track_index]
            
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
                return_names = [r.name for r in self.song.return_tracks]
                for idx, send in enumerate(track.mixer_device.sends):
                    send_levels.append({
                        "index": idx,
                        "name": return_names[idx] if idx < len(return_names) else "Send {0}".format(idx),
                        "value": send.value,
                        "min": getattr(send, "min", 0.0),
                        "max": getattr(send, "max", 1.0)
                    })
            except Exception as routing_error:
                self._log("Send level introspection failed: {0}".format(str(routing_error)))

            routing_info = self._describe_track_routing(track)

            result = {
                "index": track_index,
                "name": track.name,
                "is_audio_track": track.has_audio_input,
                "is_midi_track": track.has_midi_input,
                "mute": getattr(track, 'mute', False),
                "solo": getattr(track, 'solo', False),
                "arm": getattr(track, 'arm', False),
                "volume": track.mixer_device.volume.value,
                "panning": track.mixer_device.panning.value,
                "clip_slots": clip_slots,
                "devices": devices,
                "routing": routing_info,
                "sends": send_levels
            }
            return result
        except Exception as e:
            self._log("Error getting track info: " + str(e))
            raise

    # =========================================================================
    # Visual Properties
    # =========================================================================

    def set_track_color(self, track_index, color=None, color_index=None):
        """
        Set track color.
        
        Args:
            track_index (int): Track index
            color (int, optional): RGB color value
            color_index (int, optional): Palette index (0-69)
            
        Returns:
            dict: Updated color info
        """
        try:
            track = self.song.tracks[track_index]
            if color is not None:
                track.color = int(color)
            if color_index is not None:
                track.color_index = int(color_index)
            return {"color": track.color, "color_index": track.color_index}
        except Exception as e:
            self._log("Error setting track color: " + str(e))
            raise

    def set_track_fold_state(self, track_index, folded):
        """
        Set track fold state (for group tracks or tracks with devices showing chains).
        
        Args:
            track_index (int): Track index
            folded (bool): True to fold, False to unfold
            
        Returns:
            dict: Updated fold state
        """
        try:
            track = self.song.tracks[track_index]
            if track.is_foldable:
                track.fold_state = bool(folded)
                return {"fold_state": track.fold_state}
            return {"status": "ignored", "message": "Track is not foldable"}
        except Exception as e:
            self._log("Error setting fold state: " + str(e))
            raise

    # =========================================================================
    # Meters
    # =========================================================================

    def get_track_meters(self, track_index):
        """
        Get track meter levels.
        
        Returns:
            dict: Input and Output meter levels (0.0 to 1.0)
        """
        try:
            track = self.song.tracks[track_index]
            return {
                "input_meter_level": track.input_meter_level,
                "input_meter_left": getattr(track, 'input_meter_left', 0.0), # Audio only
                "input_meter_right": getattr(track, 'input_meter_right', 0.0), # Audio only
                "output_meter_level": track.output_meter_level,
                "output_meter_left": getattr(track, 'output_meter_left', 0.0), # Audio only
                "output_meter_right": getattr(track, 'output_meter_right', 0.0), # Audio only
            }
        except Exception as e:
            self._log("Error getting track meters: " + str(e))
            raise

    # =========================================================================
    # Arrangement & Session Ops
    # =========================================================================

    def get_arrangement_clips(self, track_index):
        """
        Get info about clips in the arrangement view.
        
        Returns:
            list: List of dicts with clip info
        """
        try:
            track = self.song.tracks[track_index]
            clips = []
            for clip in track.arrangement_clips:
                clips.append({
                    "name": clip.name,
                    "start_time": clip.start_time,
                    "end_time": clip.end_time,
                    "length": clip.length,
                    "is_audio_clip": clip.is_audio_clip,
                    "is_midi_clip": clip.is_midi_clip,
                    "color": clip.color
                })
            return {"arrangement_clips": clips}
        except Exception as e:
            self._log("Error getting arrangement clips: " + str(e))
            raise

    def jump_in_running_session_clip(self, track_index, beats):
        """
        Jump in the currently running session clip.
        
        Args:
            track_index (int): Track index
            beats (float): Amount to jump (pos/neg)
            
        Returns:
            dict: Status
        """
        try:
            track = self.song.tracks[track_index]
            track.jump_in_running_session_clip(float(beats))
            return {"status": "success", "jumped": beats}
        except Exception as e:
            self._log("Error jumping in session clip: " + str(e))
            raise

    def duplicate_clip_to_arrangement(self, track_index, clip_index, destination_time):
        """
        Duplicate a session clip to arrangement.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            destination_time (float): Time in arrangement (beats)
            
        Returns:
            dict: Info about duplicated clip
        """
        try:
            # Note: Method is on the Track, but takes a Clip object
            # First get the source clip
            import Live
            track = self.song.tracks[track_index]
            clip_slot = track.clip_slots[clip_index]
            if not clip_slot.has_clip:
                raise RuntimeError("No clip in slot")
            
            source_clip = clip_slot.clip
            new_clip = track.duplicate_clip_to_arrangement(source_clip, float(destination_time))
            
            return {
                "status": "success",
                "new_clip_name": new_clip.name,
                "start_time": new_clip.start_time
            }
        except Exception as e:
            self._log("Error duplicating clip to arrangement: " + str(e))
            raise


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

    def list_clips(self, track_pattern=None, match_mode="contains"):
        """List all named clips across tracks, optionally filtering by track name."""
        try:
            results = []
            for t_idx, track in enumerate(self.song.tracks):
                track_name = getattr(track, "name", "Track {0}".format(t_idx))
                if not self._name_matches(track_name, track_pattern, match_mode):
                    continue
                for c_idx, slot in enumerate(track.clip_slots):
                    try:
                        if slot.has_clip:
                            clip = slot.clip
                            clip_name = getattr(clip, "name", "Clip {0}".format(c_idx))
                            results.append({
                                "track_index": t_idx,
                                "track_name": track_name,
                                "clip_index": c_idx,
                                "clip_name": clip_name,
                                "length": getattr(clip, "length", None)
                            })
                    except Exception as clip_err:
                        self._log("Error reading clip at {0}:{1}: {2}".format(t_idx, c_idx, str(clip_err)))
                        continue
            return {"clips": results, "count": len(results)}
        except Exception as e:
            self._log("Error listing clips: " + str(e))
            raise

    def create_clip(self, track_index, clip_index, length):
        """Create a new MIDI clip in the specified track and clip slot"""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            # Check if the clip slot already has a clip
            if clip_slot.has_clip:
                raise Exception("Clip slot already has a clip")
            
            # Create the clip
            clip_slot.create_clip(length)
            
            return {
                "name": clip_slot.clip.name,
                "length": clip_slot.clip.length
            }
        except Exception as e:
            self._log("Error creating clip: " + str(e))
            raise

    def delete_clip(self, track_index, clip_index):
        """Delete a clip from a slot."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            if not slot.has_clip:
                return {"deleted": False, "reason": "slot_empty"}
            clip_name = slot.clip.name
            slot.delete_clip()
            return {"deleted": True, "track_index": track_index, "clip_index": clip_index, "name": clip_name}
        except Exception as e:
            self._log("Error deleting clip: " + str(e))
            raise

    def duplicate_clip(self, track_index, clip_index, target_track_index=None, target_clip_index=None):
        """Duplicate a MIDI clip by copying its notes and loop to a target slot."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            source_track = self.song.tracks[track_index]
            if clip_index < 0 or clip_index >= len(source_track.clip_slots):
                raise IndexError("Clip index out of range")
            source_slot = source_track.clip_slots[clip_index]
            if not source_slot.has_clip:
                raise ValueError("No clip in source slot")

            if target_track_index is None:
                target_track = source_track
            else:
                if target_track_index < 0 or target_track_index >= len(self.song.tracks):
                    raise IndexError("Target track index out of range")
                target_track = self.song.tracks[target_track_index]
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
            self._log("Error duplicating clip: " + str(e))
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
            self._log("Error clearing clip notes: {0}".format(e))
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
            self._log("Error writing clip notes: {0}".format(e))
            raise

    def _read_clip_notes(self, clip):
        """Read all notes from a clip, preferring extended/MPE data when available."""
        try:
            length = getattr(clip, "length", 4.0)
            
            if self._supports_extended_notes(clip):
                # Extended API: (from_time, from_pitch, time_span, pitch_span)
                raw_notes = clip.get_notes_extended(0.0, 0, length, 128)
            else:
                # Standard API: try (from_time, from_pitch, time_span, pitch_span)
                try:
                    raw_notes = clip.get_notes(0.0, 0, length, 128)
                except Exception:
                    # Fallback: some versions use (from_pitch, time_span, from_time, pitch_span)
                    raw_notes = clip.get_notes(0, length, 0.0, 128)
            return [self._note_to_dict(n) for n in raw_notes]
        except Exception as e:
            self._log("Error reading clip notes: {0}".format(e))
            raise
    
    def add_notes_to_clip(self, track_index, clip_index, notes):
        """Add MIDI notes to a clip"""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip = clip_slot.clip
            self._write_clip_notes(clip, notes, replace=False)
            
            return {
                "note_count": len(notes)
            }
        except Exception as e:
            self._log("Error adding notes to clip: " + str(e))
            raise
    
    def set_clip_name(self, track_index, clip_index, name):
        """Set the name of a clip"""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip = clip_slot.clip
            clip.name = name
            
            return {
                "name": clip.name
            }
        except Exception as e:
            self._log("Error setting clip name: " + str(e))
            raise

    def set_clip_loop(self, track_index, clip_index, start, end, loop_on=True):
        """Set loop boundaries and enable/disable looping for a clip."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
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
            self._log("Error setting clip loop: " + str(e))
            raise

    def set_clip_length(self, track_index, clip_index, length):
        """Resize a clip's loop length."""
        try:
            if length is None or length <= 0:
                raise ValueError("Length must be positive")
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
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
            self._log("Error setting clip length: " + str(e))
            raise

    def quantize_clip(self, track_index, clip_index, grid, amount):
        """Quantize MIDI clip notes by a simple grid size (e.g., 16 for 1/16th notes)."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
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
            self._log("Error quantizing clip: " + str(e))
            raise

    def fire_clip(self, track_index, clip_index):
        """Fire a clip"""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            if not clip_slot.has_clip:
                raise Exception("No clip in slot")
            
            clip_slot.fire()
            
            return {
                "fired": True
            }
        except Exception as e:
            self._log("Error firing clip: " + str(e))
            raise

    def fire_clip_by_name(self, clip_pattern, track_pattern=None, match_mode="contains", first_only=True):
        """Fire clips whose names match a pattern (optionally filter by track name)."""
        try:
            if clip_pattern is None or clip_pattern == "":
                raise ValueError("clip_pattern is required")
            fired = []
            for t_idx, track in enumerate(self.song.tracks):
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
            self._log("Error firing clip by name: " + str(e))
            raise

    def trigger_test_midi(self, track_index, clip_index, length, pitch, velocity, duration, start_time, overwrite_clip, fire_clip, cc_number, cc_value, channel):
        """Create/reuse a short MIDI clip and fire a test note/optional CC."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
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
                    self.mcp._send_midi(data)
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
            self._log("Error triggering test MIDI: " + str(e))
            raise

    def stop_clip(self, track_index, clip_index):
        """Stop a clip"""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            
            clip_slot = track.clip_slots[clip_index]
            
            clip_slot.stop()
            
            return {
                "stopped": True
            }
        except Exception as e:
            self._log("Error stopping clip: " + str(e))
            raise

    def add_basic_drum_pattern(self, track_index, clip_index):
        """Add a simple drum pattern to a clip (Kick on 1/3, Snare on 2/4, Hihats)."""
        try:
            # 1 bar length (4.0 beats)
            self.set_clip_length(track_index, clip_index, 4.0)
            self.set_clip_loop(track_index, clip_index, True)
            
            # Kick (C1 = 36)
            self.add_notes_to_clip(track_index, clip_index, [
                {"pitch": 36, "start_time": 0.0, "duration": 0.25, "velocity": 100},
                {"pitch": 36, "start_time": 2.0, "duration": 0.25, "velocity": 100},
            ])
            
            # Snare (D1 = 38)
            self.add_notes_to_clip(track_index, clip_index, [
                {"pitch": 38, "start_time": 1.0, "duration": 0.25, "velocity": 90},
                {"pitch": 38, "start_time": 3.0, "duration": 0.25, "velocity": 90},
            ])
            
            # Closed Hihat (F#1 = 42) - 8th notes
            notes = []
            for i in range(8):
                notes.append({"pitch": 42, "start_time": i * 0.5, "duration": 0.25, "velocity": 80 if i % 2 == 0 else 60})
            self.add_notes_to_clip(track_index, clip_index, notes)
            
            return {"status": "success", "message": "Drum pattern added"}
        except Exception as e:
            self._log("Error adding drum pattern: " + str(e))
            raise

    def get_clip_notes(self, track_index, clip_index):
        """Get all notes from a clip."""
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            
            # Helper to get clip similar to _ensure_clip logic
            clip = None
            if clip_index < len(track.clip_slots):
                slot = track.clip_slots[clip_index]
                if slot.has_clip:
                    clip = slot.clip
            
            if not clip:
                raise ValueError("No clip found at track {0} slot {1}".format(track_index, clip_index))

            # Use the existing _read_clip_notes helper which handles API differences
            notes = self._read_clip_notes(clip)
            return notes
        except Exception as e:
            self._log("Error getting clip notes: {0}".format(str(e)))
            raise

    def transpose_clip(self, track_index, clip_index, semitones):
        """
        Transpose all MIDI notes in a clip by a number of semitones.
        
        Args:
            track_index: Track index
            clip_index: Clip slot index
            semitones: Number of semitones to shift (positive = up, negative = down)
        
        Returns:
            Dict with transposed note count
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            
            if not slot.has_clip:
                raise ValueError("No clip in slot")
            clip = slot.clip
            
            if not getattr(clip, "is_midi_clip", False):
                raise ValueError("Transpose is only supported for MIDI clips")
            
            # Read existing notes
            notes = self._read_clip_notes(clip)
            if not notes:
                return {"transposed": 0, "semitones": semitones}
            
            # Transpose each note
            transposed = []
            for note in notes:
                new_note = dict(note)
                new_pitch = note.get("pitch", 60) + int(semitones)
                # Clamp to valid MIDI range
                new_pitch = max(0, min(127, new_pitch))
                new_note["pitch"] = new_pitch
                transposed.append(new_note)
            
            # Write back
            self._write_clip_notes(clip, transposed, replace=True)
            clip.deselect_all_notes()
            
            return {
                "transposed": len(transposed),
                "semitones": int(semitones),
                "track_index": track_index,
                "clip_index": clip_index
            }
        except Exception as e:
            self._log("Error transposing clip: {0}".format(str(e)))
            raise

    def apply_legato(self, track_index, clip_index, preserve_gaps_below=0.0):
        """
        Extend each note's duration to touch the next note (legato articulation).
        
        Args:
            track_index: Track index
            clip_index: Clip slot index
            preserve_gaps_below: Don't extend notes if gap to next note is smaller than this
                                 (0.0 = always extend, 0.25 = preserve gaps < 1/16th note)
        
        Returns:
            Dict with modified note count
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            
            if not slot.has_clip:
                raise ValueError("No clip in slot")
            clip = slot.clip
            
            if not getattr(clip, "is_midi_clip", False):
                raise ValueError("Legato is only supported for MIDI clips")
            
            # Read existing notes
            notes = self._read_clip_notes(clip)
            if not notes:
                return {"modified": 0}
            
            # Sort by start time, then by pitch (for same-pitch processing)
            notes_sorted = sorted(notes, key=lambda n: (n.get("start_time", 0.0), n.get("pitch", 0)))
            
            # Group by pitch to apply legato per-voice
            from collections import defaultdict
            by_pitch = defaultdict(list)
            for note in notes_sorted:
                by_pitch[note.get("pitch", 60)].append(note)
            
            # Apply legato within each pitch group
            modified_count = 0
            result_notes = []
            
            for pitch, pitch_notes in by_pitch.items():
                for i, note in enumerate(pitch_notes):
                    new_note = dict(note)
                    
                    if i < len(pitch_notes) - 1:
                        # There's a next note at this pitch
                        next_note = pitch_notes[i + 1]
                        note_end = note.get("start_time", 0.0) + note.get("duration", 0.25)
                        next_start = next_note.get("start_time", 0.0)
                        gap = next_start - note_end
                        
                        # Extend if there's a gap and it's larger than threshold
                        if gap > preserve_gaps_below:
                            # Extend duration to touch next note
                            new_duration = next_start - note.get("start_time", 0.0)
                            new_note["duration"] = max(0.01, new_duration - 0.01)  # Small gap to prevent overlap
                            modified_count += 1
                    
                    result_notes.append(new_note)
            
            # Write back
            self._write_clip_notes(clip, result_notes, replace=True)
            clip.deselect_all_notes()
            
            return {
                "modified": modified_count,
                "total_notes": len(result_notes),
                "track_index": track_index,
                "clip_index": clip_index
            }
        except Exception as e:
            self._log("Error applying legato: {0}".format(str(e)))
            raise

    def set_clip_envelope(self, track_index, clip_index, device_index, parameter_name, points):

        """
        Set automation envelope for a clip using Live API.
        
        Args:
            track_index: Track index
            clip_index: Clip slot index
            device_index: Device index on the track
            parameter_name: Name of the parameter to automate
            points: List of [time, value] pairs (time in beats, value 0.0-1.0 normalized)
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            
            if not slot.has_clip:
                raise ValueError("No clip in slot")
            clip = slot.clip
            
            if not getattr(clip, "is_midi_clip", False):
                raise ValueError("Automation envelopes are only supported for MIDI clips via this method")
            
            # Find the target device and parameter
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            
            target_param = None
            for param in device.parameters:
                param_name = getattr(param, "name", "")
                original_name = getattr(param, "original_name", "")
                if param_name == parameter_name or original_name == parameter_name:
                    target_param = param
                    break
            
            if target_param is None:
                raise ValueError("Parameter '{0}' not found on device".format(parameter_name))
            
            # Get or create the automation envelope
            envelope = clip.automation_envelope(target_param)
            if envelope is None:
                envelope = clip.create_automation_envelope(target_param)
            
            if envelope is None:
                raise RuntimeError("Could not create automation envelope for parameter")
            
            # Clear existing automation by inserting a flat line at 0
            # (Live API doesn't have a clear method, so we overwrite)
            
            # Insert automation points using insert_step
            # insert_step(time, duration, value)
            # For smooth curves, use small step durations
            points_written = 0
            for i, point in enumerate(points):
                if len(point) >= 2:
                    time = float(point[0])
                    value = float(point[1])
                    
                    # Normalize value from 0-127 to 0.0-1.0 if needed
                    if value > 1.0:
                        value = value / 127.0
                    
                    # Clamp
                    value = max(target_param.min, min(target_param.max, 
                               target_param.min + value * (target_param.max - target_param.min)))
                    
                    # Calculate step duration (until next point or small default)
                    if i < len(points) - 1 and len(points[i+1]) >= 2:
                        duration = float(points[i+1][0]) - time
                    else:
                        duration = 0.1  # Small duration for last point
                    
                    duration = max(0.01, duration)  # Minimum duration
                    
                    envelope.insert_step(time, duration, value)
                    points_written += 1
            
            self._log("set_clip_envelope: Wrote {0} points to '{1}' on Track {2} Clip {3}".format(
                points_written, parameter_name, track_index, clip_index))
            
            return {
                "status": "success",
                "message": "Envelope set with {0} points".format(points_written),
                "parameter": parameter_name,
                "device_index": device_index
            }
            
        except Exception as e:
            self._log("Error setting clip envelope: " + str(e))
            raise

    # ==================== DRUM RACK MANAGEMENT ====================
    
    def _find_drum_rack(self, track_index, device_index=None):
        """
        Find a Drum Rack device on the specified track.
        Returns (device, device_index) or raises ValueError.
        """
        if track_index < 0 or track_index >= len(self.song.tracks):
            raise IndexError("Track index out of range")
        track = self.song.tracks[track_index]
        
        if device_index is not None:
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            if not hasattr(device, "drum_pads"):
                raise ValueError("Device at index {0} is not a Drum Rack".format(device_index))
            return device, device_index
        
        # Find first Drum Rack on track
        for i, device in enumerate(track.devices):
            if hasattr(device, "drum_pads"):
                return device, i
        
        raise ValueError("No Drum Rack found on track {0}".format(track_index))
    
    def get_drum_rack_info(self, track_index, device_index=None, include_empty=False):
        """
        Get information about a Drum Rack and its pads.
        
        Args:
            track_index: Track containing the Drum Rack
            device_index: Optional specific device index (finds first Drum Rack if not specified)
            include_empty: Include pads without samples
            
        Returns:
            Dict with Drum Rack info and pad details
        """
        try:
            drum_rack, rack_idx = self._find_drum_rack(track_index, device_index)
            
            pads_info = []
            for pad in drum_rack.drum_pads:
                note = pad.note
                name = getattr(pad, "name", "Pad {0}".format(note))
                
                # Check if pad has content
                chains = getattr(pad, "chains", [])
                has_content = len(chains) > 0
                
                if not has_content and not include_empty:
                    continue
                
                pad_data = {
                    "note": note,
                    "name": name,
                    "mute": getattr(pad, "mute", False),
                    "solo": getattr(pad, "solo", False),
                    "has_content": has_content,
                }
                
                # Get choke group if available
                if has_content and len(chains) > 0:
                    chain = chains[0]
                    pad_data["choke_group"] = getattr(chain, "choke_group", None)
                
                # Get sample name if Simpler device
                if has_content and len(chains) > 0:
                    chain = chains[0]
                    for dev in getattr(chain, "devices", []):
                        if hasattr(dev, "sample"):
                            sample = getattr(dev, "sample", None)
                            if sample:
                                pad_data["sample_name"] = getattr(sample, "file_path", "Unknown")
                                break
                
                pads_info.append(pad_data)
            
            return {
                "status": "success",
                "device_name": getattr(drum_rack, "name", "Drum Rack"),
                "device_index": rack_idx,
                "pad_count": len(pads_info),
                "pads": pads_info
            }
            
        except Exception as e:
            self._log("Error getting drum rack info: " + str(e))
            raise
    
    def copy_drum_pad(self, track_index, source_note, dest_note, device_index=None):
        """
        Copy a drum pad from source to destination.
        
        Args:
            track_index: Track containing the Drum Rack
            source_note: MIDI note of source pad (e.g. 36 for kick)
            dest_note: MIDI note of destination pad
            device_index: Optional specific device index
        """
        try:
            drum_rack, rack_idx = self._find_drum_rack(track_index, device_index)
            
            # Find pads by note
            source_pad = None
            dest_pad = None
            for pad in drum_rack.drum_pads:
                if pad.note == source_note:
                    source_pad = pad
                if pad.note == dest_note:
                    dest_pad = pad
            
            if source_pad is None:
                raise ValueError("Source pad (note {0}) not found".format(source_note))
            if dest_pad is None:
                raise ValueError("Destination pad (note {0}) not found".format(dest_note))
            
            # Use the Copy Pad API if available
            if hasattr(drum_rack, "copy_pad"):
                drum_rack.copy_pad(source_note)
                # Select destination and paste
                # Note: Live's LOM doesn't have a direct paste_pad, so we use workaround
                self._log("copy_drum_pad: Copied pad {0} (note: {1}). Paste to {2} manually.".format(
                    getattr(source_pad, "name", ""), source_note, dest_note))
                return {
                    "status": "partial",
                    "message": "Pad copied to clipboard. Paste manually in Live.",
                    "source_note": source_note,
                    "dest_note": dest_note
                }
            else:
                return {
                    "status": "error",
                    "message": "copy_pad API not available in this Live version"
                }
            
        except Exception as e:
            self._log("Error copying drum pad: " + str(e))
            raise
    
    def set_drum_pad_choke_group(self, track_index, note, choke_group, device_index=None):
        """
        Set the choke group for a drum pad.
        
        Args:
            track_index: Track containing the Drum Rack
            note: MIDI note of the pad
            choke_group: Choke group number (0 = none, 1-16 = group)
            device_index: Optional specific device index
        """
        try:
            drum_rack, rack_idx = self._find_drum_rack(track_index, device_index)
            
            # Find pad by note
            target_pad = None
            for pad in drum_rack.drum_pads:
                if pad.note == note:
                    target_pad = pad
                    break
            
            if target_pad is None:
                raise ValueError("Pad (note {0}) not found".format(note))
            
            # Choke group is set on the chain, not the pad directly
            chains = getattr(target_pad, "chains", [])
            if not chains:
                raise ValueError("Pad has no chains (empty pad)")
            
            chain = chains[0]
            if hasattr(chain, "choke_group"):
                chain.choke_group = int(choke_group)
                return {
                    "status": "success",
                    "note": note,
                    "choke_group": choke_group
                }
            else:
                return {
                    "status": "error",
                    "message": "choke_group attribute not available"
                }
            
        except Exception as e:
            self._log("Error setting choke group: " + str(e))
            raise
    
    def mute_drum_pad(self, track_index, note, mute=True, device_index=None):
        """Mute or unmute a drum pad."""
        try:
            drum_rack, rack_idx = self._find_drum_rack(track_index, device_index)
            
            for pad in drum_rack.drum_pads:
                if pad.note == note:
                    pad.mute = mute
                    return {"status": "success", "note": note, "mute": mute}
            
            raise ValueError("Pad (note {0}) not found".format(note))
        except Exception as e:
            self._log("Error muting drum pad: " + str(e))
            raise
    
    def solo_drum_pad(self, track_index, note, solo=True, device_index=None):
        """Solo or unsolo a drum pad."""
        try:
            drum_rack, rack_idx = self._find_drum_rack(track_index, device_index)
            
            for pad in drum_rack.drum_pads:
                if pad.note == note:
                    pad.solo = solo
                    return {"status": "success", "note": note, "solo": solo}
            
            raise ValueError("Pad (note {0}) not found".format(note))
        except Exception as e:
            self._log("Error soloing drum pad: " + str(e))
            raise

    # ==================== GROOVE POOL MANAGEMENT ====================
    
    def get_groove_pool(self):
        """
        Get list of available grooves from the song's groove pool.
        
        Returns:
            Dict with list of grooves and their properties
        """
        try:
            groove_pool = self.song.groove_pool
            grooves = getattr(groove_pool, "grooves", [])
            
            groove_list = []
            for i, groove in enumerate(grooves):
                groove_data = {
                    "index": i,
                    "name": getattr(groove, "name", "Groove {0}".format(i)),
                }
                # Get groove properties if available
                if hasattr(groove, "base"):
                    groove_data["base"] = groove.base
                if hasattr(groove, "quantization"):
                    groove_data["quantization"] = groove.quantization
                if hasattr(groove, "timing_amount"):
                    groove_data["timing_amount"] = groove.timing_amount
                if hasattr(groove, "random_amount"):
                    groove_data["random_amount"] = groove.random_amount
                if hasattr(groove, "velocity_amount"):
                    groove_data["velocity_amount"] = groove.velocity_amount
                    
                groove_list.append(groove_data)
            
            return {
                "status": "success",
                "groove_count": len(groove_list),
                "grooves": groove_list
            }
            
        except Exception as e:
            self._log("Error getting groove pool: " + str(e))
            raise
    
    def set_clip_groove(self, track_index, clip_index, groove_index):
        """
        Apply a groove from the groove pool to a clip.
        
        Args:
            track_index: Track containing the clip
            clip_index: Clip slot index
            groove_index: Index into the groove pool (-1 or None to remove groove)
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            
            if not slot.has_clip:
                raise ValueError("No clip in slot")
            clip = slot.clip
            
            if groove_index is None or groove_index < 0:
                # Remove groove
                if hasattr(clip, "groove"):
                    clip.groove = None
                return {"status": "success", "message": "Groove removed"}
            
            # Get the groove from the pool
            groove_pool = self.song.groove_pool
            grooves = getattr(groove_pool, "grooves", [])
            
            if groove_index >= len(grooves):
                raise IndexError("Groove index out of range")
            
            target_groove = grooves[groove_index]
            
            if hasattr(clip, "groove"):
                clip.groove = target_groove
                return {
                    "status": "success",
                    "groove_name": getattr(target_groove, "name", "Unknown"),
                    "groove_index": groove_index
                }
            else:
                return {
                    "status": "error",
                    "message": "Clip does not support groove assignment"
                }
            
        except Exception as e:
            self._log("Error setting clip groove: " + str(e))
            raise
    
    def commit_groove(self, track_index, clip_index):
        """
        Bake the groove into the clip's notes (commit groove permanently).
        
        Args:
            track_index: Track containing the clip
            clip_index: Clip slot index
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index out of range")
            track = self.song.tracks[track_index]
            
            if clip_index < 0 or clip_index >= len(track.clip_slots):
                raise IndexError("Clip index out of range")
            slot = track.clip_slots[clip_index]
            
            if not slot.has_clip:
                raise ValueError("No clip in slot")
            clip = slot.clip
            
            # Check if clip has a groove applied
            if not hasattr(clip, "groove") or clip.groove is None:
                return {"status": "error", "message": "No groove applied to clip"}
            
            groove_name = getattr(clip.groove, "name", "Unknown")
            
            # Commit the groove (bake into notes)
            if hasattr(clip, "commit_groove"):
                clip.commit_groove()
                return {
                    "status": "success",
                    "message": "Groove '{0}' committed to clip".format(groove_name)
                }
            else:
                return {
                    "status": "error",
                    "message": "commit_groove API not available"
                }
            
        except Exception as e:
            self._log("Error committing groove: " + str(e))
            raise

    # ==================== SIMPLER/SAMPLER CONTROL ====================
    
    def _find_simpler_device(self, track_index, device_index=None):
        """
        Find a Simpler or Sampler device on the specified track.
        Returns (device, device_index, device_type) or raises ValueError.
        """
        if track_index < 0 or track_index >= len(self.song.tracks):
            raise IndexError("Track index out of range")
        track = self.song.tracks[track_index]
        
        if device_index is not None:
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            device = track.devices[device_index]
            dev_name = getattr(device, "class_name", "").lower()
            if "simpler" in dev_name:
                return device, device_index, "simpler"
            elif "sampler" in dev_name:
                return device, device_index, "sampler"
            raise ValueError("Device at index {0} is not a Simpler or Sampler".format(device_index))
        
        # Find first Simpler/Sampler on track
        for i, device in enumerate(track.devices):
            dev_name = getattr(device, "class_name", "").lower()
            if "simpler" in dev_name:
                return device, i, "simpler"
            elif "sampler" in dev_name:
                return device, i, "sampler"
        
        raise ValueError("No Simpler or Sampler found on track {0}".format(track_index))
    
    def get_simpler_info(self, track_index, device_index=None):
        """
        Get information about a Simpler device and its sample.
        """
        try:
            device, dev_idx, dev_type = self._find_simpler_device(track_index, device_index)
            
            info = {
                "status": "success",
                "device_type": dev_type,
                "device_index": dev_idx,
                "device_name": getattr(device, "name", dev_type.title())
            }
            
            # Get sample info if available
            if hasattr(device, "sample") and device.sample:
                sample = device.sample
                info["sample"] = {
                    "file_path": getattr(sample, "file_path", None),
                    "length": getattr(sample, "length", None),
                    "sample_rate": getattr(sample, "sample_rate", None),
                    "warping": getattr(sample, "warping", None),
                }
                if hasattr(sample, "start_marker"):
                    info["sample"]["start_marker"] = sample.start_marker
                if hasattr(sample, "end_marker"):
                    info["sample"]["end_marker"] = sample.end_marker
            
            # Get playback mode
            if hasattr(device, "playback_mode"):
                mode_val = device.playback_mode
                mode_names = {0: "classic", 1: "one_shot", 2: "slice"}
                info["playback_mode"] = mode_names.get(mode_val, str(mode_val))
            
            # Get voices
            if hasattr(device, "voices"):
                info["voices"] = device.voices
                
            return info
            
        except Exception as e:
            self._log("Error getting simpler info: " + str(e))
            raise
    
    def reverse_simpler_sample(self, track_index, device_index=None):
        """
        Reverse the sample in a Simpler device.
        """
        try:
            device, dev_idx, dev_type = self._find_simpler_device(track_index, device_index)
            
            if not hasattr(device, "sample") or device.sample is None:
                return {"status": "error", "message": "No sample loaded in device"}
            
            sample = device.sample
            
            if hasattr(sample, "reverse"):
                sample.reverse()
                return {
                    "status": "success",
                    "message": "Sample reversed",
                    "device_index": dev_idx
                }
            else:
                return {
                    "status": "error",
                    "message": "reverse() API not available"
                }
            
        except Exception as e:
            self._log("Error reversing sample: " + str(e))
            raise
    
    def crop_simpler_sample(self, track_index, device_index=None):
        """
        Crop the sample in a Simpler to the current start/end markers.
        """
        try:
            device, dev_idx, dev_type = self._find_simpler_device(track_index, device_index)
            
            if not hasattr(device, "sample") or device.sample is None:
                return {"status": "error", "message": "No sample loaded in device"}
            
            sample = device.sample
            
            if hasattr(sample, "crop"):
                sample.crop()
                return {
                    "status": "success",
                    "message": "Sample cropped to markers",
                    "device_index": dev_idx
                }
            else:
                return {
                    "status": "error",
                    "message": "crop() API not available"
                }
            
        except Exception as e:
            self._log("Error cropping sample: " + str(e))
            raise
    
    def set_simpler_playback_mode(self, track_index, mode, device_index=None):
        """
        Set the playback mode of a Simpler device.
        
        Args:
            mode: "classic", "one_shot", or "slice" (or 0, 1, 2)
        """
        try:
            device, dev_idx, dev_type = self._find_simpler_device(track_index, device_index)
            
            if not hasattr(device, "playback_mode"):
                return {"status": "error", "message": "playback_mode not available"}
            
            mode_map = {"classic": 0, "one_shot": 1, "slice": 2}
            if isinstance(mode, str):
                mode = mode_map.get(mode.lower(), 0)
            
            device.playback_mode = int(mode)
            
            mode_names = {0: "classic", 1: "one_shot", 2: "slice"}
            return {
                "status": "success",
                "playback_mode": mode_names.get(mode, str(mode)),
                "device_index": dev_idx
            }
            
        except Exception as e:
            self._log("Error setting playback mode: " + str(e))
            raise
    
    def set_simpler_sample_markers(self, track_index, start=None, end=None, device_index=None):
        """
        Set the start and/or end markers of the sample in a Simpler.
        
        Args:
            start: Start marker position (in sample frames)
            end: End marker position (in sample frames)
        """
        try:
            device, dev_idx, dev_type = self._find_simpler_device(track_index, device_index)
            
            if not hasattr(device, "sample") or device.sample is None:
                return {"status": "error", "message": "No sample loaded in device"}
            
            sample = device.sample
            result = {"status": "success", "device_index": dev_idx}
            
            if start is not None and hasattr(sample, "start_marker"):
                sample.start_marker = float(start)
                result["start_marker"] = start
                
            if end is not None and hasattr(sample, "end_marker"):
                sample.end_marker = float(end)
                result["end_marker"] = end
            
            return result
            
        except Exception as e:
            self._log("Error setting sample markers: " + str(e))
            raise
    
    def warp_simpler_sample(self, track_index, warp_mode=None, enable=None, device_index=None):
        """
        Enable/disable warping and set warp mode for a Simpler sample.
        
        Args:
            warp_mode: "beats", "tones", "texture", "repitch", "complex", "complex_pro"
            enable: True/False to enable/disable warping
        """
        try:
            device, dev_idx, dev_type = self._find_simpler_device(track_index, device_index)
            
            if not hasattr(device, "sample") or device.sample is None:
                return {"status": "error", "message": "No sample loaded in device"}
            
            sample = device.sample
            result = {"status": "success", "device_index": dev_idx}
            
            if enable is not None and hasattr(sample, "warping"):
                sample.warping = bool(enable)
                result["warping"] = sample.warping
            
            if warp_mode is not None and hasattr(sample, "warp_mode"):
                mode_map = {"beats": 0, "tones": 1, "texture": 2, "repitch": 3, "complex": 4, "complex_pro": 5}
                if isinstance(warp_mode, str):
                    warp_mode = mode_map.get(warp_mode.lower(), 0)
                sample.warp_mode = int(warp_mode)
                result["warp_mode"] = warp_mode
            
            return result
            
        except Exception as e:
            self._log("Error warping sample: " + str(e))
            raise

    # ==================== ARRANGEMENT VIEW ====================
    
    def get_arrangement_info(self):
        """
        Get information about the arrangement view.
        """
        try:
            song = self.song
            
            info = {
                "status": "success",
                "is_playing": song.is_playing,
                "current_song_time": song.current_song_time,
                "song_length": getattr(song, "song_length", None),
                "loop_start": getattr(song, "loop_start", None),
                "loop_length": getattr(song, "loop_length", None),
                "loop": getattr(song, "loop", None),
            }
            
            # Get cue points
            if hasattr(song, "cue_points"):
                info["cue_points"] = []
                for i, cue in enumerate(song.cue_points):
                    info["cue_points"].append({
                        "index": i,
                        "name": getattr(cue, "name", "Cue {0}".format(i)),
                        "time": getattr(cue, "time", 0.0)
                    })
            
            return info
            
        except Exception as e:
            self._log("Error getting arrangement info: " + str(e))
            raise
    
    def create_cue_point(self, time, name=None):
        """
        Create a new cue point (locator) in the arrangement.
        
        Args:
            time: Position in beats
            name: Optional name for the cue point
        """
        try:
            song = self.song
            
            if hasattr(song, "create_cue_point"):
                song.create_cue_point(float(time))
                
                # Try to name it if we have cue_points access
                if name and hasattr(song, "cue_points"):
                    cues = list(song.cue_points)
                    # Find the cue point we just created (should be last or at time)
                    for cue in reversed(cues):
                        if abs(getattr(cue, "time", 0) - time) < 0.01:
                            if hasattr(cue, "name"):
                                cue.name = name
                            break
                
                return {
                    "status": "success",
                    "time": time,
                    "name": name
                }
            else:
                return {
                    "status": "error",
                    "message": "create_cue_point API not available"
                }
            
        except Exception as e:
            self._log("Error creating cue point: " + str(e))
            raise
    
    def delete_cue_point(self, index):
        """
        Delete a cue point by index.
        """
        try:
            song = self.song
            
            if not hasattr(song, "cue_points"):
                return {"status": "error", "message": "cue_points not available"}
            
            cues = list(song.cue_points)
            if index < 0 or index >= len(cues):
                raise IndexError("Cue point index out of range")
            
            cue = cues[index]
            if hasattr(cue, "delete"):
                cue.delete()
                return {"status": "success", "deleted_index": index}
            else:
                return {"status": "error", "message": "delete() not available on cue point"}
            
        except Exception as e:
            self._log("Error deleting cue point: " + str(e))
            raise
    
    def jump_to_cue_point(self, index):
        """
        Jump playhead to a cue point.
        """
        try:
            song = self.song
            
            if not hasattr(song, "cue_points"):
                return {"status": "error", "message": "cue_points not available"}
            
            cues = list(song.cue_points)
            if index < 0 or index >= len(cues):
                raise IndexError("Cue point index out of range")
            
            cue = cues[index]
            cue_time = getattr(cue, "time", 0.0)
            
            if hasattr(cue, "jump"):
                cue.jump()
            else:
                song.current_song_time = cue_time
            
            return {
                "status": "success",
                "jumped_to": cue_time,
                "cue_name": getattr(cue, "name", "Cue {0}".format(index))
            }
            
        except Exception as e:
            self._log("Error jumping to cue point: " + str(e))
            raise
    
    def set_arrangement_loop(self, start, length, enable=True):
        """
        Set the arrangement loop region.
        
        Args:
            start: Loop start position in beats
            length: Loop length in beats
            enable: Enable/disable looping
        """
        try:
            song = self.song
            
            if hasattr(song, "loop_start"):
                song.loop_start = float(start)
            if hasattr(song, "loop_length"):
                song.loop_length = float(length)
            if hasattr(song, "loop"):
                song.loop = bool(enable)
            
            return {
                "status": "success",
                "loop_start": start,
                "loop_length": length,
                "loop_enabled": enable
            }
            
        except Exception as e:
            self._log("Error setting arrangement loop: " + str(e))
            raise
    
    def set_song_time(self, time):
        """
        Set the playhead position in the arrangement.
        
        Args:
            time: Position in beats
        """
        try:
            song = self.song
            song.current_song_time = float(time)
            
            return {
                "status": "success",
                "current_song_time": song.current_song_time
            }
            
        except Exception as e:
            self._log("Error setting song time: " + str(e))
            raise
    
    def scrub_arrangement(self, time):
        """
        Scrub to a position in the arrangement (with audio).
        
        Args:
            time: Position in beats
        """
        try:
            song = self.song
            
            if hasattr(song, "scrub_by"):
                current = song.current_song_time
                delta = float(time) - current
                song.scrub_by(delta)
                return {"status": "success", "scrubbed_to": time}
            else:
                song.current_song_time = float(time)
                return {"status": "success", "jumped_to": time, "note": "scrub_by not available, used jump"}
            
        except Exception as e:
            self._log("Error scrubbing arrangement: " + str(e))
            raise

