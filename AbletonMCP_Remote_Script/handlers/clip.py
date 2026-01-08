"""
Clip Handler Module for AbletonMCP Remote Script.

This module handles extended clip operations including clip firing,
properties, warping, and audio-specific controls.

Key Responsibilities:
    - Fire/stop individual clips
    - Clip loop settings (start, end, length)
    - Clip launch settings (mode, quantization, legato)
    - Audio clip warp settings
    - Audio clip pitch/gain
    - Clip quantization
    - Clip duplication

For Future Agents:
    - Clips exist within clip slots on tracks
    - MIDI clips have notes, audio clips have warp markers
    - Many operations differ between MIDI and audio clips
    - Use track_handler.get_clip_info() for basic info

Live 11 API Reference:
    - Live.Clip.Clip class
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class ClipHandler(HandlerBase):
    """
    Handler for extended clip operations in AbletonMCP.
    
    Provides access to clip properties, launch settings, audio
    warping, and clip manipulation beyond basic note operations.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    def _get_clip(self, track_index, clip_index):
        """
        Get a clip by track and clip/slot index.
        
        Args:
            track_index (int): Track index (0-based)
            clip_index (int): Clip slot index (0-based)
        
        Returns:
            Clip: The clip object
        
        Raises:
            IndexError: If track or slot index is out of range
            RuntimeError: If slot is empty
        """
        tracks = self.song.tracks
        if track_index < 0 or track_index >= len(tracks):
            raise IndexError("Track index {} out of range".format(track_index))
        
        track = tracks[track_index]
        slots = track.clip_slots
        
        if clip_index < 0 or clip_index >= len(slots):
            raise IndexError("Clip index {} out of range".format(clip_index))
        
        slot = slots[clip_index]
        if not slot.has_clip:
            raise RuntimeError("No clip at track {} slot {}".format(
                track_index, clip_index))
        
        return slot.clip
    
    # =========================================================================
    # Clip Firing
    # =========================================================================
    
    def fire_clip(self, track_index, clip_index, force_legato=False):
        """
        Fire (launch) a clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            force_legato (bool): If True, starts immediately in sync
        
        Returns:
            dict: Fire result
        
        Live API:
            Clip.fire()
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.fire()
            return {
                "fired": True,
                "track_index": track_index,
                "clip_index": clip_index,
                "clip_name": clip.name
            }
        except Exception as e:
            self._log("Error firing clip: " + str(e))
            raise
    
    def stop_clip(self, track_index, clip_index):
        """
        Stop a clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
        
        Returns:
            dict: Stop result
        
        Live API:
            Clip.stop()
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.stop()
            return {
                "stopped": True,
                "track_index": track_index,
                "clip_index": clip_index
            }
        except Exception as e:
            self._log("Error stopping clip: " + str(e))
            raise
    
    # =========================================================================
    # Clip Properties
    # =========================================================================
    
    def get_clip_details(self, track_index, clip_index):
        """
        Get detailed clip information.
        
        Returns comprehensive info including loop, launch, and
        type-specific settings.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
        
        Returns:
            dict: Detailed clip info
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            info = {
                "name": clip.name,
                "color": clip.color,
                "color_index": clip.color_index,
                "length": clip.length,
                
                # State
                "is_playing": clip.is_playing,
                "is_triggered": clip.is_triggered,
                "is_recording": clip.is_recording,
                
                # Loop settings
                "looping": clip.looping,
                "loop_start": clip.loop_start,
                "loop_end": clip.loop_end,
                
                # Markers
                "start_marker": clip.start_marker,
                "end_marker": clip.end_marker,
                
                # Launch settings
                "launch_mode": clip.launch_mode,
                "launch_quantization": clip.launch_quantization,
                "legato": clip.legato,
                
                # Type
                "is_midi_clip": clip.is_midi_clip,
                "is_audio_clip": clip.is_audio_clip
            }
            
            # Audio-specific
            if clip.is_audio_clip:
                info.update({
                    "warping": clip.warping,
                    "warp_mode": clip.warp_mode if hasattr(clip, 'warp_mode') else None,
                    "pitch_coarse": clip.pitch_coarse if hasattr(clip, 'pitch_coarse') else 0,
                    "pitch_fine": clip.pitch_fine if hasattr(clip, 'pitch_fine') else 0,
                    "gain": clip.gain if hasattr(clip, 'gain') else 1.0
                })
            
            # MIDI-specific
            if clip.is_midi_clip:
                if hasattr(clip, 'signature_numerator'):
                    info["time_signature"] = {
                        "numerator": clip.signature_numerator,
                        "denominator": clip.signature_denominator
                    }
            
            return info
        except Exception as e:
            self._log("Error getting clip details: " + str(e))
            raise
    
    def set_clip_name(self, track_index, clip_index, name):
        """
        Set a clip's name.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            name (str): New clip name
        
        Returns:
            dict: Updated name
        
        Live API:
            Clip.name (str property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.name = str(name)
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "name": clip.name
            }
        except Exception as e:
            self._log("Error setting clip name: " + str(e))
            raise
    
    def set_clip_color(self, track_index, clip_index, color=None, color_index=None):
        """
        Set a clip's color.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            color (int, optional): RGB color value
            color_index (int, optional): Palette index (0-69)
        
        Returns:
            dict: Updated color
        
        Live API:
            Clip.color (int property)
            Clip.color_index (int property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if color_index is not None:
                clip.color_index = int(color_index)
            elif color is not None:
                clip.color = int(color)
            
            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "color": clip.color,
                "color_index": clip.color_index
            }
        except Exception as e:
            self._log("Error setting clip color: " + str(e))
            raise
    
    # =========================================================================
    # Loop Settings
    # =========================================================================
    
    def set_clip_loop(self, track_index, clip_index, looping=None, 
                      loop_start=None, loop_end=None):
        """
        Configure clip loop settings.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            looping (bool, optional): Enable/disable looping
            loop_start (float, optional): Loop start in beats
            loop_end (float, optional): Loop end in beats
        
        Returns:
            dict: Updated loop settings
        
        Live API:
            Clip.looping (bool property)
            Clip.loop_start (float property)
            Clip.loop_end (float property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if looping is not None:
                clip.looping = bool(looping)
            if loop_start is not None:
                clip.loop_start = float(loop_start)
            if loop_end is not None:
                clip.loop_end = float(loop_end)
            
            return {
                "looping": clip.looping,
                "loop_start": clip.loop_start,
                "loop_end": clip.loop_end
            }
        except Exception as e:
            self._log("Error setting clip loop: " + str(e))
            raise
    
    def set_clip_markers(self, track_index, clip_index, start_marker=None,
                         end_marker=None):
        """
        Set clip start and end markers.
        
        These control the playback region within the clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            start_marker (float, optional): Start marker in beats
            end_marker (float, optional): End marker in beats
        
        Returns:
            dict: Updated marker positions
        
        Live API:
            Clip.start_marker (float property)
            Clip.end_marker (float property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if start_marker is not None:
                clip.start_marker = float(start_marker)
            if end_marker is not None:
                clip.end_marker = float(end_marker)
            
            return {
                "start_marker": clip.start_marker,
                "end_marker": clip.end_marker
            }
        except Exception as e:
            self._log("Error setting clip markers: " + str(e))
            raise
    
    def duplicate_loop(self, track_index, clip_index):
        """
        Duplicate the loop region (double the loop length).
        
        Copies the content within the loop and extends the loop.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
        
        Returns:
            dict: New loop settings
        
        Live API:
            Clip.duplicate_loop()
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.duplicate_loop()
            return {
                "duplicated": True,
                "loop_start": clip.loop_start,
                "loop_end": clip.loop_end,
                "length": clip.length
            }
        except Exception as e:
            self._log("Error duplicating loop: " + str(e))
            raise
    
    # =========================================================================
    # Launch Settings
    # =========================================================================
    
    def set_clip_launch_mode(self, track_index, clip_index, mode):
        """
        Set the clip's launch mode.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            mode (int): Launch mode
                0 = Trigger
                1 = Gate
                2 = Toggle
                3 = Repeat
        
        Returns:
            dict: Updated launch mode
        
        Live API:
            Clip.launch_mode (int property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            mode = int(mode)
            if mode not in (0, 1, 2, 3):
                raise ValueError("Launch mode must be 0-3")
            
            clip.launch_mode = mode
            
            mode_names = {0: "Trigger", 1: "Gate", 2: "Toggle", 3: "Repeat"}
            return {
                "launch_mode": mode,
                "launch_mode_name": mode_names[mode]
            }
        except Exception as e:
            self._log("Error setting launch mode: " + str(e))
            raise
    
    def set_clip_launch_quantization(self, track_index, clip_index, quantization):
        """
        Set the clip's launch quantization.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            quantization (int): Quantization index
                -1 = Default (use global)
                0 = None, 1 = 8 Bars, 2 = 4 Bars, etc.
        
        Returns:
            dict: Updated launch quantization
        
        Live API:
            Clip.launch_quantization (int property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.launch_quantization = int(quantization)
            return {
                "launch_quantization": clip.launch_quantization
            }
        except Exception as e:
            self._log("Error setting launch quantization: " + str(e))
            raise
    
    def set_clip_legato(self, track_index, clip_index, legato):
        """
        Set the clip's legato mode.
        
        When enabled, clip playback continues from the same
        position as the previously playing clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            legato (bool): Enable/disable legato
        
        Returns:
            dict: Updated legato setting
        
        Live API:
            Clip.legato (bool property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.legato = bool(legato)
            return {
                "legato": clip.legato
            }
        except Exception as e:
            self._log("Error setting legato: " + str(e))
            raise
    
    # =========================================================================
    # Audio Clip Properties (Warping, Pitch, Gain)
    # =========================================================================

    def set_clip_audio_properties(self, track_index, clip_index, 
                                warp_mode=None, warping=None, 
                                pitch_coarse=None, pitch_fine=None, 
                                gain=None, ram_mode=None):
        """
        Set properties specific to audio clips.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            warp_mode (int, optional): Warp mode (0=Beats, 1=Tones, 2=Texture, 3=Repitch, 4=Complex, 5=Complex Pro, 6=Rex)
            warping (bool, optional): Enable/disable warping
            pitch_coarse (int, optional): Pitch in semitones
            pitch_fine (int, optional): Pitch fine tune (-50 to 50 cents)
            gain (float, optional): Gain (0.0 to 1.0)
            ram_mode (bool, optional): Load into RAM
            
        Returns:
            dict: Updated audio properties
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            if not getattr(clip, 'is_audio_clip', False):
                return {"status": "error", "message": "Not an audio clip"}

            if warp_mode is not None:
                clip.warp_mode = int(warp_mode)
            if warping is not None:
                clip.warping = bool(warping)
            if pitch_coarse is not None:
                clip.pitch_coarse = int(pitch_coarse)
            if pitch_fine is not None:
                clip.pitch_fine = int(pitch_fine)
            if gain is not None:
                clip.gain = float(gain)
            if ram_mode is not None:
                clip.ram_mode = bool(ram_mode)

            return {
                "track_index": track_index,
                "clip_index": clip_index,
                "warp_mode": clip.warp_mode,
                "warping": clip.warping,
                "pitch_coarse": clip.pitch_coarse,
                "pitch_fine": clip.pitch_fine,
                "gain": clip.gain,
                "ram_mode": clip.ram_mode
            }
        except Exception as e:
            self._log("Error setting audio properties: " + str(e))
            raise

    # =========================================================================
    # Edit Operations (Crop, Quantize)
    # =========================================================================

    def crop_clip(self, track_index, clip_index):
        """
        Crop the clip.
        
        Removes audio/notes outside the loop (if looping) or markers.
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.crop()
            return {"status": "success", "message": "Clip cropped"}
        except Exception as e:
            self._log("Error cropping clip: " + str(e))
            raise

    def quantize_clip(self, track_index, clip_index, quantization, amount=1.0):
        """
        Quantize clip notes or warp markers.
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.quantize(int(quantization), float(amount))
            return {"status": "success", "quantization": quantization}
        except Exception as e:
            self._log("Error quantizing clip: " + str(e))
            raise

    # =========================================================================
    # Scrubbing
    # =========================================================================

    def scrub_clip(self, track_index, clip_index, position):
        """
        Start scrubbing playback at position.
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.scrub(float(position))
            return {"status": "success", "scrubbing": True, "position": position}
        except Exception as e:
            self._log("Error scrubbing clip: " + str(e))
            raise

    def stop_scrub(self, track_index, clip_index):
        """Stop scrubbing."""
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.stop_scrub()
            return {"status": "success", "scrubbing": False}
        except Exception as e:
            self._log("Error stopping scrub: " + str(e))
            raise

    # =========================================================================
    # Envelopes / Automation
    # =========================================================================

    # =========================================================================
    # Envelopes / Automation
    # =========================================================================

    def _resolve_automation_parameter(self, track_index, device_id, parameter_id):
        """
        Resolve a DeviceParameter object for automation.
        
        Args:
            track_index (int): Track index
            device_id (str/int): "mixer" or device index
            parameter_id (str/int): Parameter name or index
            
        Returns:
            DeviceParameter: The parameter object
        """
        # Validate track
        if track_index < 0 or track_index >= len(self.song.tracks):
            raise IndexError("Track index out of range")
        track = self.song.tracks[track_index]
        
        # Get device or mixer
        target_device = None
        if str(device_id).lower() == "mixer":
             target_device = track.mixer_device
        else:
            try:
                idx = int(device_id)
                if idx < 0 or idx >= len(track.devices):
                     raise IndexError("Device index out of range")
                target_device = track.devices[idx]
            except ValueError:
                # Could support device name searching here, but let's stick to index for robustness first
                # Or try to find by name if string
                 for dev in track.devices:
                     if dev.name == device_id:
                         target_device = dev
                         break
                 if not target_device:
                     raise ValueError("Device '{}' not found".format(device_id))

        if not target_device:
             raise ValueError("Could not resolve target device")

        # Get parameter
        parameters = target_device.parameters
        
        # Try index
        try:
            p_idx = int(parameter_id)
            if 0 <= p_idx < len(parameters):
                return parameters[p_idx]
        except ValueError:
            pass

        # Try name (case-insensitive)
        param_name_lower = str(parameter_id).lower()
        for p in parameters:
            if p.name.lower() == param_name_lower:
                return p
        
        # Try original name if available
        for p in parameters:
             if hasattr(p, 'original_name') and p.original_name.lower() == param_name_lower:
                 return p

        raise ValueError("Parameter '{}' not found on device '{}'".format(parameter_id, target_device.name))

    def get_clip_envelope(self, track_index, clip_index, device_id, parameter_id):
        """
        Get automation envelope status for a parameter.
        
        Note: The API does not expose reading ALL breakpoints easily without converting 
        from internal data structures. We can check if it exists and maybe get value at time.
        
        Returns:
            dict: Envelope status (has_envelope, is_debug, etc)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            param = self._resolve_automation_parameter(track_index, device_id, parameter_id)
            
            envelope = clip.automation_envelope(param)
            
            return {
                "has_envelope": envelope is not None,
                "parameter_name": param.name,
                "device_name": param.canonical_parent.name if param.canonical_parent else "Unknown"
            }
        except Exception as e:
            self._log("Error getting envelope: " + str(e))
            raise

    def set_clip_envelope_step(self, track_index, clip_index, device_id, parameter_id, 
                               time, length, value):
        """
        Insert a flat automation step.
        
        Args:
            time (float): Start time in beats
            length (float): Duration in beats
            value (float): Value (0.0 to 1.0 usually, depends on range)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            param = self._resolve_automation_parameter(track_index, device_id, parameter_id)
            
            envelope = clip.automation_envelope(param)
            if envelope is None:
                envelope = clip.create_automation_envelope(param)
            
            # Value normalization might be needed if user passes 0-1 but param expects min-max
            # API documentation for insert_step usually expects normalized? 
            # Actually insert_step args in XML were just float, float, float.
            # Usually time, length, value.
            
            envelope.insert_step(float(time), float(length), float(value))
            
            return {
                "status": "success", 
                "message": "Inserted step"
            }
        except Exception as e:
            self._log("Error setting envelope step: " + str(e))
            raise

    def clear_clip_envelope(self, track_index, clip_index, device_id, parameter_id):
        """Delete automation for a parameter."""
        try:
            clip = self._get_clip(track_index, clip_index)
            param = self._resolve_automation_parameter(track_index, device_id, parameter_id)
            
            clip.clear_envelope(param)
            return {"status": "success", "message": "Envelope cleared"}
        except Exception as e:
            self._log("Error clearing envelope: " + str(e))
            raise

    
    # =========================================================================
    # Audio Clip Settings
    # =========================================================================
    
    def set_clip_warp(self, track_index, clip_index, warping=None, warp_mode=None):
        """
        Configure audio clip warp settings.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            warping (bool, optional): Enable/disable warping
            warp_mode (int, optional): Warp mode
                0 = Beats, 1 = Tones, 2 = Texture, 3 = Re-Pitch,
                4 = Complex, 5 = Complex Pro
        
        Returns:
            dict: Updated warp settings
        
        Raises:
            RuntimeError: If clip is not an audio clip
        
        Live API:
            Clip.warping (bool property)
            Clip.warp_mode (int property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_audio_clip:
                raise RuntimeError("Warp settings only apply to audio clips")
            
            if warping is not None:
                clip.warping = bool(warping)
            if warp_mode is not None:
                clip.warp_mode = int(warp_mode)
            
            mode_names = {
                0: "Beats", 1: "Tones", 2: "Texture", 
                3: "Re-Pitch", 4: "Complex", 5: "Complex Pro"
            }
            
            return {
                "warping": clip.warping,
                "warp_mode": clip.warp_mode,
                "warp_mode_name": mode_names.get(clip.warp_mode, "Unknown")
            }
        except Exception as e:
            self._log("Error setting clip warp: " + str(e))
            raise
    
    def set_clip_pitch(self, track_index, clip_index, coarse=None, fine=None):
        """
        Set audio clip pitch shift.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            coarse (int, optional): Coarse pitch in semitones (-48 to 48)
            fine (float, optional): Fine pitch in cents (-50 to 50)
        
        Returns:
            dict: Updated pitch settings
        
        Raises:
            RuntimeError: If clip is not an audio clip
        
        Live API:
            Clip.pitch_coarse (int property)
            Clip.pitch_fine (float property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_audio_clip:
                raise RuntimeError("Pitch settings only apply to audio clips")
            
            if coarse is not None:
                coarse = max(-48, min(48, int(coarse)))
                clip.pitch_coarse = coarse
            if fine is not None:
                fine = max(-50.0, min(50.0, float(fine)))
                clip.pitch_fine = fine
            
            return {
                "pitch_coarse": clip.pitch_coarse,
                "pitch_fine": clip.pitch_fine
            }
        except Exception as e:
            self._log("Error setting clip pitch: " + str(e))
            raise
    
    def set_clip_gain(self, track_index, clip_index, gain):
        """
        Set audio clip gain.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            gain (float): Gain value (0.0 to 1.0, where 0.5 = 0dB)
        
        Returns:
            dict: Updated gain
        
        Raises:
            RuntimeError: If clip is not an audio clip
        
        Live API:
            Clip.gain (float property)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_audio_clip:
                raise RuntimeError("Gain settings only apply to audio clips")
            
            gain = max(0.0, min(1.0, float(gain)))
            clip.gain = gain
            
            return {
                "gain": clip.gain
            }
        except Exception as e:
            self._log("Error setting clip gain: " + str(e))
            raise
    
    # =========================================================================
    # Clip Operations
    # =========================================================================
    
    def quantize_clip(self, track_index, clip_index, grid=5, amount=1.0):
        """
        Quantize MIDI notes in a clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            grid (int): Quantization grid
                0 = 1/4, 1 = 1/8, 2 = 1/8T, 3 = 1/8 + 1/8T,
                4 = 1/16, 5 = 1/16T, 6 = 1/16 + 1/16T, 7 = 1/32
            amount (float): Quantize strength (0.0 to 1.0)
        
        Returns:
            dict: Quantize result
        
        Live API:
            Clip.quantize(grid, amount)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_midi_clip:
                raise RuntimeError("Quantize only applies to MIDI clips")
            
            amount = max(0.0, min(1.0, float(amount)))
            clip.quantize(int(grid), amount)
            
            return {
                "quantized": True,
                "grid": grid,
                "amount": amount
            }
        except Exception as e:
            self._log("Error quantizing clip: " + str(e))
            raise
    
    def crop_clip(self, track_index, clip_index):
        """
        Crop a clip to its loop region.
        
        Removes content outside the loop.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
        
        Returns:
            dict: Crop result
        
        Live API:
            Clip.crop()
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            clip.crop()
            return {
                "cropped": True,
                "length": clip.length
            }
        except Exception as e:
            self._log("Error cropping clip: " + str(e))
            raise
    
    def clear_clip(self, track_index, clip_index):
        """
        Clear all content from a MIDI clip.
        
        Removes all notes and envelopes from the clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
        
        Returns:
            dict: Clear result
        
        Raises:
            RuntimeError: If clip is not a MIDI clip
        
        Live API:
            Clip.remove_notes_extended() (with full range)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_midi_clip:
                raise RuntimeError("Clear only applies to MIDI clips")
            
            # Remove all notes by selecting entire clip range
            clip.remove_notes_extended(0, 127, 0.0, clip.length)
            
            return {
                "cleared": True
            }
        except Exception as e:
            self._log("Error clearing clip: " + str(e))
            raise
    
    def deselect_all_notes(self, track_index, clip_index):
        """
        Deselect all notes in a MIDI clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
        
        Returns:
            dict: Deselect result
        
        Live API:
            Clip.deselect_all_notes()
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_midi_clip:
                raise RuntimeError("Deselect applies only to MIDI clips")
            
            clip.deselect_all_notes()
            return {"deselected": True}
        except Exception as e:
            self._log("Error deselecting notes: " + str(e))
            raise
    
    def select_all_notes(self, track_index, clip_index):
        """
        Select all notes in a MIDI clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
        
        Returns:
            dict: Select result
        
        Live API:
            Clip.select_all_notes()
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            
            if not clip.is_midi_clip:
                raise RuntimeError("Select applies only to MIDI clips")
            
            clip.select_all_notes()
            return {"selected": True}
        except Exception as e:
            self._log("Error selecting notes: " + str(e))
            raise

    def get_notes(self, track_index, clip_index, start_time, time_span, start_pitch=0, pitch_span=128):
        """
        Get MIDI notes in a range.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            start_time (float): Start time in beats
            time_span (float): Duration in beats
            start_pitch (int): Start pitch (0-127)
            pitch_span (int): Pitch range
            
        Returns:
            dict: List of notes
                Each note is (pitch, time, duration, velocity, mute)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            if not clip.is_midi_clip:
                raise RuntimeError("Not a MIDI clip")
                
            notes = clip.get_notes(start_time, int(start_pitch), time_span, int(pitch_span))
            # notes is a tuple of tuples
            return {
                "notes": [list(n) for n in notes] # Convert to list for JSON serialization
            }
        except Exception as e:
            self._log("Error getting notes: " + str(e))
            raise

    def set_notes(self, track_index, clip_index, notes):
        """
        Add notes to the clip.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            notes (list): List of note tuples (pitch, time, duration, velocity, mute)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            if not clip.is_midi_clip:
                raise RuntimeError("Not a MIDI clip")
            
            # Convert list of lists/tuples to tuple of tuples for API
            note_tuples = tuple(tuple(n) for n in notes)
            clip.set_notes(note_tuples)
            return {"status": "success", "note_count": len(notes)}
        except Exception as e:
            self._log("Error setting notes: " + str(e))
            raise

    def remove_notes(self, track_index, clip_index, start_time, time_span, start_pitch=0, pitch_span=128):
        """
        Remove notes in a range.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            start_time (float): Start time
            time_span (float): Duration
            start_pitch (int): Start pitch
            pitch_span (int): Pitch range
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            if not clip.is_midi_clip:
                raise RuntimeError("Not a MIDI clip")
                
            clip.remove_notes(start_time, int(start_pitch), time_span, int(pitch_span))
            return {"status": "success", "removed_range": [start_time, time_span]}
        except Exception as e:
            self._log("Error removing notes: " + str(e))
            raise

    def replace_selected_notes(self, track_index, clip_index, notes):
        """
        Replace currently selected notes with new notes.
        
        Args:
            track_index (int): Track index
            clip_index (int): Clip slot index
            notes (list): List of note tuples (pitch, time, duration, velocity, mute)
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            if not clip.is_midi_clip:
                raise RuntimeError("Not a MIDI clip")
                
            note_tuples = tuple(tuple(n) for n in notes)
            clip.replace_selected_notes(note_tuples)
            return {"status": "success"}
        except Exception as e:
            self._log("Error replacing selected notes: " + str(e))
            raise

    def get_notes_extended(self, track_index, clip_index, start_time, time_span, start_pitch=0, pitch_span=128):
        """
        Get MIDI notes with advanced properties (probability, velocity deviation).
        
        Args:
            track_index, clip_index: Location
            start_time, time_span: Time range
            start_pitch, pitch_span: Pitch range
            
        Returns:
            dict: List of note dictionaries with IDs
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            if not clip.is_midi_clip:
                raise RuntimeError("Not a MIDI clip")
                
            # get_notes_extended returns a MidiNoteVector (list of MidiNote objects)
            notes_vector = clip.get_notes_extended(
                int(start_pitch), int(pitch_span), 
                float(start_time), float(time_span)
            )
            
            serialized_notes = []
            for note in notes_vector:
                serialized_notes.append({
                    "note_id": note.note_id,
                    "pitch": note.pitch,
                    "start_time": note.start_time,
                    "duration": note.duration,
                    "velocity": note.velocity,
                    "mute": note.mute,
                    "probability": getattr(note, "probability", 1.0),
                    "velocity_deviation": getattr(note, "velocity_deviation", 0.0),
                    "release_velocity": getattr(note, "release_velocity", 64.0)
                })
            
            return {
                "notes": serialized_notes,
                "count": len(serialized_notes)
            }
        except Exception as e:
            self._log("Error getting extended notes: " + str(e))
            raise

    def update_notes(self, track_index, clip_index, notes):
        """
        Update specific MIDI notes by ID (for probability/humanization).
        
        Logic:
        1. Fetch all notes in the relevant range (we use the full clip range to be safe finding IDs).
        2. Match provided notes by note_id.
        3. Apply changes to the live objects.
        4. Call apply_note_modifications.
        
        Args:
            track_index, clip_index: Location
            notes (list): List of dicts with 'note_id' and properties to update
        """
        try:
            clip = self._get_clip(track_index, clip_index)
            if not clip.is_midi_clip:
                raise RuntimeError("Not a MIDI clip")
            
            if not notes:
                return {"status": "success", "updated_count": 0}
            
            # 1. Fetch all notes to ensure we find simple ID matches
            # Optimization: We could try to calculate bounding box of incoming notes, 
            # but getting all notes is safer to ensure we find the ID if it moved slightly.
            # Assuming typical clip isn't gigantic.
            all_notes_vector = clip.get_notes_extended(0, 128, 0.0, clip.length)
            
            # Index live notes by ID for O(1) lookup
            # Note: note_id is unique within clip
            live_notes_map = {n.note_id: n for n in all_notes_vector}
            
            updated_objects = []
            updates_count = 0
            
            for note_data in notes:
                nid = note_data.get("note_id")
                if nid is None:
                    continue
                    
                live_note = live_notes_map.get(nid)
                if live_note:
                    # Apply updates if key exists in payload
                    if "pitch" in note_data: live_note.pitch = int(note_data["pitch"])
                    if "start_time" in note_data: live_note.start_time = float(note_data["start_time"])
                    if "duration" in note_data: live_note.duration = float(note_data["duration"])
                    if "velocity" in note_data: live_note.velocity = float(note_data["velocity"])
                    if "mute" in note_data: live_note.mute = bool(note_data["mute"])
                    
                    # Advanced properties
                    if "probability" in note_data: 
                        setattr(live_note, "probability", float(note_data["probability"]))
                    if "velocity_deviation" in note_data: 
                        setattr(live_note, "velocity_deviation", float(note_data["velocity_deviation"]))
                    if "release_velocity" in note_data: 
                        setattr(live_note, "release_velocity", float(note_data["release_velocity"]))
                    
                    updated_objects.append(live_note)
                    updates_count += 1
            
            if updated_objects:
                # API expects a vector/list of modified objects
                clip.apply_note_modifications(updated_objects)
                
            return {
                "status": "success", 
                "updated_count": updates_count
            }
        except Exception as e:
            self._log("Error updating notes: " + str(e))
            raise
