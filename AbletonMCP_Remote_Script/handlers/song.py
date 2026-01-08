"""
Song Handler Module for AbletonMCP Remote Script.

This module handles song-level operations that affect global state including
transport control, recording, undo/redo, and navigation.

Key Responsibilities:
    - MIDI capture (capture_midi)
    - Session/Arrangement recording
    - Undo/Redo operations
    - Tempo controls (tap_tempo, nudge)
    - Metronome control
    - Punch in/out
    - Loop control
    - Navigation (cue points, time jumping)
    - Global clip operations

For Future Agents:
    - This handler is instantiated as `song_handler` on the main MCP
    - All methods access Song via self.song property from HandlerBase
    - Song operations affect global state - use with care
    - Many properties are observable (can add listeners)

Live 11 API Reference:
    - Live.Song.Song class
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class SongHandler(HandlerBase):
    """
    Handler for song-level operations in AbletonMCP.
    
    Provides access to global transport, recording, undo/redo,
    metronome, and navigation functions that affect the entire Live Set.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
        
    Note:
        These operations affect the global song state and should be
        used carefully in automation contexts.
    """
    
    # =========================================================================
    # MIDI Capture
    # =========================================================================
    
    def capture_midi(self, destination=0):
        """
        Capture recently played MIDI material into a clip.
        
        Captures MIDI that was recently played through armed tracks and
        creates a new clip containing that material.
        
        Args:
            destination (int): Where to insert the captured clip
                - 0 = auto (current view)
                - 1 = session view
                - 2 = arrangement view
        
        Returns:
            dict: Result with capture status
                - captured (bool): True if MIDI was captured
                - can_capture (bool): True if capture was possible
        
        Example:
            >>> song_handler.capture_midi(1)  # Capture to session
            {"captured": True, "can_capture": True}
        
        Live API:
            Song.capture_midi(destination)
            Song.can_capture_midi (property)
        """
        try:
            can_capture = self.song.can_capture_midi
            if can_capture:
                self.song.capture_midi(destination)
            return {
                "captured": can_capture,
                "can_capture": can_capture
            }
        except Exception as e:
            self._log("Error capturing MIDI: " + str(e))
            raise
    
    # =========================================================================
    # Recording Control
    # =========================================================================
    
    def set_record_mode(self, enabled):
        """
        Set the arrangement record button state.
        
        When enabled, playback will record to the arrangement view.
        
        Args:
            enabled (bool): True to enable arrangement recording
        
        Returns:
            dict: Current record mode state
        
        Live API:
            Song.record_mode (bool property)
        """
        try:
            self.song.record_mode = bool(enabled)
            return {"record_mode": self.song.record_mode}
        except Exception as e:
            self._log("Error setting record mode: " + str(e))
            raise
    
    def get_record_mode(self):
        """Get the current arrangement record button state."""
        try:
            return {"record_mode": self.song.record_mode}
        except Exception as e:
            self._log("Error getting record mode: " + str(e))
            raise
    
    def set_session_record(self, enabled):
        """
        Set the session overdub button state.
        
        When enabled, recording into session clips will overdub.
        
        Args:
            enabled (bool): True to enable session overdub
        
        Returns:
            dict: Current session record state
        
        Live API:
            Song.session_record (bool property)
        """
        try:
            self.song.session_record = bool(enabled)
            return {"session_record": self.song.session_record}
        except Exception as e:
            self._log("Error setting session record: " + str(e))
            raise
    
    def trigger_session_record(self, record_length=None):
        """
        Start recording in the selected or next empty slot.
        
        The track must be armed. If record_length is provided,
        recording will stop after that many beats.
        
        Args:
            record_length (float, optional): Recording length in beats.
                If None, records until manually stopped.
        
        Returns:
            dict: Recording status
        
        Live API:
            Song.trigger_session_record(record_length)
        """
        try:
            if record_length is not None:
                self.song.trigger_session_record(float(record_length))
            else:
                self.song.trigger_session_record()
            return {"recording_triggered": True}
        except Exception as e:
            self._log("Error triggering session record: " + str(e))
            raise
    
    def set_overdub(self, enabled):
        """
        Set MIDI arrangement overdub state.
        
        When enabled with record_mode, MIDI recording will overdub
        existing clips in the arrangement.
        
        Args:
            enabled (bool): True to enable overdub
        
        Returns:
            dict: Current overdub state
        
        Live API:
            Song.overdub (bool property)
            Song.arrangement_overdub (bool property)
        """
        try:
            self.song.overdub = bool(enabled)
            return {"overdub": self.song.overdub}
        except Exception as e:
            self._log("Error setting overdub: " + str(e))
            raise
    
    def set_punch_in(self, enabled):
        """
        Set punch-in state.
        
        When enabled, recording starts at the loop start point.
        
        Args:
            enabled (bool): True to enable punch-in
        
        Returns:
            dict: Current punch-in state
        
        Live API:
            Song.punch_in (bool property)
        """
        try:
            self.song.punch_in = bool(enabled)
            return {"punch_in": self.song.punch_in}
        except Exception as e:
            self._log("Error setting punch in: " + str(e))
            raise
    
    def set_punch_out(self, enabled):
        """
        Set punch-out state.
        
        When enabled, recording stops at the loop end point.
        
        Args:
            enabled (bool): True to enable punch-out
        
        Returns:
            dict: Current punch-out state
        
        Live API:
            Song.punch_out (bool property)
        """
        try:
            self.song.punch_out = bool(enabled)
            return {"punch_out": self.song.punch_out}
        except Exception as e:
            self._log("Error setting punch out: " + str(e))
            raise
    
    # =========================================================================
    # Undo/Redo
    # =========================================================================
    
    def undo(self):
        """
        Undo the last operation.
        
        Returns:
            dict: Result with undo status
                - undone (bool): True if undo was performed
                - can_undo (bool): True if another undo is available
        
        Live API:
            Song.undo()
            Song.can_undo (bool property)
        """
        try:
            can_undo = self.song.can_undo
            if can_undo:
                self.song.undo()
            return {
                "undone": can_undo,
                "can_undo": self.song.can_undo
            }
        except Exception as e:
            self._log("Error performing undo: " + str(e))
            raise
    
    def redo(self):
        """
        Redo the last undone operation.
        
        Returns:
            dict: Result with redo status
                - redone (bool): True if redo was performed
                - can_redo (bool): True if another redo is available
        
        Live API:
            Song.redo()
            Song.can_redo (bool property)
        """
        try:
            can_redo = self.song.can_redo
            if can_redo:
                self.song.redo()
            return {
                "redone": can_redo,
                "can_redo": self.song.can_redo
            }
        except Exception as e:
            self._log("Error performing redo: " + str(e))
            raise
    
    def get_undo_state(self):
        """
        Get the current undo/redo availability.
        
        Returns:
            dict: Undo/redo state
                - can_undo (bool)
                - can_redo (bool)
        """
        try:
            return {
                "can_undo": self.song.can_undo,
                "can_redo": self.song.can_redo
            }
        except Exception as e:
            self._log("Error getting undo state: " + str(e))
            raise
    
    # =========================================================================
    # Metronome & Tempo
    # =========================================================================
    
    def set_metronome(self, enabled):
        """
        Enable or disable the metronome.
        
        Args:
            enabled (bool): True to enable metronome
        
        Returns:
            dict: Current metronome state
        
        Live API:
            Song.metronome (bool property)
        """
        try:
            self.song.metronome = bool(enabled)
            return {"metronome": self.song.metronome}
        except Exception as e:
            self._log("Error setting metronome: " + str(e))
            raise
    
    def get_metronome(self):
        """Get the current metronome state."""
        try:
            return {"metronome": self.song.metronome}
        except Exception as e:
            self._log("Error getting metronome: " + str(e))
            raise
    
    def tap_tempo(self):
        """
        Tap tempo - call repeatedly to set tempo by tapping.
        
        The tempo is calculated based on the time between
        consecutive calls to this function.
        
        Returns:
            dict: Current tempo after tap
        
        Live API:
            Song.tap_tempo()
        """
        try:
            self.song.tap_tempo()
            return {"tempo": self.song.tempo}
        except Exception as e:
            self._log("Error tapping tempo: " + str(e))
            raise
    
    def nudge_tempo(self, direction, active=True):
        """
        Nudge the tempo up or down.
        
        Simulates pressing/releasing the tempo nudge buttons.
        
        Args:
            direction (str): "up" or "down"
            active (bool): True to press, False to release
        
        Returns:
            dict: Current tempo
        
        Live API:
            Song.nudge_up (bool property)
            Song.nudge_down (bool property)
        """
        try:
            if direction == "up":
                self.song.nudge_up = bool(active)
            elif direction == "down":
                self.song.nudge_down = bool(active)
            else:
                raise ValueError("direction must be 'up' or 'down'")
            return {"tempo": self.song.tempo, "direction": direction, "active": active}
        except Exception as e:
            self._log("Error nudging tempo: " + str(e))
            raise
    
    def set_swing_amount(self, amount):
        """
        Set the global swing amount.
        
        This affects MIDI recording quantization and Clip.quantize().
        
        Args:
            amount (float): Swing amount from 0.0 to 1.0
        
        Returns:
            dict: Current swing amount
        
        Live API:
            Song.swing_amount (float property, 0.0-1.0)
        """
        try:
            # Clamp to valid range
            amount = max(0.0, min(1.0, float(amount)))
            self.song.swing_amount = amount
            return {"swing_amount": self.song.swing_amount}
        except Exception as e:
            self._log("Error setting swing amount: " + str(e))
            raise
    
    # =========================================================================
    # Playback Control
    # =========================================================================
    
    def continue_playing(self):
        """
        Continue playback from the current position.
        
        Unlike start_playing, this resumes from where playback
        stopped rather than jumping to the insert marker.
        
        Returns:
            dict: Playback state
        
        Live API:
            Song.continue_playing()
        """
        try:
            self.song.continue_playing()
            return {"playing": True, "continued": True}
        except Exception as e:
            self._log("Error continuing playback: " + str(e))
            raise
    
    def play_selection(self):
        """
        Play the current arrangement selection.
        
        If no selection is set, does nothing.
        
        Returns:
            dict: Playback state
        
        Live API:
            Song.play_selection()
        """
        try:
            self.song.play_selection()
            return {"playing_selection": True}
        except Exception as e:
            self._log("Error playing selection: " + str(e))
            raise
    
    def stop_all_clips(self, quantized=True):
        """
        Stop all playing clips.
        
        Args:
            quantized (bool): If True, stops are quantized to the
                global launch quantization. If False, stops immediately.
        
        Returns:
            dict: Stop result
        
        Live API:
            Song.stop_all_clips(quantized)
        """
        try:
            self.song.stop_all_clips(1 if quantized else 0)
            return {"stopped": True, "quantized": quantized}
        except Exception as e:
            self._log("Error stopping all clips: " + str(e))
            raise
    
    # =========================================================================
    # Navigation
    # =========================================================================
    
    def jump_by(self, beats):
        """
        Jump forward or backward by the specified amount.
        
        Args:
            beats (float): Amount to jump in beats. Positive = forward.
        
        Returns:
            dict: New song time
        
        Live API:
            Song.jump_by(beats)
        """
        try:
            self.song.jump_by(float(beats))
            return {"current_song_time": self.song.current_song_time}
        except Exception as e:
            self._log("Error jumping by beats: " + str(e))
            raise
    
    def jump_to_next_cue(self):
        """
        Jump to the next cue point to the right.
        
        Returns:
            dict: Jump result and new position
        
        Live API:
            Song.jump_to_next_cue()
            Song.can_jump_to_next_cue (bool property)
        """
        try:
            can_jump = self.song.can_jump_to_next_cue
            if can_jump:
                self.song.jump_to_next_cue()
            return {
                "jumped": can_jump,
                "current_song_time": self.song.current_song_time
            }
        except Exception as e:
            self._log("Error jumping to next cue: " + str(e))
            raise
    
    def jump_to_prev_cue(self):
        """
        Jump to the previous cue point to the left.
        
        Returns:
            dict: Jump result and new position
        
        Live API:
            Song.jump_to_prev_cue()
            Song.can_jump_to_prev_cue (bool property)
        """
        try:
            can_jump = self.song.can_jump_to_prev_cue
            if can_jump:
                self.song.jump_to_prev_cue()
            return {
                "jumped": can_jump,
                "current_song_time": self.song.current_song_time
            }
        except Exception as e:
            self._log("Error jumping to prev cue: " + str(e))
            raise
    
    def set_or_delete_cue(self):
        """
        Toggle cue point at current playback position.
        
        If a cue point exists at the current position, deletes it.
        Otherwise, creates a new cue point.
        
        Returns:
            dict: Cue point operation result
        
        Live API:
            Song.set_or_delete_cue()
            Song.is_cue_point_selected()
        """
        try:
            self.song.set_or_delete_cue()
            return {
                "toggled": True,
                "current_song_time": self.song.current_song_time
            }
        except Exception as e:
            self._log("Error toggling cue point: " + str(e))
            raise
    
    # =========================================================================
    # Loop Control
    # =========================================================================
    
    def set_loop(self, enabled=None, start=None, length=None):
        """
        Configure the arrangement loop.
        
        All parameters are optional - only provided values are changed.
        
        Args:
            enabled (bool, optional): Enable/disable loop
            start (float, optional): Loop start in beats
            length (float, optional): Loop length in beats
        
        Returns:
            dict: Current loop state
        
        Live API:
            Song.loop (bool property)
            Song.loop_start (float property)
            Song.loop_length (float property)
        """
        try:
            if enabled is not None:
                self.song.loop = bool(enabled)
            if start is not None:
                self.song.loop_start = float(start)
            if length is not None:
                self.song.loop_length = float(length)
            
            return {
                "loop": self.song.loop,
                "loop_start": self.song.loop_start,
                "loop_length": self.song.loop_length
            }
        except Exception as e:
            self._log("Error setting loop: " + str(e))
            raise
    
    def get_loop(self):
        """Get the current arrangement loop state."""
        try:
            return {
                "loop": self.song.loop,
                "loop_start": self.song.loop_start,
                "loop_length": self.song.loop_length
            }
        except Exception as e:
            self._log("Error getting loop: " + str(e))
            raise
    
    # =========================================================================
    # Quantization Settings
    # =========================================================================
    
    def set_clip_trigger_quantization(self, quantization):
        """
        Set the global clip launch quantization.
        
        Args:
            quantization (int): Quantization index
                0 = None, 1 = 8 Bars, 2 = 4 Bars, 3 = 2 Bars, 4 = 1 Bar,
                5 = 1/2, 6 = 1/2T, 7 = 1/4, 8 = 1/4T, 9 = 1/8, 10 = 1/8T,
                11 = 1/16, 12 = 1/16T, 13 = 1/32
        
        Returns:
            dict: Current quantization setting
        
        Live API:
            Song.clip_trigger_quantization (int property)
        """
        try:
            self.song.clip_trigger_quantization = int(quantization)
            return {"clip_trigger_quantization": self.song.clip_trigger_quantization}
        except Exception as e:
            self._log("Error setting clip trigger quantization: " + str(e))
            raise
    
    def set_midi_recording_quantization(self, quantization):
        """
        Set the MIDI recording quantization.
        
        Args:
            quantization (int): Quantization index
                0 = None, 1 = 1/4, 2 = 1/8, 3 = 1/8T, 4 = 1/8 + 1/8T,
                5 = 1/16, 6 = 1/16T, 7 = 1/16 + 1/16T, 8 = 1/32
        
        Returns:
            dict: Current quantization setting
        
        Live API:
            Song.midi_recording_quantization (int property)
        """
        try:
            self.song.midi_recording_quantization = int(quantization)
            return {"midi_recording_quantization": self.song.midi_recording_quantization}
        except Exception as e:
            self._log("Error setting MIDI recording quantization: " + str(e))
            raise
    
    # =========================================================================
    # Return Tracks
    # =========================================================================
    
    def create_return_track(self):
        """
        Create a new return track at the end of the return track list.
        
        Returns:
            dict: New return track count
        
        Live API:
            Song.create_return_track()
        """
        try:
            self.song.create_return_track()
            return {
                "created": True,
                "return_track_count": len(self.song.return_tracks)
            }
        except Exception as e:
            self._log("Error creating return track: " + str(e))
            raise
    
    def delete_return_track(self, index):
        """
        Delete a return track by index.
        
        Args:
            index (int): Return track index (0-based)
        
        Returns:
            dict: Deletion result
        
        Live API:
            Song.delete_return_track(index)
        """
        try:
            if index < 0 or index >= len(self.song.return_tracks):
                raise IndexError("Return track index out of range")
            self.song.delete_return_track(index)
            return {
                "deleted": True,
                "index": index,
                "return_track_count": len(self.song.return_tracks)
            }
        except Exception as e:
            self._log("Error deleting return track: " + str(e))
            raise
    
    def get_return_tracks(self):
        """
        Get information about all return tracks.
        
        Returns:
            dict: Return tracks info with name, color, and volume
        
        Live API:
            Song.return_tracks (Vector property)
        """
        try:
            tracks = []
            for idx, track in enumerate(self.song.return_tracks):
                tracks.append({
                    "index": idx,
                    "name": track.name,
                    "color": track.color,
                    "mute": track.mute,
                    "solo": track.solo,
                    "volume": track.mixer_device.volume.value
                })
            return {
                "count": len(tracks),
                "return_tracks": tracks
            }
        except Exception as e:
            self._log("Error getting return tracks: " + str(e))
            raise
    
    # =========================================================================
    # Scrubbing & Groove
    # =========================================================================
    
    def scrub_by(self, beats):
        """
        Scrub the playback position by a number of beats.
        
        Args:
            beats (float): Beats to scrub (positive=forward, negative=backward)
            
        Returns:
            dict: New capture time
            
        Live API:
            Song.scrub_by(beats)
        """
        try:
            self.song.scrub_by(float(beats))
            return {"current_song_time": self.song.current_song_time}
        except Exception as e:
            self._log("Error scrubbing: " + str(e))
            raise

    def set_groove_amount(self, amount):
        """
        Set the global groove amount.
        
        Args:
            amount (float): Groove amount (0.0 to 1.0) # Check range, usually 0-100 or 0-1
            
        Returns:
            dict: New groove amount
            
        Live API:
            Song.groove_amount (float)
        """
        try:
            # API docs say groove_amount is 0.0 to 130.0 (percentage?) or 0-1?
            # Usually strict 0-1 or 0-100. Let's assume input needs to be passed directly
            # but usually it's 0-100 in Live's UI, might be 0-1 in API.
            # Reference check: Song.md says type is float.
            self.song.groove_amount = float(amount)
            return {"groove_amount": self.song.groove_amount}
        except Exception as e:
            self._log("Error setting groove amount: " + str(e))
            raise

    def get_groove_amount(self):
        """Get the global groove amount."""
        try:
            return {"groove_amount": self.song.groove_amount}
        except Exception as e:
            self._log("Error getting groove amount: " + str(e))
            raise

    # =========================================================================
    # Track & Scene Management (Creation included above, Duplication/Deletion here)
    # =========================================================================

    def duplicate_scene(self, index):
        """
        Duplicate a scene.
        
        Args:
            index (int): Scene index to duplicate
            
        Returns:
            dict: Result
            
        Live API:
            Song.duplicate_scene(index)
        """
        try:
            self.song.duplicate_scene(index)
            return {"duplicated_scene_index": index, "scene_count": len(self.song.scenes)}
        except Exception as e:
            self._log("Error duplicating scene: " + str(e))
            raise
            
    def capture_and_insert_scene(self, capture_mode=0):
        """
        Capture playing clips and insert as new scene.
        
        Args:
            capture_mode (int): 0=all, 1=monitored_tracks (CaptureMode enum)
            
        Returns:
            dict: Result
            
        Live API:
            Song.capture_and_insert_scene(capture_mode)
        """
        try:
            self.song.capture_and_insert_scene(capture_mode)
            return {"captured": True, "scene_count": len(self.song.scenes)}
        except Exception as e:
            self._log("Error capturing scene: " + str(e))
            raise

    def duplicate_track(self, index):
        """
        Duplicate a track.
        
        Args:
            index (int): Track index
            
        Returns:
            dict: Result
            
        Live API:
            Song.duplicate_track(index)
        """
        try:
            self.song.duplicate_track(index)
            return {"duplicated_track_index": index, "track_count": len(self.song.tracks)}
        except Exception as e:
            self._log("Error duplicating track: " + str(e))
            raise

    def delete_track(self, index):
        """
        Delete a track.
        
        Args:
            index (int): Track index
            
        Returns:
            dict: Result
            
        Live API:
            Song.delete_track(index)
        """
        try:
            self.song.delete_track(index)
            return {"deleted_track_index": index}
        except Exception as e:
            self._log("Error deleting track: " + str(e))
            raise

    # =========================================================================
    # Additional Navigation
    # =========================================================================

    def get_cue_points(self):
        """
        Get all cue points.
        
        Returns:
            dict: List of cue points with names and times
            
        Live API:
            Song.cue_points (list of CuePoint)
        """
        try:
            cues = []
            for cue in self.song.cue_points:
                cues.append({
                    "name": cue.name,
                    "time": cue.time,
                    "measure": getattr(cue, 'bars_beats_sixteenths', ''), # Assuming helper exists or similar
                    "jump_count": getattr(cue, 'jump_count', 0)
                })
            return {"cue_points": cues}
        except Exception as e:
            self._log("Error getting cue points: " + str(e))
            raise

    # =========================================================================
    # Song Info
    # =========================================================================
    
    def get_data(self, key):
        """
        Get persistent data from the Song object.
        
        Args:
            key (str): Data key
            
        Returns:
            dict: The value
        """
        try:
            val = self.song.get_data(key, None)
            return {"key": key, "value": val}
        except Exception as e:
            # Often raises error if key doesn't exist? Or returns None?
            # API says "get_data(key, default_value)".
            # We catch just in case.
            self._log("Error getting data: " + str(e))
            return {"key": key, "value": None} # Return None safely

    def set_data(self, key, value):
        """
        Set persistent data in the Song object.
        
        Args:
            key (str): Data key
            value (str): Data value (API typically expects strings)
        """
        try:
            self.song.set_data(key, value)
            return {"status": "success", "key": key, "value": value}
        except Exception as e:
            self._log("Error setting data: " + str(e))
            raise

    def move_device(self, track_index, device_index, target_track_index, target_index):
        """
        Move a device to a new location (Track-to-Track only for now).
        
        Note: The API 'move_device' allows moving between Chains too, but we need
        robust 'Target' resolution. For Phase 7, we implement Track->Track moving
        as the primary use case (reordering mixer strip).
        
        Args:
            track_index, device_index: Source
            target_track_index: Destination Track
            target_index: Insertion index (0 = start, -1 = end)
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Source track index out of range")
            source_track = self.song.tracks[track_index]
            
            if device_index < 0 or device_index >= len(source_track.devices):
                raise IndexError("Source device index out of range")
            device = source_track.devices[device_index]
            
            if target_track_index < 0 or target_track_index >= len(self.song.tracks):
                raise IndexError("Target track index out of range")
            target_track = self.song.tracks[target_track_index]
            
            # Target is the track (LomObject), position is index
            self.song.move_device(device, target_track, target_index)
            
            return {
                "status": "success",
                "source": {"track": track_index, "device": device_index},
                "destination": {"track": target_track_index, "index": target_index}
            }
        except Exception as e:
            self._log("Error moving device: " + str(e))
            raise

    def get_song_state(self):
        """
        Get comprehensive song state for LLM context.
        
        Returns a complete snapshot of transport, recording, and
        playback state for AI awareness.
        
        Returns:
            dict: Complete song state including:
                - tempo, time_signature
                - is_playing, current_song_time
                - record_mode, session_record, overdub
                - metronome state
                - loop state
                - undo/redo availability
        """
        try:
            return {
                # Transport
                "tempo": self.song.tempo,
                "signature_numerator": self.song.signature_numerator,
                "signature_denominator": self.song.signature_denominator,
                "is_playing": self.song.is_playing,
                "current_song_time": self.song.current_song_time,
                "song_length": self.song.song_length,
                
                # Recording
                "record_mode": self.song.record_mode,
                "session_record": self.song.session_record,
                "overdub": self.song.overdub,
                "punch_in": self.song.punch_in,
                "punch_out": self.song.punch_out,
                "can_capture_midi": self.song.can_capture_midi,
                
                # Metronome
                "metronome": self.song.metronome,
                
                # Loop
                "loop": self.song.loop,
                "loop_start": self.song.loop_start,
                "loop_length": self.song.loop_length,
                
                # Undo
                "can_undo": self.song.can_undo,
                "can_redo": self.song.can_redo,
                
                # Quantization
                "clip_trigger_quantization": self.song.clip_trigger_quantization,
                "swing_amount": self.song.swing_amount,
                
                # Counts
                "track_count": len(self.song.tracks),
                "scene_count": len(self.song.scenes),
                "return_track_count": len(self.song.return_tracks)
            }
        except Exception as e:
            self._log("Error getting song state: " + str(e))
            raise
