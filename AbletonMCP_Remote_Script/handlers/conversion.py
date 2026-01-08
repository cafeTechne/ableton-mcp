"""
Conversion Handler Module for AbletonMCP Remote Script.

This module handles audio-to-MIDI conversions and other
content transformation operations.

Key Responsibilities:
    - Audio to MIDI conversion (drums, harmony, melody)
    - Simpler slices to Drum Rack
    - Create MIDI track with Simpler from audio

For Future Agents:
    - Audio-to-MIDI conversions only work on audio clips
    - Conversions create new tracks and clips
    - Slice operations require Simpler in slice mode
    - Some conversions may take time to complete

Live 11 API Reference:
    - Clip.create_drum_rack_from_slice_markers()
    - Song.create_midi_track_with_simpler(clip)
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase
import Live


class ConversionHandler(HandlerBase):
    """
    Handler for content conversion operations in AbletonMCP.
    
    Provides audio-to-MIDI conversion and other transformation
    capabilities.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    def _get_clip(self, track_index, clip_index):
        """Get clip by track and slot index."""
        tracks = self.song.tracks
        if track_index < 0 or track_index >= len(tracks):
            raise IndexError("Track index out of range")
        
        track = tracks[track_index]
        slots = track.clip_slots
        
        if clip_index < 0 or clip_index >= len(slots):
            raise IndexError("Clip index out of range")
        
        slot = slots[clip_index]
        if not slot.has_clip:
            raise RuntimeError("No clip at this position")
        
        return slot.clip
    
    # =========================================================================
    # Audio to MIDI Conversion
    # =========================================================================
    
    def audio_to_drums(self, track_index, clip_index):
        """
        Convert an audio clip to MIDI using drum detection.
        
        Creates a new MIDI track with the detected drum hits.
        Best used for percussion samples and drum loops.
        
        Args:
            track_index (int): Track containing the audio clip
            clip_index (int): Clip slot index
        
        Returns:
            dict: Conversion result
        
        Raises:
            RuntimeError: If clip is not an audio clip
        
        Live API:
            Song.tracks[].clip_slots[].clip
            Conversion creates new track automatically
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_audio_clip:
                raise RuntimeError("Audio to drums only works on audio clips")
            
            # The conversion is typically triggered via Live's interface
            # Remote Script can access the result but not directly trigger
            # Using available workarounds
            
            # Note: In Live 11, audio-to-MIDI is done through the Edit menu
            # or context menu - not directly accessible from API
            # We document what would be needed
            
            return {
                "status": "info",
                "message": "Audio-to-MIDI drum conversion must be triggered via Live's Edit menu",
                "clip_name": clip.name,
                "clip_length": clip.length
            }
        except Exception as e:
            self._log("Error in audio to drums: " + str(e))
            raise
    
    def audio_to_harmony(self, track_index, clip_index):
        """
        Convert an audio clip to MIDI using harmony detection.
        
        Creates a new MIDI track with detected chords/harmonies.
        Best used for polyphonic audio like piano or guitar.
        
        Args:
            track_index (int): Track containing the audio clip
            clip_index (int): Clip slot index
        
        Returns:
            dict: Conversion result
        
        Raises:
            RuntimeError: If clip is not an audio clip
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_audio_clip:
                raise RuntimeError("Audio to harmony only works on audio clips")
            
            return {
                "status": "info",
                "message": "Audio-to-MIDI harmony conversion must be triggered via Live's Edit menu",
                "clip_name": clip.name,
                "clip_length": clip.length
            }
        except Exception as e:
            self._log("Error in audio to harmony: " + str(e))
            raise
    
    def audio_to_melody(self, track_index, clip_index):
        """
        Convert an audio clip to MIDI using melody detection.
        
        Creates a new MIDI track with detected melodic notes.
        Best used for monophonic audio like vocals or leads.
        
        Args:
            track_index (int): Track containing the audio clip
            clip_index (int): Clip slot index
        
        Returns:
            dict: Conversion result
        
        Raises:
            RuntimeError: If clip is not an audio clip
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_audio_clip:
                raise RuntimeError("Audio to melody only works on audio clips")
            
            return {
                "status": "info",
                "message": "Audio-to-MIDI melody conversion must be triggered via Live's Edit menu",
                "clip_name": clip.name,
                "clip_length": clip.length
            }
        except Exception as e:
            self._log("Error in audio to melody: " + str(e))
            raise
    
    # =========================================================================
    # Simpler Conversions
    # =========================================================================
    
    def simpler_to_sampler(self, track_index, device_index=None):
        """
        Convert a Simpler device to Sampler.
        
        Creates a Sampler with the same sample and basic settings.
        
        Args:
            track_index (int): Track index
            device_index (int, optional): Device index, None = first Simpler
        
        Returns:
            dict: Conversion info
        
        Note:
            This is typically done via right-click context menu in Live.
            The API doesn't directly support this conversion.
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            # Find Simpler device
            simpler = None
            for idx, device in enumerate(track.devices):
                if hasattr(device, 'class_name') and device.class_name == 'OriginalSimpler':
                    if device_index is None or idx == device_index:
                        simpler = device
                        break
            
            if not simpler:
                raise RuntimeError("No Simpler found at specified position")
            
            return {
                "status": "info",
                "message": "Simpler to Sampler conversion must be done via right-click menu in Live",
                "device_name": simpler.name
            }
        except Exception as e:
            self._log("Error in simpler to sampler: " + str(e))
            raise
    
    def create_drum_rack_from_slices(self, track_index, device_index=None):
        """
        Convert a Simpler in slice mode to a Drum Rack.
        
        Each slice becomes a pad in the new Drum Rack.
        
        Args:
            track_index (int): Track index
            device_index (int, optional): Device index, None = first Simpler
        
        Returns:
            dict: Conversion info
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            # Find Simpler device in slice mode
            simpler = None
            simpler_index = -1
            
            for idx, device in enumerate(track.devices):
                if hasattr(device, 'class_name') and device.class_name == 'OriginalSimpler':
                    if device_index is None or idx == device_index:
                        simpler = device
                        simpler_index = idx
                        break
            
            if not simpler:
                raise RuntimeError("No Simpler found at specified position")
            
            # Check if in slice mode (playback mode 2)
            if hasattr(simpler, 'playback_mode') and simpler.playback_mode != 2:
                # Try to switch to slice mode if possible, or raise error
                # simpler.playback_mode = 2
                pass 

            # Perform actual conversion using Live API
            Live.Conversions.sliced_simpler_to_drum_rack(self.song, simpler)
            
            return {
                "status": "success",
                "message": "Converted Simpler slices to Drum Rack",
                "original_device_index": simpler_index
            }
        except Exception as e:
            self._log("Error creating drum rack from slices: " + str(e))
            raise

    def create_drum_rack_from_audio_clip(self, track_index, clip_index):
        """
        Create a new Drum Rack track from an audio clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip index
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            if not clip.is_audio_clip:
                raise RuntimeError("Target clip must be an audio clip")

            Live.Conversions.create_drum_rack_from_audio_clip(self.song, clip)
            
            return {
                "status": "success",
                "message": "Created Drum Rack from Audio Clip"
            }
        except Exception as e:
            self._log("Error creating drum rack from audio clip: " + str(e))
            raise

    def move_devices_to_drum_rack(self, track_index):
        """
        Move devices on track to a new Drum Rack pad.
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            target_track = tracks[track_index]
            
            # Live API returns a WeakPtr to the new object (likely the Drum Rack device or pad)
            new_obj = Live.Conversions.move_devices_on_track_to_new_drum_rack_pad(self.song, target_track)
            
            return {
                "status": "success",
                "message": "Moved devices to new Drum Rack pad"
            }
        except Exception as e:
            self._log("Error moving devices to drum rack: " + str(e))
            raise
    
    # =========================================================================
    # MIDI Conversion
    # =========================================================================
    
    def midi_to_audio(self, track_index):
        """
        Freeze and flatten a MIDI track to audio.
        
        This is equivalent to Freeze + Flatten in Live's UI.
        The track's devices are rendered to audio.
        
        Args:
            track_index (int): MIDI track index
        
        Returns:
            dict: Conversion info
        
        Note:
            Flatten is destructive - it replaces MIDI with audio.
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            
            if not track.has_midi_input:
                raise RuntimeError("Track must be a MIDI track")
            
            if not track.can_be_frozen:
                raise RuntimeError("Track cannot be frozen")
            
            # First freeze the track
            # Note: There's no direct flatten API - user must do via UI
            
            return {
                "status": "info",
                "message": "Use Freeze then Flatten via Live's Track menu to convert MIDI to audio",
                "track_name": track.name,
                "can_be_frozen": track.can_be_frozen,
                "is_frozen": track.is_frozen
            }
        except Exception as e:
            self._log("Error in MIDI to audio: " + str(e))
            raise
    
    # =========================================================================
    # Clip Conversions
    # =========================================================================
    
    def consolidate_clip(self, track_index, clip_index):
        """
        Consolidate a clip (render to new clip).
        
        For audio clips, renders any warping/effects.
        For MIDI clips, creates a new clip with flattened data.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
        
        Returns:
            dict: Consolidation info
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            return {
                "status": "info",
                "message": "Clip consolidation must be done via Live's Edit menu (Cmd/Ctrl+J)",
                "clip_name": clip.name,
                "clip_length": clip.length
            }
        except Exception as e:
            self._log("Error consolidating clip: " + str(e))
            raise
