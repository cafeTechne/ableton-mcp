"""
Simpler/Sampler Handler Module for AbletonMCP Remote Script.

This module provides Simpler and Sampler device control:
    - Get device and sample information
    - Reverse and crop samples
    - Set playback mode (classic, one-shot, slice)
    - Adjust sample markers and warping

For Future Agents:
    - Simpler is identified by class_name containing "simpler"
    - Sampler is identified by class_name containing "sampler"
    - Most sample operations are on device.sample object
    - Playback modes: 0=classic, 1=one_shot, 2=slice
    - Warp modes: 0=beats, 1=tones, 2=texture, 3=repitch, 4=complex, 5=complex_pro
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class SimplerHandler(HandlerBase):
    """
    Handler for Simpler and Sampler device operations.
    
    Provides commands for manipulating samples in Simpler/Sampler devices,
    including playback modes, warping, and markers.
    """
    
    def _find_simpler_device(self, track_index, device_index=None):
        """
        Find a Simpler or Sampler device on the specified track.
        
        Args:
            track_index (int): Track to search
            device_index (int, optional): Specific device index
            
        Returns:
            tuple: (device, device_index, device_type)
            
        Raises:
            IndexError: If track or device index out of range
            ValueError: If no Simpler/Sampler found
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
        
        Args:
            track_index (int): Track containing the device
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {
                "status": "success",
                "device_type": "simpler"|"sampler",
                "device_name": str,
                "playback_mode": "classic"|"one_shot"|"slice",
                "sample": {
                    "file_path": str,
                    "length": float,
                    "start_marker": float,
                    "end_marker": float,
                    ...
                }
            }
        """
        try:
            device, dev_idx, dev_type = self._find_simpler_device(track_index, device_index)
            
            info = {
                "status": "success",
                "device_type": dev_type,
                "device_index": dev_idx,
                "device_name": getattr(device, "name", dev_type.title())
            }
            
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
            
            if hasattr(device, "playback_mode"):
                mode_val = device.playback_mode
                mode_names = {0: "classic", 1: "one_shot", 2: "slice"}
                info["playback_mode"] = mode_names.get(mode_val, str(mode_val))
            
            if hasattr(device, "voices"):
                info["voices"] = device.voices
                
            return info
            
        except Exception as e:
            self._log("Error getting simpler info: " + str(e))
            raise
    
    def reverse_simpler_sample(self, track_index, device_index=None):
        """
        Reverse the sample in a Simpler device.
        
        Args:
            track_index (int): Track containing the device
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success"|"error", "message": str}
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
        Crop the sample to the current start/end markers.
        
        Args:
            track_index (int): Track containing the device
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success"|"error", "message": str}
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
            track_index (int): Track containing the device
            mode (str|int): "classic", "one_shot", "slice" (or 0, 1, 2)
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success", "playback_mode": str}
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
        Set the start and/or end markers of the sample.
        
        Args:
            track_index (int): Track containing the device
            start (float, optional): Start marker position (sample frames)
            end (float, optional): End marker position (sample frames)
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success", "start_marker": float, "end_marker": float}
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
        Enable/disable warping and set warp mode.
        
        Args:
            track_index (int): Track containing the device
            warp_mode (str, optional): "beats", "tones", "texture", "repitch", "complex", "complex_pro"
            enable (bool, optional): Enable/disable warping
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success", "warping": bool, "warp_mode": str}
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
