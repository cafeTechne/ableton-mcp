"""
Sample Handler Module for AbletonMCP Remote Script.

This module handles operations on audio samples within clips or Simpler devices,
including slicing, warping, and gain management.

Live 11 API Reference:
    - Live.Sample.Sample
    - Live.Clip.Clip (audio_clip.sample)
    - Live.SimplerDevice.SimplerDevice (sample)
"""
from __future__ import absolute_import, print_function, unicode_literals
from .base import HandlerBase

class SampleHandler(HandlerBase):
    """
    Handler for sample operations in AbletonMCP.
    Provides access to detailed sample properties like slices, markers, and warping details.
    """

    def __init__(self, mcp_instance):
        self.mcp = mcp_instance

    def _get_sample(self, track_index, clip_index=None, device_index=None):
        """
        Resolve a sample from a Clip or a Simpler device.
        
        Args:
            track_index (int): Track index
            clip_index (int, optional): Clip slot index (for audio clips)
            device_index (int, optional): Device index (for Simpler/Sampler)
            
        Returns:
            Live.Sample.Sample: The sample object
        """
        try:
            if track_index < 0 or track_index >= len(self.song.tracks):
                raise IndexError("Track index {} out of range".format(track_index))
            track = self.song.tracks[track_index]

            # Case A: Audio Clip
            if clip_index is not None:
                if clip_index < 0: # Arrangement clip? Not supported easily by index. Assuming session.
                     raise ValueError("Arrangement clip sample access not yet implemented by index")
                
                # Check clip slots (Session View)
                if clip_index >= len(track.clip_slots):
                    raise IndexError("Clip slot index {} out of range".format(clip_index))
                slot = track.clip_slots[clip_index]
                if not slot.has_clip:
                    raise ValueError("No clip in slot {}".format(clip_index))
                clip = slot.clip
                if not clip.is_audio_clip:
                    raise ValueError("Clip is not an audio clip")
                return clip.sample

            # Case B: Simpler/Sampler Device
            if device_index is not None:
                if device_index >= len(track.devices):
                    raise IndexError("Device index {} out of range".format(device_index))
                device = track.devices[device_index]
                if hasattr(device, 'sample'):
                    return device.sample
                # Some devices might have 'sample' on a child parameter or chain?
                # Primarily Simpler has 'sample'. Sampler has multiple, more complex.
                raise ValueError("Device '{}' does not expose a single 'sample' property directly".format(device.name))

            raise ValueError("Must provide either clip_index or device_index")
        except Exception as e:
            self._log("Error resolving sample: " + str(e))
            raise

    def get_sample_details(self, track_index, clip_index=None, device_index=None):
        """
        Get detailed information about a sample.
        """
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if not sample:
                return {"status": "empty", "message": "No sample loaded"}

            return {
                "file_path": getattr(sample, "file_path", ""),
                "length": getattr(sample, "length", 0),
                "sample_rate": getattr(sample, "sample_rate", 44100),
                "gain": getattr(sample, "gain", 1.0),
                "warping": getattr(sample, "warping", False),
                "warp_mode": getattr(sample, "warp_mode", 0),
                # Granular details could be added here
                "slicing_style": getattr(sample, "slicing_style", 0) if hasattr(sample, "slicing_style") else None
            }
        except Exception as e:
            self._log("Error getting sample details: " + str(e))
            raise

    # =========================================================================
    # Slicing & Markers
    # =========================================================================

    def get_slices(self, track_index, clip_index=None, device_index=None):
        """Get list of slice points (time in samples)."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if not sample: return []
            # 'slices' is a tuple of float/int sample times
            return {"slices": list(getattr(sample, "slices", []))}
        except Exception as e:
            self._log("Error getting slices: " + str(e))
            raise

    def insert_slice(self, track_index, slice_time, clip_index=None, device_index=None):
        """Insert a slice marker at the given sample time."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if hasattr(sample, "insert_slice"):
                sample.insert_slice(int(slice_time))
                return {"status": "success", "action": "insert", "time": slice_time}
            return {"status": "ignored", "message": "Sample does not support insert_slice"}
        except Exception as e:
            self._log("Error inserting slice: " + str(e))
            raise

    def remove_slice(self, track_index, slice_time, clip_index=None, device_index=None):
        """Remove a slice marker at the given sample time."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if hasattr(sample, "remove_slice"):
                sample.remove_slice(int(slice_time))
                return {"status": "success", "action": "remove", "time": slice_time}
            return {"status": "ignored", "message": "Sample does not support remove_slice"}
        except Exception as e:
            self._log("Error removing slice: " + str(e))
            raise

    def clear_slices(self, track_index, clip_index=None, device_index=None):
        """Clear all manual slices."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if hasattr(sample, "clear_slices"):
                sample.clear_slices()
                return {"status": "success", "action": "clear_all"}
            return {"status": "ignored", "message": "Sample does not support clear_slices"}
        except Exception as e:
            self._log("Error clearing slices: " + str(e))
            raise

    def set_sample_gain(self, track_index, gain, clip_index=None, device_index=None):
        """Set the gain of the sample (0.0 to 1.0)."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if sample:
                sample.gain = float(gain)
                return {"status": "success", "gain": sample.gain}
            return {"status": "error", "message": "No sample"}
        except Exception as e:
            self._log("Error setting sample gain: " + str(e))
            raise

    def reset_slices(self, track_index, clip_index=None, device_index=None):
        """Resets all edited slices to their original positions."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if hasattr(sample, "reset_slices"):
                sample.reset_slices()
                return {"status": "success", "action": "reset_slices"}
            return {"status": "ignored", "message": "Sample does not support reset_slices"}
        except Exception as e:
            self._log("Error resetting slices: " + str(e))
            raise

    def get_gain_display_string(self, track_index, clip_index=None, device_index=None):
        """Get the gain's display value as a string."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if hasattr(sample, "gain_display_string"):
                return {"display_value": sample.gain_display_string()}
            return {"display_value": str(getattr(sample, "gain", 1.0))}
        except Exception as e:
            self._log("Error getting gain display string: " + str(e))
            raise

    def beat_to_sample_time(self, track_index, beat_time, clip_index=None, device_index=None):
        """Converts the given beat time to sample time (requires warping)."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if hasattr(sample, "beat_to_sample_time"):
                st = sample.beat_to_sample_time(float(beat_time))
                return {"beat_time": beat_time, "sample_time": st}
            return {"status": "error", "message": "Method not supported (sample likely not warped)"}
        except Exception as e:
            self._log("Error converting beat to sample time: " + str(e))
            raise

    def sample_to_beat_time(self, track_index, sample_time, clip_index=None, device_index=None):
        """Converts the given sample time to beat time (requires warping)."""
        try:
            sample = self._get_sample(track_index, clip_index, device_index)
            if hasattr(sample, "sample_to_beat_time"):
                bt = sample.sample_to_beat_time(float(sample_time))
                return {"sample_time": sample_time, "beat_time": bt}
            return {"status": "error", "message": "Method not supported (sample likely not warped)"}
        except Exception as e:
            self._log("Error converting sample to beat time: " + str(e))
            raise

