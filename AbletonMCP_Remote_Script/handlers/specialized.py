"""
Specialized Device Handler Module for AbletonMCP Remote Script.

This module provides specialized control for complex built-in devices
such as EQ8, Compressor, and other devices with specific parameter structures.

Key Responsibilities:
    - EQ8 filter band management
    - Compressor sidechain routing
    - Device-specific macro controls

For Future Agents:
    - Uses device.class_name to identify devices
    - EQ8 parameters are named "1 Filter On A", "1 Frequency A", etc.
    - Compressor sidechain requires routing settings

Live 11 API Reference:
    - Live.Device.Device class
    - DeviceParameter class
    - See: https://nsuspray.github.io/Live_API_Doc/11.0.0.xml
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase


class SpecializedDeviceHandler(HandlerBase):
    """
    Handler for specialized device operations in AbletonMCP.
    
    Attributes:
        mcp: Reference to the main AbletonMCP ControlSurface instance
    """
    
    def _find_device_by_class(self, track_index, class_name, device_index=None):
        """Find a device by class name on a track."""
        tracks = self.song.tracks
        if track_index < 0 or track_index >= len(tracks):
            raise IndexError("Track index out of range")
        
        track = tracks[track_index]
        found_devices = []
        
        for device in track.devices:
            if hasattr(device, 'class_name'):
                 d_class = device.class_name.lower()
                 target = class_name.lower()
                 if d_class == target or target in d_class or (target == "eq8" and "eq8" in d_class):
                     found_devices.append(device)
        
        if not found_devices:
            raise RuntimeError("No device of class {} found on track {}".format(
                class_name, track_index))
        
        if device_index is None:
            return found_devices[0]
        
        if device_index < 0 or device_index >= len(found_devices):
            raise IndexError("Device index {} out of range".format(device_index))
        
        return found_devices[device_index]

    # =========================================================================
    # EQ8 Control
    # =========================================================================
    
    def set_eq8_band(self, track_index, band_index, enabled=None, 
                     freq=None, gain=None, q=None, filter_type=None, device_index=None):
        """
        Configure a band on an EQ8 device.
        
        Args:
            track_index (int): Track index
            band_index (int): Band index (1-8)
            enabled (bool, optional): Enable/disable band
            freq (float, optional): Frequency in Hz
            gain (float, optional): Gain in dB
            q (float, optional): Resonance/Q
            filter_type (int, optional): Filter mode index
                0=Cut12, 1=Cut48, 2=LowShelf, 3=Bell, 4=HighShelf, 
                5=Notch, 6=HighPass, 7=LowPass
            device_index (int, optional): Index of EQ8 device if multiple
        
        Returns:
            dict: Updated band settings
        """
        try:
            device = self._find_device_by_class(track_index, 'Eq8', device_index)
            
            if band_index < 1 or band_index > 8:
                raise ValueError("Band index must be 1-8")
            
            # Parameter naming convention for EQ8:
            # "1 Filter On A" or "1 Filter On" depending on view?
            # Actually standard parameters are:
            # "Band 1 On", "Band 1 Freq", "Band 1 Gain", "Band 1 Q", "Band 1 Type"
            # But internally they might differ. We will search by name prefix.
            
            prefix = str(band_index) + " "  # e.g., "1 "
            
            updates = {}
            
            for param in device.parameters:
                name = param.name
                
                # Check for enabled (often "1 Filter On A")
                if enabled is not None and name.startswith(prefix) and "On" in name:
                     param.value = 1.0 if enabled else 0.0
                     updates["enabled"] = bool(param.value)
                
                # Check for frequency (often "1 Frequency A")
                if freq is not None and name.startswith(prefix) and "Freq" in name:
                    # Map Hz to parameter range (approximate)
                    # For now just setting value directly if within range
                    # This might need normalization logic later
                    param.value = float(freq)
                    updates["freq"] = param.value
                
                # Check for gain (often "1 Gain A")
                if gain is not None and name.startswith(prefix) and "Gain" in name:
                    param.value = float(gain)
                    updates["gain"] = param.value
                    
                # Check for Q (often "1 Resonance A")
                if q is not None and name.startswith(prefix) and "Resonance" in name:
                    param.value = float(q)
                    updates["q"] = param.value
                
                # Check for type (often "1 Filter Type A")
                if filter_type is not None and name.startswith(prefix) and "Type" in name:
                    param.value = float(filter_type)
                    updates["type"] = int(param.value)
            
            return {
                "track_index": track_index,
                "device_name": device.name,
                "band_index": band_index,
                "updates": updates
            }
        except Exception as e:
            self._log("Error setting EQ8 band: " + str(e))
            raise
            
    # =========================================================================
    # Compressor Control
    # =========================================================================
    
    def set_compressor_sidechain(self, track_index, enabled=None, 
                                 source_track_index=None, gain=None, mix=None, device_index=None):
        """
        Configure Compressor sidechain settings.
        
        Args:
            track_index (int): Track index
            enabled (bool, optional): Enable sidechain
            source_track_index (int, optional): Source track for sidechain
            gain (float, optional): Sidechain gain in dB
            mix (float, optional): Sidechain mix/dry-wet
            device_index (int, optional): Index of Compressor if multiple
        
        Returns:
            dict: Updated sidechain settings
        """
        try:
            device = self._find_device_by_class(track_index, 'Compressor2', device_index)
            
            updates = {}
            
            for param in device.parameters:
                # "Sidechain On" not directly exposed as param sometimes?
                # Check specific parameters
                
                if enabled is not None and param.name == "Sidechain":
                    param.value = 1.0 if enabled else 0.0
                    updates["enabled"] = bool(param.value)
                
                if gain is not None and param.name == "Gain":
                    param.value = float(gain)
                    updates["gain"] = param.value
                
                if mix is not None and param.name == "Dry/Wet":
                    param.value = float(mix)
                    updates["mix"] = param.value
            
            # Routing logic is complex as it involves internal routing objects
            # not easily exposed via simple parameters.
            # Usually requires selecting the routing source from the device chain.
            
            return {
                "track_index": track_index,
                "device_name": device.name,
                "updates": updates,
                "note": "Sidechain source routing requires detailed routing API"
            }
        except Exception as e:
            self._log("Error setting compressor sidechain: " + str(e))
            raise

    # =========================================================================
    # Generic Specialized Device Info
    # =========================================================================
    
    def get_specialized_device_info(self, track_index, device_index=0):
        """
        Get detailed info about a specialized device.
        
        Works with: EQ8, Compressor, MaxDevice, WavetableDevice, 
        HybridReverbDevice, TransmuteDevice, etc.
        
        Args:
            track_index (int): Track index
            device_index (int): Device index on track
            
        Returns:
            dict: Device-specific properties based on class
            
        Live API:
            Device.class_name to identify, then class-specific properties
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            
            device = track.devices[device_index]
            class_name = getattr(device, 'class_name', 'Unknown')
            
            result = {
                "status": "success",
                "track_index": track_index,
                "device_index": device_index,
                "name": getattr(device, 'name', ''),
                "class_name": class_name,
                "class_display_name": getattr(device, 'class_display_name', class_name),
                "is_active": getattr(device, 'is_active', True),
                "can_have_chains": getattr(device, 'can_have_chains', False),
                "can_have_drum_pads": getattr(device, 'can_have_drum_pads', False),
            }
            
            # EQ8-specific
            if 'eq8' in class_name.lower():
                result["device_type"] = "Eq8Device"
                if hasattr(device, 'edit_mode'):
                    result["edit_mode"] = device.edit_mode
                if hasattr(device, 'global_mode'):
                    result["global_mode"] = device.global_mode
                if hasattr(device, 'oversample'):
                    result["oversample"] = device.oversample
            
            # Compressor-specific
            elif 'compressor' in class_name.lower():
                result["device_type"] = "CompressorDevice"
                if hasattr(device, 'available_input_routing_types'):
                    result["available_input_routing_types"] = list(device.available_input_routing_types)
                if hasattr(device, 'input_routing_type'):
                    result["input_routing_type"] = str(device.input_routing_type)
            
            # MaxDevice-specific
            elif class_name == 'MaxForLiveMidiEffect' or class_name == 'MaxForLiveAudioEffect' or 'max' in class_name.lower():
                result["device_type"] = "MaxDevice"
                if hasattr(device, 'audio_inputs'):
                    result["audio_input_count"] = len(device.audio_inputs)
                if hasattr(device, 'audio_outputs'):
                    result["audio_output_count"] = len(device.audio_outputs)
                if hasattr(device, 'midi_inputs'):
                    result["midi_input_count"] = len(device.midi_inputs)
                if hasattr(device, 'midi_outputs'):
                    result["midi_output_count"] = len(device.midi_outputs)
                if hasattr(device, 'get_bank_count'):
                    result["bank_count"] = device.get_bank_count()
            
            # WavetableDevice-specific
            elif 'wavetable' in class_name.lower():
                result["device_type"] = "WavetableDevice"
                if hasattr(device, 'filter_routing'):
                    result["filter_routing"] = int(device.filter_routing)
                if hasattr(device, 'mono_poly'):
                    result["mono_poly"] = int(device.mono_poly)
                if hasattr(device, 'poly_voices'):
                    result["poly_voices"] = int(device.poly_voices)
                if hasattr(device, 'unison_mode'):
                    result["unison_mode"] = int(device.unison_mode)
                if hasattr(device, 'unison_voice_count'):
                    result["unison_voice_count"] = int(device.unison_voice_count)
                if hasattr(device, 'oscillator_wavetable_categories'):
                    cats = device.oscillator_wavetable_categories
                    result["wavetable_categories"] = list(cats) if cats else []
                if hasattr(device, 'oscillator_1_wavetable_category'):
                    result["oscillator_1_category"] = int(device.oscillator_1_wavetable_category)
                if hasattr(device, 'oscillator_1_wavetable_index'):
                    result["oscillator_1_index"] = int(device.oscillator_1_wavetable_index)
                if hasattr(device, 'oscillator_2_wavetable_category'):
                    result["oscillator_2_category"] = int(device.oscillator_2_wavetable_category)
                if hasattr(device, 'oscillator_2_wavetable_index'):
                    result["oscillator_2_index"] = int(device.oscillator_2_wavetable_index)
            
            # HybridReverbDevice-specific
            elif 'hybrid' in class_name.lower() and 'reverb' in class_name.lower():
                result["device_type"] = "HybridReverbDevice"
                if hasattr(device, 'ir_category_list'):
                    result["ir_categories"] = list(device.ir_category_list)
                if hasattr(device, 'ir_category_index'):
                    result["ir_category_index"] = int(device.ir_category_index)
                if hasattr(device, 'ir_file_list'):
                    result["ir_files"] = list(device.ir_file_list)
                if hasattr(device, 'ir_file_index'):
                    result["ir_file_index"] = int(device.ir_file_index)
                if hasattr(device, 'ir_attack_time'):
                    result["ir_attack_time"] = float(device.ir_attack_time)
                if hasattr(device, 'ir_decay_time'):
                    result["ir_decay_time"] = float(device.ir_decay_time)
                if hasattr(device, 'ir_size_factor'):
                    result["ir_size_factor"] = float(device.ir_size_factor)
            
            # TransmuteDevice-specific
            elif 'transmute' in class_name.lower():
                result["device_type"] = "TransmuteDevice"
                if hasattr(device, 'frequency_dial_mode_list'):
                    result["frequency_dial_modes"] = list(device.frequency_dial_mode_list)
                if hasattr(device, 'frequency_dial_mode_index'):
                    result["frequency_dial_mode_index"] = int(device.frequency_dial_mode_index)
                if hasattr(device, 'midi_gate_list'):
                    result["midi_gate_modes"] = list(device.midi_gate_list)
                if hasattr(device, 'midi_gate_index'):
                    result["midi_gate_index"] = int(device.midi_gate_index)
                if hasattr(device, 'mod_mode_list'):
                    result["mod_modes"] = list(device.mod_mode_list)
                if hasattr(device, 'mod_mode_index'):
                    result["mod_mode_index"] = int(device.mod_mode_index)
                if hasattr(device, 'pitch_mode_list'):
                    result["pitch_modes"] = list(device.pitch_mode_list)
                if hasattr(device, 'pitch_mode_index'):
                    result["pitch_mode_index"] = int(device.pitch_mode_index)
                if hasattr(device, 'mono_poly_list'):
                    result["mono_poly_modes"] = list(device.mono_poly_list)
                if hasattr(device, 'mono_poly_index'):
                    result["mono_poly_index"] = int(device.mono_poly_index)
                if hasattr(device, 'polyphony'):
                    result["polyphony"] = int(device.polyphony)
                if hasattr(device, 'pitch_bend_range'):
                    result["pitch_bend_range"] = int(device.pitch_bend_range)
            
            else:
                result["device_type"] = "GenericDevice"
            
            return result
            
        except Exception as e:
            self._log("Error getting specialized device info: " + str(e))
            raise
    
    # =========================================================================
    # MaxDevice Control
    # =========================================================================
    
    def get_max_device_banks(self, track_index, device_index=0):
        """
        Get bank info for a Max for Live device.
        
        Args:
            track_index (int): Track index
            device_index (int): Device index
            
        Returns:
            dict: Bank names and parameter indices
            
        Live API:
            MaxDevice.get_bank_count()
            MaxDevice.get_bank_name(index)
            MaxDevice.get_bank_parameters(index)
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            
            device = track.devices[device_index]
            
            if not hasattr(device, 'get_bank_count'):
                return {"status": "error", "message": "Not a Max for Live device"}
            
            bank_count = device.get_bank_count()
            banks = []
            
            for i in range(bank_count):
                bank_data = {
                    "index": i,
                    "name": device.get_bank_name(i) if hasattr(device, 'get_bank_name') else "Bank {}".format(i),
                }
                if hasattr(device, 'get_bank_parameters'):
                    bank_data["parameter_indices"] = list(device.get_bank_parameters(i))
                banks.append(bank_data)
            
            return {
                "status": "success",
                "track_index": track_index,
                "device_index": device_index,
                "device_name": device.name,
                "bank_count": bank_count,
                "banks": banks
            }
            
        except Exception as e:
            self._log("Error getting Max device banks: " + str(e))
            raise
    
    # =========================================================================
    # WavetableDevice Control
    # =========================================================================
    
    def get_wavetable_oscillator(self, track_index, osc_number, device_index=0):
        """
        Get wavetable settings for an oscillator.
        
        Args:
            track_index (int): Track index
            osc_number (int): Oscillator number (1 or 2)
            device_index (int): Device index
            
        Returns:
            dict: Oscillator wavetable info
            
        Live API:
            WavetableDevice.oscillator_1_wavetable_category
            WavetableDevice.oscillator_1_wavetable_index
            WavetableDevice.oscillator_1_wavetables
            WavetableDevice.oscillator_1_effect_mode
        """
        try:
            device = self._find_device_by_class(track_index, 'Wavetable', device_index)
            
            if osc_number not in [1, 2]:
                raise ValueError("Oscillator number must be 1 or 2")
            
            prefix = "oscillator_{}_".format(osc_number)
            
            result = {
                "status": "success",
                "track_index": track_index,
                "oscillator": osc_number,
            }
            
            if hasattr(device, prefix + 'wavetable_category'):
                result["category_index"] = getattr(device, prefix + 'wavetable_category')
            if hasattr(device, prefix + 'wavetable_index'):
                result["wavetable_index"] = getattr(device, prefix + 'wavetable_index')
            if hasattr(device, prefix + 'wavetables'):
                wts = getattr(device, prefix + 'wavetables')
                result["wavetables"] = list(wts) if wts else []
            if hasattr(device, prefix + 'effect_mode'):
                result["effect_mode"] = getattr(device, prefix + 'effect_mode')
            
            return result
            
        except Exception as e:
            self._log("Error getting wavetable oscillator: " + str(e))
            raise
    
    def get_wavetable_modulation(self, track_index, target_index, source, device_index=0):
        """
        Get modulation amount between target and source.
        
        Args:
            track_index (int): Track index
            target_index (int): Modulation target index
            source (int): Modulation source (ModulationSource enum)
            device_index (int): Device index
            
        Returns:
            dict: Modulation value
            
        Live API:
            WavetableDevice.get_modulation_value(target_index, source)
        """
        try:
            device = self._find_device_by_class(track_index, 'Wavetable', device_index)
            
            if not hasattr(device, 'get_modulation_value'):
                return {"status": "error", "message": "get_modulation_value not available"}
            
            value = device.get_modulation_value(target_index, source)
            
            target_name = ""
            if hasattr(device, 'get_modulation_target_parameter_name'):
                target_name = device.get_modulation_target_parameter_name(target_index)
            
            return {
                "status": "success",
                "target_index": target_index,
                "target_name": target_name,
                "source": source,
                "value": value
            }
            
        except Exception as e:
            self._log("Error getting wavetable modulation: " + str(e))
            raise
    
    def set_wavetable_modulation(self, track_index, target_index, source, value, device_index=0):
        """
        Set modulation amount between target and source.
        
        Args:
            track_index (int): Track index
            target_index (int): Modulation target index
            source (int): Modulation source
            value (float): Modulation amount (-1.0 to 1.0)
            device_index (int): Device index
            
        Returns:
            dict: Updated modulation
            
        Live API:
            WavetableDevice.set_modulation_value(target_index, source, value)
        """
        try:
            device = self._find_device_by_class(track_index, 'Wavetable', device_index)
            
            if not hasattr(device, 'set_modulation_value'):
                return {"status": "error", "message": "set_modulation_value not available"}
            
            device.set_modulation_value(target_index, source, value)
            
            return {
                "status": "success",
                "target_index": target_index,
                "source": source,
                "value": value
            }
            
        except Exception as e:
            self._log("Error setting wavetable modulation: " + str(e))
            raise
    
    # =========================================================================
    # HybridReverbDevice Control
    # =========================================================================
    
    def get_hybrid_reverb_ir(self, track_index, device_index=0):
        """
        Get Hybrid Reverb impulse response settings.
        
        Args:
            track_index (int): Track index
            device_index (int): Device index
            
        Returns:
            dict: IR categories, files, and timing
            
        Live API:
            HybridReverbDevice.ir_category_list/index
            HybridReverbDevice.ir_file_list/index
            HybridReverbDevice.ir_attack_time/decay_time/size_factor
        """
        try:
            device = self._find_device_by_class(track_index, 'HybridReverb', device_index)
            
            result = {
                "status": "success",
                "track_index": track_index,
                "device_name": device.name,
            }
            
            if hasattr(device, 'ir_category_list'):
                result["categories"] = list(device.ir_category_list)
            if hasattr(device, 'ir_category_index'):
                result["category_index"] = device.ir_category_index
            if hasattr(device, 'ir_file_list'):
                result["files"] = list(device.ir_file_list)
            if hasattr(device, 'ir_file_index'):
                result["file_index"] = device.ir_file_index
            if hasattr(device, 'ir_attack_time'):
                result["attack_time"] = device.ir_attack_time
            if hasattr(device, 'ir_decay_time'):
                result["decay_time"] = device.ir_decay_time
            if hasattr(device, 'ir_size_factor'):
                result["size_factor"] = device.ir_size_factor
            if hasattr(device, 'ir_time_shaping_on'):
                result["time_shaping_on"] = device.ir_time_shaping_on
            
            return result
            
        except Exception as e:
            self._log("Error getting Hybrid Reverb IR: " + str(e))
            raise
    
    # =========================================================================
    # Device Active Toggle (common to all specialized devices)
    # =========================================================================
    
    def toggle_device_active(self, track_index, device_index=0):
        """
        Toggle a device's active state (on/off).
        
        Note: is_active is read-only for most devices - this finds
        the "Device On" parameter instead.
        
        Args:
            track_index (int): Track index
            device_index (int): Device index
            
        Returns:
            dict: New active state
            
        Live API:
            Device.parameters["Device On"]
        """
        try:
            tracks = self.song.tracks
            if track_index < 0 or track_index >= len(tracks):
                raise IndexError("Track index out of range")
            
            track = tracks[track_index]
            if device_index < 0 or device_index >= len(track.devices):
                raise IndexError("Device index out of range")
            
            device = track.devices[device_index]
            
            # Find "Device On" parameter
            for param in device.parameters:
                if param.name == "Device On":
                    new_value = 0.0 if param.value > 0.5 else 1.0
                    param.value = new_value
                    return {
                        "status": "success",
                        "device_name": device.name,
                        "is_on": new_value > 0.5
                    }
            
            return {"status": "error", "message": "Device On parameter not found"}
            
        except Exception as e:
            self._log("Error toggling device: " + str(e))
            raise

