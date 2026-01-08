"""
Session Handler Module for AbletonMCP Remote Script.

This module handles session-level operations including transport control,
scene management, and global song state.

Key Responsibilities:
    - Transport (play, stop, tempo, time signature)
    - Scene CRUD (create, delete, duplicate, fire)
    - Session info and song context for LLM awareness
    
For Future Agents:
    - This handler is instantiated as `session_handler` on the main MCP
    - Song reference is cached in self.song for efficiency
    - get_song_context() provides comprehensive state for AI context
    - Scene operations use 0-based indexing
    
Common Patterns:
    >>> # Get comprehensive song state for AI
    >>> context = session_handler.get_song_context(include_clips=True)
    
    >>> # Fire scenes by pattern matching
    >>> session_handler.fire_scene_by_name("Verse", match_mode="startswith")
"""
from __future__ import absolute_import, print_function, unicode_literals
import logging


class SessionHandler(object):
    """
    Handler for session-level operations in AbletonMCP.
    
    Manages transport control (play/stop/tempo), scene operations,
    and provides comprehensive song context for LLM awareness.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
        song: Cached reference to the Live Song object
        
    Note:
        Scene indices are 0-based and correspond to clip slot rows.
    """
    def __init__(self, mcp_instance):
        self.mcp = mcp_instance
        self.song = self.mcp.song()
        
    def _log(self, message):
        if hasattr(self.mcp, 'log_message'):
            self.mcp.log_message(message)

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

    def get_session_info(self):
        """Get information about the current session"""
        try:
            result = {
                "tempo": self.song.tempo,
                "signature_numerator": self.song.signature_numerator,
                "signature_denominator": self.song.signature_denominator,
                "track_count": len(self.song.tracks),
                "return_track_count": len(self.song.return_tracks),
                "master_track": {
                    "name": "Master",
                    "volume": self.song.master_track.mixer_device.volume.value,
                    "panning": self.song.master_track.mixer_device.panning.value
                }
            }
            return result
        except Exception as e:
            self._log("Error getting session info: " + str(e))
            raise

    def set_tempo(self, tempo):
        """Set the tempo of the session"""
        try:
            self.song.tempo = float(tempo)
            return {
                "tempo": self.song.tempo
            }
        except Exception as e:
            self._log("Error setting tempo: " + str(e))
            raise

    def set_time_signature(self, numerator, denominator):
        """Set the global time signature."""
        try:
            self.song.signature_numerator = int(numerator)
            self.song.signature_denominator = int(denominator)
            return {
                "signature_numerator": self.song.signature_numerator,
                "signature_denominator": self.song.signature_denominator
            }
        except Exception as e:
            self._log("Error setting time signature: " + str(e))
            raise
    
    def start_playback(self):
        """Start playback"""
        try:
            self.song.is_playing = True
            return {"playing": True}
        except Exception as e:
            self._log("Error starting playback: " + str(e))
            raise

    def stop_playback(self):
        """Stop playback"""
        try:
            self.song.is_playing = False
            return {"playing": False}
        except Exception as e:
            self._log("Error stopping playback: " + str(e))
            raise

    def create_scene(self, index=-1, name=None):
        """Create a new scene."""
        try:
            if index is None or index < 0:
                index = len(self.song.scenes)
            self.song.create_scene(index)
            created_index = min(index, len(self.song.scenes) - 1)
            scene = self.song.scenes[created_index]
            if name:
                scene.name = name
            return {"index": created_index, "name": scene.name}
        except Exception as e:
            self._log("Error creating scene: " + str(e))
            raise

    def delete_scene(self, index):
        """Delete a scene by index."""
        try:
            if index < 0 or index >= len(self.song.scenes):
                raise IndexError("Scene index out of range")
            name = self.song.scenes[index].name
            self.song.delete_scene(index)
            return {"deleted": True, "index": index, "name": name}
        except Exception as e:
            self._log("Error deleting scene: " + str(e))
            raise

    def duplicate_scene(self, index):
        """Duplicate a scene."""
        try:
            if index < 0 or index >= len(self.song.scenes):
                raise IndexError("Scene index out of range")
            self.song.duplicate_scene(index)
            new_index = index + 1
            scene = self.song.scenes[new_index]
            return {"index": new_index, "name": scene.name, "duplicated_from": index}
        except Exception as e:
            self._log("Error duplicating scene: " + str(e))
            raise

    def fire_scene(self, index):
        """Launch a scene."""
        try:
            if index < 0 or index >= len(self.song.scenes):
                raise IndexError("Scene index out of range")
            scene = self.song.scenes[index]
            scene.fire()
            return {"fired": True, "index": index, "name": scene.name}
        except Exception as e:
            self._log("Error firing scene: " + str(e))
            raise

    def fire_scene_by_name(self, pattern, match_mode="contains", first_only=True):
        """Launch scenes matching a name pattern."""
        try:
            if pattern is None or pattern == "":
                raise ValueError("pattern is required")
            fired = []
            for idx, scene in enumerate(self.song.scenes):
                if self._name_matches(scene.name, pattern, match_mode):
                    scene.fire()
                    fired.append({"index": idx, "name": scene.name})
                    if first_only:
                        return {"fired": fired}
            if not fired:
                raise ValueError("No scenes matched pattern '{0}'".format(pattern))
            return {"fired": fired}
        except Exception as e:
            self._log("Error firing scene by name: " + str(e))
            raise

    def stop_scene(self, index):
        """Stop all clips in a scene."""
        try:
            if index < 0 or index >= len(self.song.scenes):
                raise IndexError("Scene index out of range")
            scene = self.song.scenes[index]

            stopped_slots = 0
            for track in self.song.tracks:
                try:
                    if index < len(track.clip_slots):
                        track.clip_slots[index].stop()
                        stopped_slots += 1
                except Exception as slot_err:
                    self._log("Error stopping slot {0} on track {1}: {2}".format(index, getattr(track, "name", "unknown"), slot_err))

            try:
                if getattr(self.song.view, "selected_scene", None) == scene:
                    self.song.stop_all_clips()
            except Exception as global_stop_err:
                self._log("Error issuing global stop_all_clips: {0}".format(global_stop_err))

            return {"index": index, "name": scene.name, "stopped": True, "stopped_slots": stopped_slots}
        except Exception as e:
            self._log("Error stopping scene: " + str(e))
            raise

    def get_song_context(self, include_clips=False):
        """
        Get a comprehensive snapshot of the current song state.
        Returns tracks, scenes, tempo, and transport state.
        Designed for LLM context awareness.
        """
        try:
            tracks = []
            for idx, track in enumerate(self.song.tracks):
                track_info = {
                    "index": idx,
                    "name": track.name,
                    "type": "midi" if track.has_midi_input else "audio",
                    "armed": track.arm,
                    "muted": track.mute,
                    "soloed": track.solo,
                    "devices": [],
                    "has_clips": False
                }
                
                # Devices
                for dev_idx, device in enumerate(track.devices):
                    track_info["devices"].append({
                        "index": dev_idx,
                        "name": device.name,
                        "class_name": device.class_name
                    })
                
                # Clip info
                clips = []
                for slot_idx, slot in enumerate(track.clip_slots):
                    if slot.has_clip:
                        track_info["has_clips"] = True
                        if include_clips:
                            clip = slot.clip
                            clips.append({
                                "slot": slot_idx,
                                "name": clip.name,
                                "length": clip.length,
                                "playing": clip.is_playing
                            })
                
                if include_clips and clips:
                    track_info["clips"] = clips
                
                tracks.append(track_info)
            
            # Scenes
            scenes = []
            for idx, scene in enumerate(self.song.scenes):
                scenes.append({
                    "index": idx,
                    "name": scene.name
                })
            
            result = {
                "tempo": self.song.tempo,
                "time_signature": "{0}/{1}".format(
                    self.song.signature_numerator,
                    self.song.signature_denominator
                ),
                "playing": self.song.is_playing,
                "track_count": len(tracks),
                "scene_count": len(scenes),
                "tracks": tracks,
                "scenes": scenes
            }
            return result
        except Exception as e:
            self._log("Error getting song context: " + str(e))
            raise

    def set_record_mode(self, enabled):
        """Set the global arrangement record mode."""
        try:
            self.song.record_mode = bool(enabled)
            return {"record_mode": self.song.record_mode}
        except Exception as e:
            self._log("Error setting record mode: " + str(e))
            raise

    def trigger_session_record(self, record_length=None):
        """Trigger session recording (Session Record button)."""
        try:
            # Toggle session record
            self.song.session_record = not self.song.session_record
            return {"session_record": self.song.session_record}
        except Exception as e:
            self._log("Error triggering session record: " + str(e))
            raise

    def capture_midi(self, destination=0):
        """Capture MIDI (Capture)."""
        try:
            if hasattr(self.song, "capture_midi"):
                self.song.capture_midi(destination)
                return {"captured": True}
            else:
                return {"captured": False, "error": "capture_midi not supported"}
        except Exception as e:
            self._log("Error capturing MIDI: " + str(e))
            raise

    def set_overdub(self, enabled):
        """Set the Overdub (OVR) state (Arrangement Overdub)."""
        try:
            if hasattr(self.song, "arrangement_overdub"):
                self.song.arrangement_overdub = bool(enabled)
            return {
                "arrangement_overdub": getattr(self.song, "arrangement_overdub", False),
                "session_record": self.song.session_record
            }
        except Exception as e:
            self._log("Error setting overdub: " + str(e))
            raise
