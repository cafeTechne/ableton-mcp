"""
Base Handler Module for AbletonMCP Remote Script.

This module provides the foundational class that all handler modules inherit from.
It centralizes common functionality like logging, song access, and error handling.

For Future Agents:
    - All handlers inherit from HandlerBase
    - Use self._log() for consistent logging
    - Access Live's Song object via self.song
    - Follow the established error handling pattern in try/except blocks
"""
from __future__ import absolute_import, print_function, unicode_literals


class HandlerBase(object):
    """
    Base class for all AbletonMCP handler modules.
    
    Provides common utilities used across all handlers:
        - Logging via _log()
        - Song object access via .song property
        - Consistent initialization pattern
    
    Usage:
        class MyHandler(HandlerBase):
            def my_command(self, param):
                try:
                    track = self.song.tracks[0]
                    self._log("Accessed track: " + track.name)
                    return {"status": "success"}
                except Exception as e:
                    self._log("Error: " + str(e))
                    raise
    """
    
    def __init__(self, mcp):
        """
        Initialize handler with reference to main MCP controller.
        
        Args:
            mcp: The main AbletonMCP instance that provides:
                - log_message(): Logging function
                - _song: Reference to Live's Song object
        """
        self.mcp = mcp
    
    def _log(self, message):
        """
        Log a message to Ableton's log file.
        
        Args:
            message (str): Message to log
        """
        self.mcp.log_message(message)
    
    @property
    def song(self):
        """
        Access the Live Song object.
        
        Returns:
            Live.Song.Song: The current Live Set
        """
        return self.mcp._song

    def _find_param_by_keywords(self, device, keywords):
        """
        Search for a parameter on a device that matches all provided keywords in its name.
        
        Args:
            device: Live.Device.Device instance
            keywords: List of strings to match against the parameter name
            
        Returns:
            Live.DeviceParameter.DeviceParameter or None
        """
        if not device or not hasattr(device, 'parameters'):
            return None
        
        keywords = [k.lower() for k in keywords]
        for param in device.parameters:
            name_lower = getattr(param, 'name', '').lower()
            if all(k in name_lower for k in keywords):
                return param
        return None
