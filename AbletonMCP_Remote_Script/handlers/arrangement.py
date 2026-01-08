"""
Arrangement View Handler Module for AbletonMCP Remote Script.

This module provides Arrangement view operations:
    - Get arrangement info (position, loop, cue points)
    - Create, delete, and navigate cue points
    - Set loop region and playhead position
    - Scrub through the arrangement

For Future Agents:
    - Arrangement is accessed via Song object
    - Cue points are locators/markers in the timeline
    - song_time is in beats (quarter notes)
    - Loop is controlled via loop_start, loop_length, and loop (enable)
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class ArrangementHandler(HandlerBase):
    """
    Handler for Arrangement View operations.
    
    Provides commands for navigating and controlling the arrangement,
    including cue points (locators) and loop settings.
    """
    
    def get_arrangement_info(self):
        """
        Get information about the arrangement view.
        
        Returns:
            dict: {
                "status": "success",
                "is_playing": bool,
                "current_song_time": float (beats),
                "song_length": float (beats),
                "loop_start": float (beats),
                "loop_length": float (beats),
                "loop": bool,
                "cue_points": [{"index": int, "name": str, "time": float}, ...]
            }
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
            time (float): Position in beats
            name (str, optional): Name for the cue point
            
        Returns:
            dict: {"status": "success", "time": float, "name": str}
        """
        try:
            song = self.song
            
            if hasattr(song, "create_cue_point"):
                song.create_cue_point(float(time))
                
                if name and hasattr(song, "cue_points"):
                    cues = list(song.cue_points)
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
        
        Args:
            index (int): Index of cue point to delete
            
        Returns:
            dict: {"status": "success", "deleted_index": int}
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
        
        Args:
            index (int): Index of cue point to jump to
            
        Returns:
            dict: {"status": "success", "jumped_to": float, "cue_name": str}
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
            start (float): Loop start position in beats
            length (float): Loop length in beats
            enable (bool): Enable/disable looping
            
        Returns:
            dict: {"status": "success", "loop_start": float, ...}
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
            time (float): Position in beats
            
        Returns:
            dict: {"status": "success", "current_song_time": float}
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
        Scrub to a position in the arrangement (with audio preview).
        
        Args:
            time (float): Position in beats
            
        Returns:
            dict: {"status": "success", "scrubbed_to": float}
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
