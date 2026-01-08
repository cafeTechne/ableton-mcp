"""
Groove Pool Handler Module for AbletonMCP Remote Script.

This module provides Groove Pool integration:
    - List available grooves in the project
    - Apply grooves to clips
    - Commit (bake) grooves permanently into note data

For Future Agents:
    - Groove Pool is accessed via Song.groove_pool
    - Grooves affect timing and velocity of notes
    - commit_groove() permanently modifies the notes, removing the groove reference
    - Grooves are loaded into the pool from .agr files or by dragging from clips
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class GrooveHandler(HandlerBase):
    """
    Handler for Groove Pool operations.
    
    Provides commands for working with Live's Groove Pool to add
    swing and feel to MIDI clips.
    """
    
    def get_groove_pool(self):
        """
        Get list of available grooves from the song's groove pool.
        
        Returns:
            dict: {
                "status": "success",
                "groove_count": int,
                "grooves": [
                    {
                        "index": int,
                        "name": str,
                        "timing_amount": float (0.0-1.0),
                        "velocity_amount": float (0.0-1.0),
                        "random_amount": float (0.0-1.0),
                        ...
                    },
                    ...
                ]
            }
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
            track_index (int): Track containing the clip
            clip_index (int): Clip slot index
            groove_index (int): Index into the groove pool (-1 or None to remove)
            
        Returns:
            dict: {"status": "success", "groove_name": str, "groove_index": int}
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
                if hasattr(clip, "groove"):
                    clip.groove = None
                return {"status": "success", "message": "Groove removed"}
            
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
        Bake the groove into the clip's notes permanently.
        
        This modifies the actual note positions/velocities and removes the
        groove reference. Cannot be undone except via Undo.
        
        Args:
            track_index (int): Track containing the clip
            clip_index (int): Clip slot index
            
        Returns:
            dict: {"status": "success", "message": str}
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
            
            if not hasattr(clip, "groove") or clip.groove is None:
                return {"status": "error", "message": "No groove applied to clip"}
            
            groove_name = getattr(clip.groove, "name", "Unknown")
            
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
