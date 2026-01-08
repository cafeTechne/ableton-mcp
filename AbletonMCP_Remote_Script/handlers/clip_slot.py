"""
ClipSlot Handler Module for AbletonMCP Remote Script.

This module handles clip slot operations in Session View including
firing, stopping, and managing individual clip slots.

Key Responsibilities:
    - Fire/stop clip slots
    - Create/delete clips in slots
    - Duplicate clips between slots
    - Query slot state (has_clip, is_playing, etc.)
    - Slot color management

For Future Agents:
    - Clip slots are the grid cells in Session View
    - Each track has a list of clip_slots corresponding to scene rows
    - A slot may contain a clip or be empty
    - Group tracks have "group slots" that control member tracks

Live 11 API Reference:
    - Live.ClipSlot.ClipSlot class
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class ClipSlotHandler(HandlerBase):
    """
    Handler for clip slot operations in AbletonMCP.
    
    Provides access to Session View clip slots for launching,
    stopping, and managing clips.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    def _get_clip_slot(self, track_index, slot_index):
        """
        Get a clip slot by track and slot index.
        
        Args:
            track_index (int): Track index (0-based)
            slot_index (int): Slot/scene index (0-based)
        
        Returns:
            ClipSlot: The clip slot object
        
        Raises:
            IndexError: If track or slot index is out of range
        """
        tracks = self.song.tracks
        if track_index < 0 or track_index >= len(tracks):
            raise IndexError("Track index {} out of range (0-{})".format(
                track_index, len(tracks) - 1))
        
        track = tracks[track_index]
        slots = track.clip_slots
        
        if slot_index < 0 or slot_index >= len(slots):
            raise IndexError("Slot index {} out of range (0-{})".format(
                slot_index, len(slots) - 1))
        
        return slots[slot_index]
    
    # =========================================================================
    # Slot Information
    # =========================================================================
    
    def get_slot_info(self, track_index, slot_index):
        """
        Get information about a specific clip slot.
        
        Args:
            track_index (int): Track index (0-based)
            slot_index (int): Slot/scene index (0-based)
        
        Returns:
            dict: Slot information including:
                - has_clip (bool): Whether the slot contains a clip
                - has_stop_button (bool): Whether the slot has a stop button
                - is_playing (bool): Whether the clip is playing
                - is_recording (bool): Whether the clip is recording
                - is_triggered (bool): Whether playback is pending
                - is_group_slot (bool): Whether this is a group track slot
                - color (int): Slot color (if has_clip)
                - clip_name (str): Clip name (if has_clip)
        
        Live API:
            ClipSlot properties: has_clip, has_stop_button, is_playing,
            is_recording, is_triggered, is_group_slot, color
        """
        try:
            slot = self._get_clip_slot(track_index, slot_index)
            
            info = {
                "track_index": track_index,
                "slot_index": slot_index,
                "has_clip": slot.has_clip,
                "has_stop_button": slot.has_stop_button,
                "is_playing": slot.is_playing,
                "is_recording": slot.is_recording,
                "is_triggered": slot.is_triggered,
                "is_group_slot": slot.is_group_slot
            }
            
            if slot.has_clip:
                clip = slot.clip
                info.update({
                    "color": slot.color,
                    "clip_name": clip.name,
                    "clip_length": clip.length,
                    "looping": clip.looping,
                    "is_midi_clip": clip.is_midi_clip
                })
            
            return info
        except Exception as e:
            self._log("Error getting slot info: " + str(e))
            raise
    
    # =========================================================================
    # Firing and Stopping
    # =========================================================================
    
    def fire_slot(self, track_index, slot_index, record_length=None, 
                  launch_quantization=None, force_legato=False):
        """
        Fire a clip slot (start playback or recording).
        
        If the slot has a clip, starts playing it. If the track is armed
        and the slot is empty, starts recording into the slot.
        
        Args:
            track_index (int): Track index (0-based)
            slot_index (int): Slot index (0-based)
            record_length (float, optional): For recording, stop after
                this many beats
            launch_quantization (int, optional): Override global quantization
                -1 = use global, other values are quantization indices
            force_legato (bool): If True, start immediately and sync playhead
        
        Returns:
            dict: Fire result with slot state
        
        Live API:
            ClipSlot.fire(record_length, launch_quantization, force_legato)
        """
        try:
            slot = self._get_clip_slot(track_index, slot_index)
            
            # Call fire with appropriate arguments based on what's provided
            if record_length is not None or launch_quantization is not None:
                slot.fire(
                    record_length if record_length is not None else 1.7976931348623157e+308,
                    launch_quantization if launch_quantization is not None else -2147483648,
                    force_legato
                )
            else:
                slot.fire()
            
            return {
                "fired": True,
                "track_index": track_index,
                "slot_index": slot_index,
                "has_clip": slot.has_clip
            }
        except Exception as e:
            self._log("Error firing slot: " + str(e))
            raise
    
    def stop_slot(self, track_index, slot_index):
        """
        Stop a clip slot.
        
        Stops playback of the clip in this slot, if any.
        
        Args:
            track_index (int): Track index (0-based)
            slot_index (int): Slot index (0-based)
        
        Returns:
            dict: Stop result
        
        Live API:
            ClipSlot.stop()
        """
        try:
            slot = self._get_clip_slot(track_index, slot_index)
            slot.stop()
            return {
                "stopped": True,
                "track_index": track_index,
                "slot_index": slot_index
            }
        except Exception as e:
            self._log("Error stopping slot: " + str(e))
            raise
    
    # =========================================================================
    # Clip Creation and Deletion
    # =========================================================================
    
    def create_clip(self, track_index, slot_index, length=4.0):
        """
        Create an empty MIDI clip in the slot.
        
        Only works on MIDI tracks with empty slots.
        
        Args:
            track_index (int): Track index (0-based)
            slot_index (int): Slot index (0-based)  
            length (float): Clip length in beats (default 4.0)
        
        Returns:
            dict: Creation result with clip info
        
        Raises:
            RuntimeError: If slot is not empty or track is not MIDI
        
        Live API:
            ClipSlot.create_clip(length)
        """
        try:
            slot = self._get_clip_slot(track_index, slot_index)
            
            if slot.has_clip:
                raise RuntimeError("Slot already contains a clip")
            
            slot.create_clip(float(length))
            
            return {
                "created": True,
                "track_index": track_index,
                "slot_index": slot_index,
                "length": length
            }
        except Exception as e:
            self._log("Error creating clip: " + str(e))
            raise
    
    def delete_clip(self, track_index, slot_index):
        """
        Delete the clip in a slot.
        
        Args:
            track_index (int): Track index (0-based)
            slot_index (int): Slot index (0-based)
        
        Returns:
            dict: Deletion result
        
        Raises:
            RuntimeError: If slot is empty
        
        Live API:
            ClipSlot.delete_clip()
        """
        try:
            slot = self._get_clip_slot(track_index, slot_index)
            
            if not slot.has_clip:
                raise RuntimeError("Slot does not contain a clip")
            
            slot.delete_clip()
            
            return {
                "deleted": True,
                "track_index": track_index,
                "slot_index": slot_index
            }
        except Exception as e:
            self._log("Error deleting clip: " + str(e))
            raise
    
    def duplicate_clip_to(self, src_track, src_slot, dest_track, dest_slot):
        """
        Duplicate a clip from one slot to another.
        
        Copies the clip, overwriting any existing clip in the destination.
        Source and destination must be the same type (both audio or both MIDI).
        
        Args:
            src_track (int): Source track index
            src_slot (int): Source slot index
            dest_track (int): Destination track index
            dest_slot (int): Destination slot index
        
        Returns:
            dict: Duplication result
        
        Raises:
            RuntimeError: If source is empty or track types don't match
        
        Live API:
            ClipSlot.duplicate_clip_to(target_slot)
        """
        try:
            source = self._get_clip_slot(src_track, src_slot)
            destination = self._get_clip_slot(dest_track, dest_slot)
            
            if not source.has_clip:
                raise RuntimeError("Source slot does not contain a clip")
            
            source.duplicate_clip_to(destination)
            
            return {
                "duplicated": True,
                "source": {"track": src_track, "slot": src_slot},
                "destination": {"track": dest_track, "slot": dest_slot}
            }
        except Exception as e:
            self._log("Error duplicating clip: " + str(e))
            raise
    
    # =========================================================================
    # Slot Properties
    # =========================================================================
    
    def set_stop_button(self, track_index, slot_index, has_stop_button):
        """
        Set whether a slot has a stop button.
        
        Args:
            track_index (int): Track index
            slot_index (int): Slot index
            has_stop_button (bool): Whether to show stop button
        
        Returns:
            dict: Updated slot state
        
        Live API:
            ClipSlot.has_stop_button (bool property, writable)
        """
        try:
            slot = self._get_clip_slot(track_index, slot_index)
            slot.has_stop_button = bool(has_stop_button)
            return {
                "set": True,
                "track_index": track_index,
                "slot_index": slot_index,
                "has_stop_button": slot.has_stop_button
            }
        except Exception as e:
            self._log("Error setting stop button: " + str(e))
            raise
    
    # =========================================================================
    # Batch Operations
    # =========================================================================
    
    def get_track_slots(self, track_index):
        """
        Get information about all slots on a track.
        
        Returns a summary of each slot's state for efficient batch queries.
        
        Args:
            track_index (int): Track index (0-based)
        
        Returns:
            dict: Track slots info including list of slot states
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            slots = []
            
            for idx, slot in enumerate(track.clip_slots):
                slot_info = {
                    "index": idx,
                    "has_clip": slot.has_clip,
                    "is_playing": slot.is_playing,
                    "is_triggered": slot.is_triggered
                }
                if slot.has_clip:
                    slot_info["clip_name"] = slot.clip.name
                    slot_info["clip_color"] = slot.clip.color
                slots.append(slot_info)
            
            return {
                "track_index": track_index,
                "track_name": track.name,
                "slot_count": len(slots),
                "slots": slots
            }
        except Exception as e:
            self._log("Error getting track slots: " + str(e))
            raise
    
    def fire_scene_slots(self, scene_index):
        """
        Fire all slots in a scene row.
        
        This is effectively a scene launch, but done through slots.
        Prefer using Scene.fire() for proper scene launching.
        
        Args:
            scene_index (int): Scene index (0-based)
        
        Returns:
            dict: Fire result with count of fired slots
        """
        try:
            scenes = self.song.scenes
            if scene_index < 0 or scene_index >= len(scenes):
                raise IndexError("Scene index out of range")
            
            # Fire the scene directly (more reliable)
            self.song.scenes[scene_index].fire()
            
            return {
                "fired": True,
                "scene_index": scene_index,
                "scene_name": scenes[scene_index].name
            }
        except Exception as e:
            self._log("Error firing scene slots: " + str(e))
            raise
