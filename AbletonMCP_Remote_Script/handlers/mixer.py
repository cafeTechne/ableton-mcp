"""
Mixer Handler Module for AbletonMCP Remote Script.

This module handles mixer operations including master track, return tracks,
crossfader, and cue volume controls.

Key Responsibilities:
    - Master track volume/pan controls
    - Return track controls
    - Crossfader assignment and position
    - Cue/preview volume
    - Track send levels

For Future Agents:
    - Master track is always at song.master_track
    - Return tracks are at song.return_tracks
    - Each track has a mixer_device with volume, pan, sends
    - Crossfader assigns tracks to A, B, or off

Live 11 API Reference:
    - Live.MixerDevice.MixerDevice class
    - Live.Track.Track.mixer_device property
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class MixerHandler(HandlerBase):
    """
    Handler for mixer operations in AbletonMCP.
    
    Provides access to master track, return tracks, crossfader,
    and send controls that affect the overall mix.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    # =========================================================================
    # Master Track
    # =========================================================================
    
    def get_master_info(self):
        """
        Get master track information.
        
        Returns:
            dict: Master track info including volume, pan, and device count
        
        Live API:
            Song.master_track (Track property)
            MixerDevice properties: volume, panning
        """
        try:
            master = self.song.master_track
            mixer = master.mixer_device
            
            return {
                "name": master.name,
                "volume": mixer.volume.value,
                "volume_str": mixer.volume.str_for_value(mixer.volume.value),
                "pan": mixer.panning.value,
                "pan_str": mixer.panning.str_for_value(mixer.panning.value),
                "device_count": len(master.devices)
            }
        except Exception as e:
            self._log("Error getting master info: " + str(e))
            raise
    
    def set_master_volume(self, value):
        """
        Set the master track volume.
        
        Args:
            value (float): Volume value from 0.0 (silence) to 1.0 (0 dB)
                Values above 1.0 may boost above 0 dB if supported
        
        Returns:
            dict: New volume setting
        
        Live API:
            MixerDevice.volume (DeviceParameter)
        """
        try:
            mixer = self.song.master_track.mixer_device
            value = max(0.0, min(1.0, float(value)))
            mixer.volume.value = value
            return {
                "volume": mixer.volume.value,
                "volume_str": mixer.volume.str_for_value(mixer.volume.value)
            }
        except Exception as e:
            self._log("Error setting master volume: " + str(e))
            raise
    
    def set_master_pan(self, value):
        """
        Set the master track pan.
        
        Args:
            value (float): Pan value from -1.0 (left) to 1.0 (right)
        
        Returns:
            dict: New pan setting
        
        Live API:
            MixerDevice.panning (DeviceParameter)
        """
        try:
            mixer = self.song.master_track.mixer_device
            value = max(-1.0, min(1.0, float(value)))
            mixer.panning.value = value
            return {
                "pan": mixer.panning.value,
                "pan_str": mixer.panning.str_for_value(mixer.panning.value)
            }
        except Exception as e:
            self._log("Error setting master pan: " + str(e))
            raise
    
    # =========================================================================
    # Cue/Preview Volume
    # =========================================================================
    
    def get_cue_volume(self):
        """
        Get the cue (preview) volume.
        
        Returns:
            dict: Cue volume value
        
        Live API:
            MixerDevice.cue_volume (DeviceParameter)
        """
        try:
            mixer = self.song.master_track.mixer_device
            cue = mixer.cue_volume
            return {
                "cue_volume": cue.value,
                "cue_volume_str": cue.str_for_value(cue.value)
            }
        except Exception as e:
            self._log("Error getting cue volume: " + str(e))
            raise
    
    def set_cue_volume(self, value):
        """
        Set the cue (preview) volume.
        
        Args:
            value (float): Volume value from 0.0 to 1.0
        
        Returns:
            dict: New cue volume setting
        
        Live API:
            MixerDevice.cue_volume (DeviceParameter)
        """
        try:
            mixer = self.song.master_track.mixer_device
            value = max(0.0, min(1.0, float(value)))
            mixer.cue_volume.value = value
            return {
                "cue_volume": mixer.cue_volume.value,
                "cue_volume_str": mixer.cue_volume.str_for_value(mixer.cue_volume.value)
            }
        except Exception as e:
            self._log("Error setting cue volume: " + str(e))
            raise
    
    # =========================================================================
    # Crossfader
    # =========================================================================
    
    def get_crossfader(self):
        """
        Get the current crossfader position.
        
        Returns:
            dict: Crossfader position (-1.0 = A, 0.0 = center, 1.0 = B)
        
        Live API:
            MixerDevice.crossfader (DeviceParameter)
        """
        try:
            mixer = self.song.master_track.mixer_device
            cf = mixer.crossfader
            return {
                "crossfader": cf.value,
                "crossfader_str": cf.str_for_value(cf.value)
            }
        except Exception as e:
            self._log("Error getting crossfader: " + str(e))
            raise
    
    def set_crossfader(self, value):
        """
        Set the crossfader position.
        
        Args:
            value (float): Position from -1.0 (full A) to 1.0 (full B)
        
        Returns:
            dict: New crossfader position
        
        Live API:
            MixerDevice.crossfader (DeviceParameter)
        """
        try:
            mixer = self.song.master_track.mixer_device
            value = max(-1.0, min(1.0, float(value)))
            mixer.crossfader.value = value
            return {
                "crossfader": mixer.crossfader.value,
                "crossfader_str": mixer.crossfader.str_for_value(mixer.crossfader.value)
            }
        except Exception as e:
            self._log("Error setting crossfader: " + str(e))
            raise
    
    def set_track_crossfade_assign(self, track_index, assign):
        """
        Set a track's crossfade assignment.
        
        Args:
            track_index (int): Track index (0-based)
            assign (int): Assignment value
                0 = None (not affected by crossfader)
                1 = A
                2 = B
        
        Returns:
            dict: New assignment
        
        Live API:
            MixerDevice.crossfade_assign (int property: 0=None, 1=A, 2=B)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            mixer = track.mixer_device
            
            # Validate assign value
            assign = int(assign)
            if assign not in (0, 1, 2):
                raise ValueError("assign must be 0 (None), 1 (A), or 2 (B)")
            
            mixer.crossfade_assign = assign
            
            assign_names = {0: "None", 1: "A", 2: "B"}
            return {
                "track_index": track_index,
                "track_name": track.name,
                "crossfade_assign": assign,
                "crossfade_assign_name": assign_names[assign]
            }
        except Exception as e:
            self._log("Error setting crossfade assign: " + str(e))
            raise
    
    # =========================================================================
    # Track Sends
    # =========================================================================
    
    def get_track_sends(self, track_index):
        """
        Get all send levels for a track.
        
        Args:
            track_index (int): Track index (0-based)
        
        Returns:
            dict: List of send levels with names and values
        
        Live API:
            MixerDevice.sends (DeviceParameter vector)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            sends = track.mixer_device.sends
            return_tracks = self.song.return_tracks
            
            send_list = []
            for idx, send in enumerate(sends):
                send_info = {
                    "index": idx,
                    "value": send.value,
                    "value_str": send.str_for_value(send.value)
                }
                # Add return track name if available
                if idx < len(return_tracks):
                    send_info["return_name"] = return_tracks[idx].name
                send_list.append(send_info)
            
            return {
                "track_index": track_index,
                "track_name": track.name,
                "send_count": len(send_list),
                "sends": send_list
            }
        except Exception as e:
            self._log("Error getting track sends: " + str(e))
            raise
    
    def set_track_send(self, track_index, send_index, value):
        """
        Set a track's send level.
        
        Args:
            track_index (int): Track index (0-based)
            send_index (int): Send index (0-based, corresponds to return track order)
            value (float): Send level from 0.0 to 1.0
        
        Returns:
            dict: New send level
        
        Live API:
            MixerDevice.sends[index] (DeviceParameter)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            sends = track.mixer_device.sends
            
            if send_index < 0 or send_index >= len(sends):
                raise IndexError("Send index out of range")
            
            value = max(0.0, min(1.0, float(value)))
            sends[send_index].value = value
            
            return {
                "track_index": track_index,
                "send_index": send_index,
                "value": sends[send_index].value,
                "value_str": sends[send_index].str_for_value(sends[send_index].value)
            }
        except Exception as e:
            self._log("Error setting track send: " + str(e))
            raise
    
    # =========================================================================
    # Return Tracks
    # =========================================================================
    
    def set_return_volume(self, return_index, value):
        """
        Set a return track's volume.
        
        Args:
            return_index (int): Return track index (0-based)
            value (float): Volume from 0.0 to 1.0
        
        Returns:
            dict: New volume setting
        
        Live API:
            Track.mixer_device.volume (DeviceParameter)
        """
        try:
            returns = self.song.return_tracks
            if return_index < 0 or return_index >= len(returns):
                raise IndexError("Return track index out of range")
            
            track = returns[return_index]
            value = max(0.0, min(1.0, float(value)))
            track.mixer_device.volume.value = value
            
            mixer = track.mixer_device
            return {
                "return_index": return_index,
                "return_name": track.name,
                "volume": mixer.volume.value,
                "volume_str": mixer.volume.str_for_value(mixer.volume.value)
            }
        except Exception as e:
            self._log("Error setting return volume: " + str(e))
            raise
    
    def set_return_pan(self, return_index, value):
        """
        Set a return track's pan.
        
        Args:
            return_index (int): Return track index (0-based)
            value (float): Pan from -1.0 (left) to 1.0 (right)
        
        Returns:
            dict: New pan setting
        
        Live API:
            Track.mixer_device.panning (DeviceParameter)
        """
        try:
            returns = self.song.return_tracks
            if return_index < 0 or return_index >= len(returns):
                raise IndexError("Return track index out of range")
            
            track = returns[return_index]
            value = max(-1.0, min(1.0, float(value)))
            track.mixer_device.panning.value = value
            
            mixer = track.mixer_device
            return {
                "return_index": return_index,
                "return_name": track.name,
                "pan": mixer.panning.value,
                "pan_str": mixer.panning.str_for_value(mixer.panning.value)
            }
        except Exception as e:
            self._log("Error setting return pan: " + str(e))
            raise
    
    def mute_return(self, return_index, muted):
        """
        Mute or unmute a return track.
        
        Args:
            return_index (int): Return track index (0-based)
            muted (bool): True to mute, False to unmute
        
        Returns:
            dict: New mute state
        
        Live API:
            Track.mute (bool property)
        """
        try:
            returns = self.song.return_tracks
            if return_index < 0 or return_index >= len(returns):
                raise IndexError("Return track index out of range")
            
            track = returns[return_index]
            track.mute = bool(muted)
            
            return {
                "return_index": return_index,
                "return_name": track.name,
                "mute": track.mute
            }
        except Exception as e:
            self._log("Error muting return: " + str(e))
            raise
    
    def solo_return(self, return_index, soloed):
        """
        Solo or unsolo a return track.
        
        Args:
            return_index (int): Return track index (0-based)
            soloed (bool): True to solo, False to unsolo
        
        Returns:
            dict: New solo state
        
        Live API:
            Track.solo (bool property)
        """
        try:
            returns = self.song.return_tracks
            if return_index < 0 or return_index >= len(returns):
                raise IndexError("Return track index out of range")
            
            track = returns[return_index]
            track.solo = bool(soloed)
            
            return {
                "return_index": return_index,
                "return_name": track.name,
                "solo": track.solo
            }
        except Exception as e:
            self._log("Error soloing return: " + str(e))
            raise
    
    # =========================================================================
    # Mixer Overview
    # =========================================================================
    
    def get_mixer_overview(self):
        """
        Get a complete mixer overview for LLM context.
        
        Returns comprehensive state of master, returns, and crossfader.
        
        Returns:
            dict: Complete mixer state
        """
        try:
            master = self.song.master_track
            master_mixer = master.mixer_device
            
            # Master info
            result = {
                "master": {
                    "volume": master_mixer.volume.value,
                    "pan": master_mixer.panning.value,
                    "crossfader": master_mixer.crossfader.value,
                    "cue_volume": master_mixer.cue_volume.value
                }
            }
            
            # Return tracks
            returns = []
            for idx, track in enumerate(self.song.return_tracks):
                mixer = track.mixer_device
                returns.append({
                    "index": idx,
                    "name": track.name,
                    "color": track.color,
                    "volume": mixer.volume.value,
                    "pan": mixer.panning.value,
                    "mute": track.mute,
                    "solo": track.solo
                })
            result["return_tracks"] = returns
            result["return_count"] = len(returns)
            
            return result
        except Exception as e:
            self._log("Error getting mixer overview: " + str(e))
            raise
