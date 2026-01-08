"""
Drum Rack Handler Module for AbletonMCP Remote Script.

This module provides all Drum Rack-related functionality:
    - Get information about drum pads and their samples
    - Copy pads between slots
    - Set choke groups
    - Mute/solo individual pads

For Future Agents:
    - Drum Rack is identified by having a 'drum_pads' attribute
    - Pads are indexed by MIDI note (36 = C1 = kick, 38 = snare, etc.)
    - Choke groups are set on the chain, not the pad directly
    - Standard GM drum mapping: 36=kick, 38=snare, 42=closed hat, 46=open hat
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class DrumRackHandler(HandlerBase):
    """
    Handler for Drum Rack device operations.
    
    Provides commands for inspecting and manipulating Drum Rack pads,
    including sample info, choke groups, and mute/solo states.
    """
    
    def _find_drum_rack(self, track_index, device_index=None):
        """
        Find a Drum Rack device on the specified track.
        
        Args:
            track_index (int): Track to search
            device_index (int, optional): Specific device index, or None to find first
            
        Returns:
            tuple: (device, device_index)
            
        Raises:
            IndexError: If track or device index out of range
            ValueError: If no Drum Rack found
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
            track_index (int): Track containing the Drum Rack
            device_index (int, optional): Specific device index
            include_empty (bool): Include pads without samples
            
        Returns:
            dict: {
                "status": "success",
                "device_name": str,
                "device_index": int,
                "pad_count": int,
                "pads": [{"note": int, "name": str, "mute": bool, ...}, ...]
            }
        """
        try:
            drum_rack, rack_idx = self._find_drum_rack(track_index, device_index)
            
            pads_info = []
            for pad in drum_rack.drum_pads:
                note = pad.note
                name = getattr(pad, "name", "Pad {0}".format(note))
                
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
                
                if has_content and len(chains) > 0:
                    chain = chains[0]
                    pad_data["choke_group"] = getattr(chain, "choke_group", None)
                
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
            track_index (int): Track containing the Drum Rack
            source_note (int): MIDI note of source pad (e.g. 36 for kick)
            dest_note (int): MIDI note of destination pad
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success"|"partial"|"error", ...}
        """
        try:
            drum_rack, rack_idx = self._find_drum_rack(track_index, device_index)
            
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
            
            if hasattr(drum_rack, "copy_pad"):
                drum_rack.copy_pad(source_note)
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
            track_index (int): Track containing the Drum Rack
            note (int): MIDI note of the pad
            choke_group (int): Choke group number (0 = none, 1-16 = group)
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success", "note": int, "choke_group": int}
        """
        try:
            drum_rack, rack_idx = self._find_drum_rack(track_index, device_index)
            
            target_pad = None
            for pad in drum_rack.drum_pads:
                if pad.note == note:
                    target_pad = pad
                    break
            
            if target_pad is None:
                raise ValueError("Pad (note {0}) not found".format(note))
            
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
        """
        Mute or unmute a drum pad.
        
        Args:
            track_index (int): Track containing the Drum Rack
            note (int): MIDI note of the pad
            mute (bool): True to mute, False to unmute
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success", "note": int, "mute": bool}
        """
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
        """
        Solo or unsolo a drum pad.
        
        Args:
            track_index (int): Track containing the Drum Rack
            note (int): MIDI note of the pad
            solo (bool): True to solo, False to unsolo
            device_index (int, optional): Specific device index
            
        Returns:
            dict: {"status": "success", "note": int, "solo": bool}
        """
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
