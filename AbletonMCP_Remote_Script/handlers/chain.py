"""
Chain Handler Module for AbletonMCP Remote Script.

This module provides control over Rack Device chains:
    - Chain properties (name, color, mute, solo)
    - ChainMixerDevice (volume, pan, sends)
    - DrumChain-specific properties (choke_group, out_note)
    - Delete devices from chains

API Reference:
    - Live.Chain.Chain
    - Live.ChainMixerDevice.ChainMixerDevice
    - Live.DrumChain.DrumChain
    
See: api_modules/Chain.md, ChainMixerDevice.md, DrumChain.md
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class ChainHandler(HandlerBase):
    """
    Handler for Chain operations in AbletonMCP.
    
    Provides access to chains within Rack Devices (Instrument Rack,
    Audio Effect Rack, MIDI Effect Rack, Drum Rack).
    """
    
    def _get_rack_device(self, track_index, device_index=0):
        """Get a rack device from a track."""
        if track_index < 0 or track_index >= len(self.song.tracks):
            raise IndexError("Track index out of range")
        track = self.song.tracks[track_index]
        
        if device_index < 0 or device_index >= len(track.devices):
            raise IndexError("Device index out of range")
        device = track.devices[device_index]
        
        if not getattr(device, 'can_have_chains', False):
            raise ValueError("Device is not a rack (cannot have chains)")
        
        return device
    
    def _get_chain(self, track_index, device_index, chain_index):
        """Get a specific chain from a rack device."""
        device = self._get_rack_device(track_index, device_index)
        chains = getattr(device, 'chains', [])
        
        if chain_index < 0 or chain_index >= len(chains):
            raise IndexError("Chain index out of range")
        
        return chains[chain_index]
    
    # =========================================================================
    # Chain Properties
    # =========================================================================
    
    def get_chains(self, track_index, device_index=0):
        """
        Get all chains in a rack device.
        
        Args:
            track_index (int): Track containing the rack
            device_index (int): Device index on track (default 0)
            
        Returns:
            dict: List of chains with properties
            
        Live API:
            Device.chains (list of Chain objects)
        """
        try:
            device = self._get_rack_device(track_index, device_index)
            chains = getattr(device, 'chains', [])
            
            result = []
            for i, chain in enumerate(chains):
                chain_data = {
                    "index": i,
                    "name": getattr(chain, 'name', "Chain {}".format(i)),
                    "mute": getattr(chain, 'mute', False),
                    "solo": getattr(chain, 'solo', False),
                    "color": getattr(chain, 'color', 0),
                    "color_index": getattr(chain, 'color_index', 0),
                    "is_auto_colored": getattr(chain, 'is_auto_colored', False),
                    "has_audio_input": getattr(chain, 'has_audio_input', False),
                    "has_audio_output": getattr(chain, 'has_audio_output', False),
                    "has_midi_input": getattr(chain, 'has_midi_input', False),
                    "has_midi_output": getattr(chain, 'has_midi_output', False),
                    "muted_via_solo": getattr(chain, 'muted_via_solo', False),
                    "device_count": len(getattr(chain, 'devices', [])),
                }
                
                # DrumChain-specific properties
                if hasattr(chain, 'choke_group'):
                    chain_data["choke_group"] = chain.choke_group
                if hasattr(chain, 'out_note'):
                    chain_data["out_note"] = chain.out_note
                
                result.append(chain_data)
            
            return {
                "status": "success",
                "track_index": track_index,
                "device_index": device_index,
                "chain_count": len(result),
                "chains": result
            }
            
        except Exception as e:
            self._log("Error getting chains: " + str(e))
            raise
    
    def get_chain(self, track_index, device_index, chain_index):
        """
        Get detailed info about a specific chain.
        
        Args:
            track_index (int): Track containing the rack
            device_index (int): Device index on track
            chain_index (int): Chain index within rack
            
        Returns:
            dict: Chain properties and devices
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            
            devices = []
            for i, dev in enumerate(getattr(chain, 'devices', [])):
                devices.append({
                    "index": i,
                    "name": getattr(dev, 'name', "Device"),
                    "class_name": getattr(dev, 'class_name', "Unknown"),
                    "is_active": getattr(dev, 'is_active', True)
                })
            
            result = {
                "status": "success",
                "index": chain_index,
                "name": getattr(chain, 'name', ""),
                "mute": getattr(chain, 'mute', False),
                "solo": getattr(chain, 'solo', False),
                "color": getattr(chain, 'color', 0),
                "color_index": getattr(chain, 'color_index', 0),
                "is_auto_colored": getattr(chain, 'is_auto_colored', False),
                "devices": devices
            }
            
            # DrumChain-specific
            if hasattr(chain, 'choke_group'):
                result["choke_group"] = chain.choke_group
            if hasattr(chain, 'out_note'):
                result["out_note"] = chain.out_note
            
            return result
            
        except Exception as e:
            self._log("Error getting chain: " + str(e))
            raise
    
    def set_chain_name(self, track_index, device_index, chain_index, name):
        """
        Set the name of a chain.
        
        Args:
            track_index, device_index, chain_index: Location
            name (str): New name for the chain
            
        Returns:
            dict: Updated chain name
            
        Live API:
            Chain.name (R/W str)
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            chain.name = name
            return {
                "status": "success",
                "chain_index": chain_index,
                "name": chain.name
            }
        except Exception as e:
            self._log("Error setting chain name: " + str(e))
            raise
    
    def set_chain_mute(self, track_index, device_index, chain_index, mute):
        """
        Mute/unmute a chain.
        
        Args:
            track_index, device_index, chain_index: Location
            mute (bool): Mute state
            
        Returns:
            dict: Updated mute state
            
        Live API:
            Chain.mute (R/W bool)
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            chain.mute = mute
            return {
                "status": "success",
                "chain_index": chain_index,
                "mute": chain.mute
            }
        except Exception as e:
            self._log("Error setting chain mute: " + str(e))
            raise
    
    def set_chain_solo(self, track_index, device_index, chain_index, solo):
        """
        Solo/unsolo a chain.
        
        Note: This will not disable solo on other chains automatically.
        
        Args:
            track_index, device_index, chain_index: Location
            solo (bool): Solo state
            
        Returns:
            dict: Updated solo state
            
        Live API:
            Chain.solo (R/W bool)
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            chain.solo = solo
            return {
                "status": "success",
                "chain_index": chain_index,
                "solo": chain.solo
            }
        except Exception as e:
            self._log("Error setting chain solo: " + str(e))
            raise
    
    def set_chain_color(self, track_index, device_index, chain_index, color_index):
        """
        Set the color of a chain.
        
        Args:
            track_index, device_index, chain_index: Location
            color_index (int): Color index (0-69)
            
        Returns:
            dict: Updated color
            
        Live API:
            Chain.color_index (R/W int)
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            chain.color_index = color_index
            return {
                "status": "success",
                "chain_index": chain_index,
                "color_index": chain.color_index
            }
        except Exception as e:
            self._log("Error setting chain color: " + str(e))
            raise
    
    def delete_chain_device(self, track_index, device_index, chain_index, chain_device_index):
        """
        Delete a device from a chain.
        
        Args:
            track_index, device_index, chain_index: Chain location
            chain_device_index (int): Index of device within chain to delete
            
        Returns:
            dict: Deletion result
            
        Live API:
            Chain.delete_device(int)
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            
            if not hasattr(chain, 'delete_device'):
                return {"status": "error", "message": "delete_device not available"}
            
            devices_before = len(getattr(chain, 'devices', []))
            chain.delete_device(chain_device_index)
            devices_after = len(getattr(chain, 'devices', []))
            
            return {
                "status": "success",
                "deleted_index": chain_device_index,
                "devices_before": devices_before,
                "devices_after": devices_after
            }
        except Exception as e:
            self._log("Error deleting chain device: " + str(e))
            raise
    
    # =========================================================================
    # ChainMixerDevice
    # =========================================================================
    
    def get_chain_mixer(self, track_index, device_index, chain_index):
        """
        Get the mixer device for a chain (volume, pan, sends).
        
        Args:
            track_index, device_index, chain_index: Chain location
            
        Returns:
            dict: Mixer device parameters
            
        Live API:
            Chain.mixer_device (ChainMixerDevice)
            ChainMixerDevice.volume, panning, sends, chain_activator
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            mixer = getattr(chain, 'mixer_device', None)
            
            if mixer is None:
                return {"status": "error", "message": "No mixer device on chain"}
            
            result = {
                "status": "success",
                "chain_index": chain_index,
            }
            
            # Volume
            vol = getattr(mixer, 'volume', None)
            if vol:
                result["volume"] = {
                    "value": vol.value,
                    "min": vol.min,
                    "max": vol.max,
                    "name": getattr(vol, 'name', 'Volume')
                }
            
            # Pan
            pan = getattr(mixer, 'panning', None)
            if pan:
                result["panning"] = {
                    "value": pan.value,
                    "min": pan.min,
                    "max": pan.max,
                    "name": getattr(pan, 'name', 'Pan')
                }
            
            # Sends
            sends = getattr(mixer, 'sends', [])
            result["sends"] = []
            for i, send in enumerate(sends):
                result["sends"].append({
                    "index": i,
                    "value": send.value,
                    "min": send.min,
                    "max": send.max,
                    "name": getattr(send, 'name', 'Send {}'.format(i))
                })
            
            # Chain activator
            activator = getattr(mixer, 'chain_activator', None)
            if activator:
                result["chain_activator"] = {
                    "value": activator.value,
                    "name": getattr(activator, 'name', 'Chain On')
                }
            
            return result
            
        except Exception as e:
            self._log("Error getting chain mixer: " + str(e))
            raise
    
    def set_chain_volume(self, track_index, device_index, chain_index, value):
        """
        Set the volume of a chain.
        
        Args:
            track_index, device_index, chain_index: Chain location
            value (float): Volume value (0.0 to 1.0)
            
        Returns:
            dict: Updated volume
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            mixer = getattr(chain, 'mixer_device', None)
            if mixer is None:
                return {"status": "error", "message": "No mixer device"}
            
            vol = getattr(mixer, 'volume', None)
            if vol:
                vol.value = value
                return {
                    "status": "success",
                    "chain_index": chain_index,
                    "volume": vol.value
                }
            return {"status": "error", "message": "Volume parameter not found"}
            
        except Exception as e:
            self._log("Error setting chain volume: " + str(e))
            raise
    
    def set_chain_pan(self, track_index, device_index, chain_index, value):
        """
        Set the panning of a chain.
        
        Args:
            track_index, device_index, chain_index: Chain location
            value (float): Pan value (-1.0 to 1.0)
            
        Returns:
            dict: Updated pan
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            mixer = getattr(chain, 'mixer_device', None)
            if mixer is None:
                return {"status": "error", "message": "No mixer device"}
            
            pan = getattr(mixer, 'panning', None)
            if pan:
                pan.value = value
                return {
                    "status": "success",
                    "chain_index": chain_index,
                    "panning": pan.value
                }
            return {"status": "error", "message": "Panning parameter not found"}
            
        except Exception as e:
            self._log("Error setting chain pan: " + str(e))
            raise
    
    def set_chain_send(self, track_index, device_index, chain_index, send_index, value):
        """
        Set a send amount for a chain.
        
        Args:
            track_index, device_index, chain_index: Chain location
            send_index (int): Send index (0 = Send A, etc.)
            value (float): Send amount (0.0 to 1.0)
            
        Returns:
            dict: Updated send
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            mixer = getattr(chain, 'mixer_device', None)
            if mixer is None:
                return {"status": "error", "message": "No mixer device"}
            
            sends = getattr(mixer, 'sends', [])
            if send_index < 0 or send_index >= len(sends):
                return {"status": "error", "message": "Send index out of range"}
            
            sends[send_index].value = value
            return {
                "status": "success",
                "chain_index": chain_index,
                "send_index": send_index,
                "value": sends[send_index].value
            }
            
        except Exception as e:
            self._log("Error setting chain send: " + str(e))
            raise
    
    # =========================================================================
    # DrumChain Specific
    # =========================================================================
    
    def set_drum_chain_choke_group(self, track_index, device_index, chain_index, choke_group):
        """
        Set the choke group for a drum chain.
        
        Args:
            track_index, device_index, chain_index: Chain location
            choke_group (int): Choke group number (0 = none)
            
        Returns:
            dict: Updated choke group
            
        Live API:
            DrumChain.choke_group (R/W int)
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            
            if not hasattr(chain, 'choke_group'):
                return {"status": "error", "message": "Not a drum chain (no choke_group)"}
            
            chain.choke_group = choke_group
            return {
                "status": "success",
                "chain_index": chain_index,
                "choke_group": chain.choke_group
            }
            
        except Exception as e:
            self._log("Error setting choke group: " + str(e))
            raise
    
    def set_drum_chain_out_note(self, track_index, device_index, chain_index, out_note):
        """
        Set the output MIDI note for a drum chain.
        
        Args:
            track_index, device_index, chain_index: Chain location
            out_note (int): MIDI note number (0-127)
            
        Returns:
            dict: Updated out note
            
        Live API:
            DrumChain.out_note (R/W int)
        """
        try:
            chain = self._get_chain(track_index, device_index, chain_index)
            
            if not hasattr(chain, 'out_note'):
                return {"status": "error", "message": "Not a drum chain (no out_note)"}
            
            chain.out_note = out_note
            return {
                "status": "success",
                "chain_index": chain_index,
                "out_note": chain.out_note
            }
            
        except Exception as e:
            self._log("Error setting out note: " + str(e))
            raise
