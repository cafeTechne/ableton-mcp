"""
Command Interface Module for AbletonMCP Remote Script.

This module contains the CommandDispatcher class which routes incoming commands
from the MCP Server to the appropriate handler methods.

Architecture:
    MCP Server -> Socket -> CommandDispatcher.dispatch() -> Handler.method()

For Future Agents:
    - Commands arrive as dicts with "type" and "params" keys
    - The dispatcher maps command type strings to handler lambdas
    - All handlers are accessed via self.handler (the main AbletonMCP instance)
    - Handler instances: track_handler, session_handler, device_handler,
      drum_rack_handler, groove_handler, simpler_handler, arrangement_handler
    - Add new commands by extending the main_thread_commands dict

Command Flow Example:
    >>> command = {"type": "create_midi_track", "params": {"index": 0}}
    >>> response = dispatcher.dispatch(command)
    >>> # Returns: {"status": "success", "result": {...}}

Error Handling:
    - Exceptions are caught and returned as {"status": "error", "error": str}
    - Tracebacks are logged to Ableton's log file
"""
from __future__ import absolute_import, print_function, unicode_literals
import traceback
import json

# Change queue import for Python 2
try:
    import Queue as queue  # Python 2
except ImportError:
    import queue  # Python 3


class CommandDispatcher(object):
    """
    Routes incoming commands to appropriate handler methods.
    
    The dispatcher maintains a mapping of command type strings to handler
    method calls. Each command is processed synchronously on Live's main
    thread via the socket callback mechanism.
    
    Attributes:
        handler: Reference to the main AbletonMCP ControlSurface instance,
                 which provides access to all handler objects
    
    Handler Access Patterns:
        - self.handler.track_handler -> TrackHandler (core track ops)
        - self.handler.session_handler -> SessionHandler (transport, scenes)
        - self.handler.device_handler -> DeviceHandler (browser, parameters)
        - self.handler.drum_rack_handler -> DrumRackHandler (drum pads)
        - self.handler.groove_handler -> GrooveHandler (groove pool)
        - self.handler.simpler_handler -> SimplerHandler (sample ops)
        - self.handler.arrangement_handler -> ArrangementHandler (timeline)
    """
    def __init__(self, handler):
        self.handler = handler

    def dispatch(self, command):
        """Process a command and return a response"""
        command_type = command.get("type", "")
        params = command.get("params", {})
        
        response = {
            "status": "success",
            "result": {}
        }

        try:
            # Map command types to method names on the handler
            # This allows us to decouple the command name from the method name if needed
            # For now, we manually map to existing methods
            
            # Commands that modify Live's state (require main thread)
            main_thread_commands = {
                "create_midi_track": lambda: self.handler.track_handler.create_midi_track(params.get("index", -1)),
                "create_audio_track": lambda: self.handler.track_handler.create_audio_track(params.get("index", -1)),
                "delete_track": lambda: self.handler.track_handler.delete_track(params.get("track_index", -1)),
                "duplicate_track": lambda: self.handler.track_handler.duplicate_track(params.get("track_index", -1), params.get("target_index", None)),
                "set_track_name": lambda: self.handler.track_handler.set_track_name(params.get("track_index", 0), params.get("name", "")),
                "configure_track_routing": lambda: self.handler.track_handler.configure_track_routing(
                    params.get("track_index", 0),
                    params.get("input_type", None),
                    params.get("input_channel", None),
                    params.get("output_type", None),
                    params.get("output_channel", None),
                    params.get("monitor_state", None),
                    params.get("arm", None),
                    params.get("sends", None)
                ),
                "set_track_io": lambda: self.handler.track_handler.set_track_io(
                    params.get("track_index", 0),
                    params.get("input_type", None),
                    params.get("input_channel", None),
                    params.get("output_type", None),
                    params.get("output_channel", None)
                ),
                "set_track_monitor": lambda: self.handler.track_handler.set_track_monitor(params.get("track_index", 0), params.get("state", "auto")),
                "set_track_arm": lambda: self.handler.track_handler.set_track_bool(params.get("track_index", 0), "arm", params.get("arm", True)),
                "set_track_solo": lambda: self.handler.track_handler.set_track_bool(params.get("track_index", 0), "solo", params.get("solo", True)),
                "set_track_mute": lambda: self.handler.track_handler.set_track_bool(params.get("track_index", 0), "mute", params.get("mute", True)),
                "set_track_volume": lambda: self.handler.track_handler.set_track_volume(params.get("track_index", 0), params.get("volume", 0.0)),
                "set_track_panning": lambda: self.handler.track_handler.set_track_panning(params.get("track_index", 0), params.get("panning", 0.0)),
                "set_send_level": lambda: self.handler.track_handler.set_send_level(params.get("track_index", 0), params.get("send_index", 0), params.get("level", 0.0)),
                "create_return_track": lambda: self.handler.track_handler.create_return_track(params.get("name", None)),
                "delete_return_track": lambda: self.handler.track_handler.delete_return_track(params.get("index", -1)),
                "set_return_track_name": lambda: self.handler.track_handler.set_return_track_name(params.get("index", 0), params.get("name", "")),
                "get_routing_options": lambda: self.handler.track_handler.get_routing_options(params.get("track_index", 0)),
                "set_track_output": lambda: self.handler.track_handler.set_track_output(
                    params.get("track_index", 0),
                    params.get("output_name", "Master")
                ),
                "create_clip": lambda: self.handler.track_handler.create_clip(params.get("track_index", 0), params.get("clip_index", 0), params.get("length", 4.0)),
                "delete_clip": lambda: self.handler.track_handler.delete_clip(params.get("track_index", 0), params.get("clip_index", 0)),
                "duplicate_clip": lambda: self.handler.track_handler.duplicate_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("target_track_index", None),
                    params.get("target_clip_index", None)
                ),
                "add_notes_to_clip": lambda: self.handler.track_handler.add_notes_to_clip(params.get("track_index", 0), params.get("clip_index", 0), params.get("notes", [])),
                "set_clip_name": lambda: self.handler.track_handler.set_clip_name(params.get("track_index", 0), params.get("clip_index", 0), params.get("name", "Clip")),
                "set_clip_loop": lambda: self.handler.track_handler.set_clip_loop(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("start", None),
                    params.get("end", None),
                    params.get("loop_on", True)
                ),
                "set_clip_length": lambda: self.handler.track_handler.set_clip_length(params.get("track_index", 0), params.get("clip_index", 0), params.get("length", 4.0)),
                "quantize_clip": lambda: self.handler.track_handler.quantize_clip(params.get("track_index", 0), params.get("clip_index", 0), params.get("grid", 0.25), params.get("amount", 1.0)),
                "transpose_clip": lambda: self.handler.track_handler.transpose_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("semitones", 0)
                ),
                "apply_legato": lambda: self.handler.track_handler.apply_legato(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("preserve_gaps_below", 0.0)
                ),
                "set_tempo": lambda: self.handler.session_handler.set_tempo(params.get("tempo", 120.0)),
                "set_time_signature": lambda: self.handler.session_handler.set_time_signature(params.get("numerator", 4), params.get("denominator", 4)),
                "fire_clip": lambda: self.handler.track_handler.fire_clip(params.get("track_index", 0), params.get("clip_index", 0)),
                "list_clips": lambda: self.handler.track_handler.list_clips(
                    params.get("track_pattern", None),
                    params.get("match_mode", "contains")
                ),
                "fire_clip_by_name": lambda: self.handler.track_handler.fire_clip_by_name(
                    params.get("clip_pattern", ""),
                    params.get("track_pattern", None),
                    params.get("match_mode", "contains"),
                    params.get("first_only", True)
                ),
                "trigger_test_midi": lambda: self.handler._trigger_test_midi(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("length", 1.0),
                    params.get("pitch", 60),
                    params.get("velocity", 100),
                    params.get("duration", 0.5),
                    params.get("start_time", 0.0),
                    params.get("overwrite_clip", False),
                    params.get("fire_clip", True),
                    params.get("cc_number", None),
                    params.get("cc_value", 64),
                    params.get("channel", 0)
                ),
                "stop_clip": lambda: self.handler.track_handler.stop_clip(params.get("track_index", 0), params.get("clip_index", 0)),
                "start_playback": lambda: self.handler.session_handler.start_playback(),
                "stop_playback": lambda: self.handler.session_handler.stop_playback(),
                "set_record_mode": lambda: self.handler.session_handler.set_record_mode(params.get("enabled", False)),
                "trigger_session_record": lambda: self.handler.session_handler.trigger_session_record(params.get("record_length", 0)),
                "capture_midi": lambda: self.handler.session_handler.capture_midi(params.get("destination", 0)),
                "set_overdub": lambda: self.handler.session_handler.set_overdub(params.get("enabled", False)),
                "create_scene": lambda: self.handler.session_handler.create_scene(params.get("index", -1), params.get("name", None)),
                "delete_scene": lambda: self.handler.session_handler.delete_scene(params.get("index", -1)),
                "duplicate_scene": lambda: self.handler.session_handler.duplicate_scene(params.get("index", -1)),
                "fire_scene": lambda: self.handler.session_handler.fire_scene(params.get("index", -1)),
                "fire_scene_by_name": lambda: self.handler.session_handler.fire_scene_by_name(
                    params.get("pattern", ""),
                    params.get("match_mode", "contains"),
                    params.get("first_only", True)
                ),
                "stop_scene": lambda: self.handler.session_handler.stop_scene(params.get("index", -1)),
                "get_song_context": lambda: self.handler.session_handler.get_song_context(params.get("include_clips", False)),
                "load_browser_item": lambda: self.handler.device_handler.load_browser_item(
                    params.get("track_index", 0),
                    params.get("item_uri", ""),
                    params.get("clip_index", None)
                ),
                "load_device": lambda: self.handler.device_handler.load_device(params.get("track_index", 0), params.get("device_uri", ""), params.get("device_slot", -1)),
                "hotswap_browser_item": lambda: self.handler.device_handler.hotswap_browser_item(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("item_uri", "")
                ),
                "set_device_parameter": lambda: self.handler.device_handler.set_device_parameter(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("parameter", 0),
                    params.get("value", 0.0)
                ),
                # Conversion Commands
                "create_drum_rack_from_slices": lambda: self.handler.conversion_handler.create_drum_rack_from_slices(
                    params.get("track_index", 0), 
                    params.get("device_index", None)
                ),
                "create_drum_rack_from_audio_clip": lambda: self.handler.conversion_handler.create_drum_rack_from_audio_clip(
                    params.get("track_index", 0), 
                    params.get("clip_index", 0)
                ),
                "move_devices_to_drum_rack": lambda: self.handler.conversion_handler.move_devices_to_drum_rack(
                    params.get("track_index", 0)
                ),
                "audio_to_drums": lambda: self.handler.conversion_handler.audio_to_drums(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "audio_to_harmony": lambda: self.handler.conversion_handler.audio_to_harmony(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "audio_to_melody": lambda: self.handler.conversion_handler.audio_to_melody(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                # Macro Commands
                "get_rack_macros": lambda: self.handler.device_handler.get_rack_macros(
                    params.get("track_index", 0),
                    params.get("device_index", 0)
                ),
                "add_macro": lambda: self.handler.device_handler.add_macro(
                    params.get("track_index", 0),
                    params.get("device_index", 0)
                ),
                "remove_macro": lambda: self.handler.device_handler.remove_macro(
                    params.get("track_index", 0),
                    params.get("device_index", 0)
                ),
                "randomize_macros": lambda: self.handler.device_handler.randomize_macros(
                    params.get("track_index", 0),
                    params.get("device_index", 0)
                ),
                "get_rack_chains": lambda: self.handler.device_handler.get_rack_chains(
                    params.get("track_index", 0),
                    params.get("device_index", 0)
                ),
                "set_device_parameters": lambda: self.handler.device_handler.set_device_parameters(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("parameters", None)
                ),
                "set_device_audio_input": lambda: self.handler._set_device_audio_input(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("input_type", None),
                    params.get("input_channel", None)
                ),
                "get_device_parameters": lambda: self.handler.device_handler.get_device_parameters(params.get("track_index", 0), params.get("device_index", 0)),
                "set_device_sidechain_source": lambda: self.handler.device_handler.set_device_sidechain_source(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("source_track_index", 0),
                    params.get("pre_fx", True),
                    params.get("mono", True)
                ),
                "list_routable_devices": lambda: self.handler.device_handler.list_routable_devices(),
                "save_device_snapshot": lambda: self.handler.device_handler.save_device_snapshot(params.get("track_index", 0), params.get("device_index", 0)),
                "save_device_preset": lambda: self.handler.device_handler.save_device_snapshot(params.get("track_index", 0), params.get("device_index", 0)),
                "apply_device_snapshot": lambda: self.handler.device_handler.apply_device_snapshot(
                    params.get("track_index", 0),
                    params.get("device_index", 0),
                    params.get("snapshot", {})
                ),
                "add_basic_drum_pattern": lambda: self.handler.track_handler.add_basic_drum_pattern(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "add_chord_stack": lambda: self.handler._add_chord_stack(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("root_midi", 60),
                    params.get("quality", "major"),
                    params.get("bars", 4),
                    params.get("chord_length", 1.0)
                ),
                "set_clip_envelope": lambda: self.handler.track_handler.set_clip_envelope(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("device_index", 0),
                    params.get("parameter_name", "Frequency"),
                    params.get("points", [])
                ),
                "list_loadable_devices": lambda: self.handler.device_handler.list_loadable_devices(params.get("category", "all"), params.get("max_items", 200)),
                "search_loadable_devices": lambda: self.handler.device_handler.search_loadable_devices(
                    params.get("query", ""),
                    params.get("category", "all"),
                    params.get("max_items", 200)
                ),
                "get_clip_notes": lambda: self.handler.track_handler.get_clip_notes(params.get("track_index", 0), params.get("clip_index", 0)),
                "search_and_load_device": lambda: self.handler.device_handler.search_and_load_device(
                    params.get("track_index", 0),
                    params.get("query", ""),
                    params.get("category", "all")
                ),
                # Drum Rack Management (uses modular DrumRackHandler)
                "get_drum_rack_info": lambda: self.handler.drum_rack_handler.get_drum_rack_info(
                    params.get("track_index", 0),
                    params.get("device_index", None),
                    params.get("include_empty", False)
                ),
                "copy_drum_pad": lambda: self.handler.drum_rack_handler.copy_drum_pad(
                    params.get("track_index", 0),
                    params.get("source_note", 36),
                    params.get("dest_note", 37),
                    params.get("device_index", None)
                ),
                "set_drum_pad_choke_group": lambda: self.handler.drum_rack_handler.set_drum_pad_choke_group(
                    params.get("track_index", 0),
                    params.get("note", 36),
                    params.get("choke_group", 0),
                    params.get("device_index", None)
                ),
                "mute_drum_pad": lambda: self.handler.drum_rack_handler.mute_drum_pad(
                    params.get("track_index", 0),
                    params.get("note", 36),
                    params.get("mute", True),
                    params.get("device_index", None)
                ),
                "solo_drum_pad": lambda: self.handler.drum_rack_handler.solo_drum_pad(
                    params.get("track_index", 0),
                    params.get("note", 36),
                    params.get("solo", True),
                    params.get("device_index", None)
                ),
                # Groove Pool Management (uses modular GrooveHandler)
                "get_groove_pool": lambda: self.handler.groove_handler.get_groove_pool(),
                "set_clip_groove": lambda: self.handler.groove_handler.set_clip_groove(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("groove_index", None)
                ),
                "commit_groove": lambda: self.handler.groove_handler.commit_groove(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                # Simpler/Sampler Control (uses modular SimplerHandler)
                "get_simpler_info": lambda: self.handler.simpler_handler.get_simpler_info(
                    params.get("track_index", 0),
                    params.get("device_index", None)
                ),
                "reverse_simpler_sample": lambda: self.handler.simpler_handler.reverse_simpler_sample(
                    params.get("track_index", 0),
                    params.get("device_index", None)
                ),
                "crop_simpler_sample": lambda: self.handler.simpler_handler.crop_simpler_sample(
                    params.get("track_index", 0),
                    params.get("device_index", None)
                ),
                "set_simpler_playback_mode": lambda: self.handler.simpler_handler.set_simpler_playback_mode(
                    params.get("track_index", 0),
                    params.get("mode", "classic"),
                    params.get("device_index", None)
                ),
                "set_simpler_sample_markers": lambda: self.handler.simpler_handler.set_simpler_sample_markers(
                    params.get("track_index", 0),
                    params.get("start", None),
                    params.get("end", None),
                    params.get("device_index", None)
                ),
                "warp_simpler_sample": lambda: self.handler.simpler_handler.warp_simpler_sample(
                    params.get("track_index", 0),
                    params.get("warp_mode", None),
                    params.get("enable", None),
                    params.get("device_index", None)
                ),
                # Arrangement View (uses modular ArrangementHandler)
                "get_arrangement_info": lambda: self.handler.arrangement_handler.get_arrangement_info(),
                "create_cue_point": lambda: self.handler.arrangement_handler.create_cue_point(
                    params.get("time", 0.0),
                    params.get("name", None)
                ),
                "delete_cue_point": lambda: self.handler.arrangement_handler.delete_cue_point(
                    params.get("index", 0)
                ),
                "jump_to_cue_point": lambda: self.handler.arrangement_handler.jump_to_cue_point(
                    params.get("index", 0)
                ),
                "set_arrangement_loop": lambda: self.handler.arrangement_handler.set_arrangement_loop(
                    params.get("start", 0.0),
                    params.get("length", 4.0),
                    params.get("enable", True)
                ),
                "set_song_time": lambda: self.handler.arrangement_handler.set_song_time(
                    params.get("time", 0.0)
                ),
                "scrub_arrangement": lambda: self.handler.arrangement_handler.scrub_arrangement(
                    params.get("time", 0.0)
                ),
                # Song Operations (uses modular SongHandler)
                "capture_midi": lambda: self.handler.song_handler.capture_midi(
                    params.get("destination", 0)
                ),
                "set_record_mode": lambda: self.handler.song_handler.set_record_mode(
                    params.get("enabled", False)
                ),
                "get_record_mode": lambda: self.handler.song_handler.get_record_mode(),
                "set_session_record": lambda: self.handler.song_handler.set_session_record(
                    params.get("enabled", False)
                ),
                "trigger_session_record": lambda: self.handler.song_handler.trigger_session_record(
                    params.get("record_length", None)
                ),
                "set_overdub": lambda: self.handler.song_handler.set_overdub(
                    params.get("enabled", False)
                ),
                "set_punch_in": lambda: self.handler.song_handler.set_punch_in(
                    params.get("enabled", False)
                ),
                "set_punch_out": lambda: self.handler.song_handler.set_punch_out(
                    params.get("enabled", False)
                ),
                "undo": lambda: self.handler.song_handler.undo(),
                "redo": lambda: self.handler.song_handler.redo(),
                "get_undo_state": lambda: self.handler.song_handler.get_undo_state(),
                "set_metronome": lambda: self.handler.song_handler.set_metronome(
                    params.get("enabled", True)
                ),
                "get_metronome": lambda: self.handler.song_handler.get_metronome(),
                "tap_tempo": lambda: self.handler.song_handler.tap_tempo(),
                "nudge_tempo": lambda: self.handler.song_handler.nudge_tempo(
                    params.get("direction", "up"),
                    params.get("active", True)
                ),
                "set_swing_amount": lambda: self.handler.song_handler.set_swing_amount(
                    params.get("amount", 0.0)
                ),
                "continue_playing": lambda: self.handler.song_handler.continue_playing(),
                "play_selection": lambda: self.handler.song_handler.play_selection(),
                "stop_all_clips": lambda: self.handler.song_handler.stop_all_clips(
                    params.get("quantized", True)
                ),
                "jump_by": lambda: self.handler.song_handler.jump_by(
                    params.get("beats", 0.0)
                ),
                "jump_to_next_cue": lambda: self.handler.song_handler.jump_to_next_cue(),
                "jump_to_prev_cue": lambda: self.handler.song_handler.jump_to_prev_cue(),
                "set_or_delete_cue": lambda: self.handler.song_handler.set_or_delete_cue(),
                "set_loop": lambda: self.handler.song_handler.set_loop(
                    params.get("enabled", None),
                    params.get("start", None),
                    params.get("length", None)
                ),
                "get_loop": lambda: self.handler.song_handler.get_loop(),
                "set_clip_trigger_quantization": lambda: self.handler.song_handler.set_clip_trigger_quantization(
                    params.get("quantization", 4)
                ),
                "set_midi_recording_quantization": lambda: self.handler.song_handler.set_midi_recording_quantization(
                    params.get("quantization", 0)
                ),
                "create_return_track": lambda: self.handler.song_handler.create_return_track(),
                "delete_return_track": lambda: self.handler.song_handler.delete_return_track(
                    params.get("index", 0)
                ),
                "get_return_tracks": lambda: self.handler.song_handler.get_return_tracks(),
                "get_song_state": lambda: self.handler.song_handler.get_song_state(),
                # Clip Slot Operations (uses modular ClipSlotHandler)
                "get_slot_info": lambda: self.handler.clip_slot_handler.get_slot_info(
                    params.get("track_index", 0),
                    params.get("slot_index", 0)
                ),
                "fire_slot": lambda: self.handler.clip_slot_handler.fire_slot(
                    params.get("track_index", 0),
                    params.get("slot_index", 0),
                    params.get("record_length", None),
                    params.get("launch_quantization", None),
                    params.get("force_legato", False)
                ),
                "stop_slot": lambda: self.handler.clip_slot_handler.stop_slot(
                    params.get("track_index", 0),
                    params.get("slot_index", 0)
                ),
                "create_clip_in_slot": lambda: self.handler.clip_slot_handler.create_clip(
                    params.get("track_index", 0),
                    params.get("slot_index", 0),
                    params.get("length", 4.0)
                ),
                "delete_clip_in_slot": lambda: self.handler.clip_slot_handler.delete_clip(
                    params.get("track_index", 0),
                    params.get("slot_index", 0)
                ),
                "duplicate_clip_to_slot": lambda: self.handler.clip_slot_handler.duplicate_clip_to(
                    params.get("src_track", 0),
                    params.get("src_slot", 0),
                    params.get("dest_track", 0),
                    params.get("dest_slot", 0)
                ),
                "set_slot_stop_button": lambda: self.handler.clip_slot_handler.set_stop_button(
                    params.get("track_index", 0),
                    params.get("slot_index", 0),
                    params.get("has_stop_button", True)
                ),
                "get_track_slots": lambda: self.handler.clip_slot_handler.get_track_slots(
                    params.get("track_index", 0)
                ),
                "fire_scene": lambda: self.handler.clip_slot_handler.fire_scene_slots(
                    params.get("scene_index", 0)
                ),
                # Mixer Operations (uses modular MixerHandler)
                "get_master_info": lambda: self.handler.mixer_handler.get_master_info(),
                "set_master_volume": lambda: self.handler.mixer_handler.set_master_volume(
                    params.get("value", 0.85)
                ),
                "set_master_pan": lambda: self.handler.mixer_handler.set_master_pan(
                    params.get("value", 0.0)
                ),
                "get_cue_volume": lambda: self.handler.mixer_handler.get_cue_volume(),
                "set_cue_volume": lambda: self.handler.mixer_handler.set_cue_volume(
                    params.get("value", 0.85)
                ),
                "get_crossfader": lambda: self.handler.mixer_handler.get_crossfader(),
                "set_crossfader": lambda: self.handler.mixer_handler.set_crossfader(
                    params.get("value", 0.0)
                ),
                "set_track_crossfade_assign": lambda: self.handler.mixer_handler.set_track_crossfade_assign(
                    params.get("track_index", 0),
                    params.get("assign", 0)
                ),
                "get_track_sends": lambda: self.handler.mixer_handler.get_track_sends(
                    params.get("track_index", 0)
                ),
                "set_track_send": lambda: self.handler.mixer_handler.set_track_send(
                    params.get("track_index", 0),
                    params.get("send_index", 0),
                    params.get("value", 0.0)
                ),
                "set_return_volume": lambda: self.handler.mixer_handler.set_return_volume(
                    params.get("return_index", 0),
                    params.get("value", 0.85)
                ),
                "set_return_pan": lambda: self.handler.mixer_handler.set_return_pan(
                    params.get("return_index", 0),
                    params.get("value", 0.0)
                ),
                "mute_return": lambda: self.handler.mixer_handler.mute_return(
                    params.get("return_index", 0),
                    params.get("muted", True)
                ),
                "solo_return": lambda: self.handler.mixer_handler.solo_return(
                    params.get("return_index", 0),
                    params.get("soloed", True)
                ),
                "get_mixer_overview": lambda: self.handler.mixer_handler.get_mixer_overview(),
                # Scene Operations (uses modular SceneHandler)
                "get_scene_info": lambda: self.handler.scene_handler.get_scene_info(
                    params.get("scene_index", 0)
                ),
                "get_all_scenes": lambda: self.handler.scene_handler.get_all_scenes(),
                "set_scene_name": lambda: self.handler.scene_handler.set_scene_name(
                    params.get("scene_index", 0),
                    params.get("name", "")
                ),
                "set_scene_color": lambda: self.handler.scene_handler.set_scene_color(
                    params.get("scene_index", 0),
                    params.get("color", 0)
                ),
                "set_scene_color_index": lambda: self.handler.scene_handler.set_scene_color_index(
                    params.get("scene_index", 0),
                    params.get("color_index", 0)
                ),
                "set_scene_tempo": lambda: self.handler.scene_handler.set_scene_tempo(
                    params.get("scene_index", 0),
                    params.get("tempo", 0)
                ),
                "set_scene_time_signature": lambda: self.handler.scene_handler.set_scene_time_signature(
                    params.get("scene_index", 0),
                    params.get("numerator", 4),
                    params.get("denominator", 4)
                ),
                "fire_scene_by_index": lambda: self.handler.scene_handler.fire_scene(
                    params.get("scene_index", 0),
                    params.get("force_legato", False)
                ),
                "select_scene": lambda: self.handler.scene_handler.select_scene(
                    params.get("scene_index", 0)
                ),
                "create_scene": lambda: self.handler.scene_handler.create_scene(
                    params.get("index", -1)
                ),
                "delete_scene": lambda: self.handler.scene_handler.delete_scene(
                    params.get("scene_index", 0)
                ),
                "duplicate_scene": lambda: self.handler.scene_handler.duplicate_scene(
                    params.get("scene_index", 0)
                ),
                "move_scene": lambda: self.handler.scene_handler.move_scene(
                    params.get("scene_index", 0),
                    params.get("target_index", 0)
                ),
                "get_scene_overview": lambda: self.handler.scene_handler.get_scene_overview(),
                # Application Operations (uses modular ApplicationHandler)
                "get_live_version": lambda: self.handler.application_handler.get_live_version(),
                "get_available_views": lambda: self.handler.application_handler.get_available_views(),
                "focus_view": lambda: self.handler.application_handler.focus_view(
                    params.get("view_name", "Session")
                ),
                "show_view": lambda: self.handler.application_handler.show_view(
                    params.get("view_name", "Session")
                ),
                "hide_view": lambda: self.handler.application_handler.hide_view(
                    params.get("view_name", "Browser")
                ),
                "is_view_visible": lambda: self.handler.application_handler.is_view_visible(
                    params.get("view_name", "Session"),
                    params.get("main_window_only", True)
                ),
                "get_focused_document_view": lambda: self.handler.application_handler.get_focused_document_view(),
                "scroll_view": lambda: self.handler.application_handler.scroll_view(
                    params.get("direction", 0),
                    params.get("view_name", "Session"),
                    params.get("animate", True)
                ),
                "zoom_view": lambda: self.handler.application_handler.zoom_view(
                    params.get("direction", 1),
                    params.get("view_name", "Session"),
                    params.get("animate", True)
                ),
                "toggle_browser": lambda: self.handler.application_handler.toggle_browser(),
                "get_browse_mode": lambda: self.handler.application_handler.get_browse_mode(),
                "get_dialog_state": lambda: self.handler.application_handler.get_dialog_state(),
                "press_dialog_button": lambda: self.handler.application_handler.press_dialog_button(
                    params.get("button_index", 0)
                ),
                "get_application_overview": lambda: self.handler.application_handler.get_application_overview(),
                # Clip Operations (uses modular ClipHandler)
                "fire_clip": lambda: self.handler.clip_handler.fire_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("force_legato", False)
                ),
                "stop_clip": lambda: self.handler.clip_handler.stop_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "get_clip_details": lambda: self.handler.clip_handler.get_clip_details(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "set_clip_name": lambda: self.handler.clip_handler.set_clip_name(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("name", "")
                ),
                "set_clip_color": lambda: self.handler.clip_handler.set_clip_color(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("color", None),
                    params.get("color_index", None)
                ),
                "set_clip_loop": lambda: self.handler.clip_handler.set_clip_loop(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("looping", None),
                    params.get("loop_start", None),
                    params.get("loop_end", None)
                ),
                "set_clip_markers": lambda: self.handler.clip_handler.set_clip_markers(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("start_marker", None),
                    params.get("end_marker", None)
                ),
                "duplicate_loop": lambda: self.handler.clip_handler.duplicate_loop(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "set_clip_launch_mode": lambda: self.handler.clip_handler.set_clip_launch_mode(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("mode", 0)
                ),
                "set_clip_launch_quantization": lambda: self.handler.clip_handler.set_clip_launch_quantization(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("quantization", -1)
                ),
                "set_clip_legato": lambda: self.handler.clip_handler.set_clip_legato(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("legato", False)
                ),
                "set_clip_warp": lambda: self.handler.clip_handler.set_clip_warp(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("warping", None),
                    params.get("warp_mode", None)
                ),
                "set_clip_pitch": lambda: self.handler.clip_handler.set_clip_pitch(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("coarse", None),
                    params.get("fine", None)
                ),
                "set_clip_gain": lambda: self.handler.clip_handler.set_clip_gain(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("gain", 0.5)
                ),
                "quantize_clip": lambda: self.handler.clip_handler.quantize_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0),
                    params.get("grid", 5),
                    params.get("amount", 1.0)
                ),
                "crop_clip": lambda: self.handler.clip_handler.crop_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "clear_clip": lambda: self.handler.clip_handler.clear_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "deselect_all_notes": lambda: self.handler.clip_handler.deselect_all_notes(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "select_all_notes": lambda: self.handler.clip_handler.select_all_notes(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                # Track Group Operations (uses modular TrackGroupHandler)
                "get_group_info": lambda: self.handler.track_group_handler.get_group_info(
                    params.get("track_index", 0)
                ),
                "get_all_groups": lambda: self.handler.track_group_handler.get_all_groups(),
                "get_track_group_membership": lambda: self.handler.track_group_handler.get_track_group_membership(
                    params.get("track_index", 0)
                ),
                "fold_group": lambda: self.handler.track_group_handler.fold_group(
                    params.get("track_index", 0)
                ),
                "unfold_group": lambda: self.handler.track_group_handler.unfold_group(
                    params.get("track_index", 0)
                ),
                "toggle_group_fold": lambda: self.handler.track_group_handler.toggle_group_fold(
                    params.get("track_index", 0)
                ),
                "set_track_color": lambda: self.handler.track_group_handler.set_track_color(
                    params.get("track_index", 0),
                    params.get("color", None),
                    params.get("color_index", None)
                ),
                "get_track_freeze_state": lambda: self.handler.track_group_handler.get_track_freeze_state(
                    params.get("track_index", 0)
                ),
                "stop_track_clips": lambda: self.handler.track_group_handler.stop_track_clips(
                    params.get("track_index", 0)
                ),
                "get_tracks_overview": lambda: self.handler.track_group_handler.get_tracks_overview(),
                # Browser Operations (uses modular BrowserHandler)
                "get_browser_tree": lambda: self.handler.browser_handler.get_browser_tree(
                    params.get("max_depth", 2)
                ),
                "get_browser_category": lambda: self.handler.browser_handler.get_browser_category(
                    params.get("category_name", "sounds"),
                    params.get("max_items", 50)
                ),
                "load_item_by_uri": lambda: self.handler.browser_handler.load_item_by_uri(
                    params.get("uri", "")
                ),
                "hotswap_target_enabled": lambda: self.handler.browser_handler.hotswap_target_enabled(),
                "filter_browser": lambda: self.handler.browser_handler.filter_browser(
                    params.get("filter_type", 0)
                ),
                "stop_preview": lambda: self.handler.browser_handler.stop_preview(),
                "get_browser_state": lambda: self.handler.browser_handler.get_browser_state(),
                # Conversion Operations (uses modular ConversionHandler)
                "audio_to_drums": lambda: self.handler.conversion_handler.audio_to_drums(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "audio_to_harmony": lambda: self.handler.conversion_handler.audio_to_harmony(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "audio_to_melody": lambda: self.handler.conversion_handler.audio_to_melody(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "simpler_to_sampler": lambda: self.handler.conversion_handler.simpler_to_sampler(
                    params.get("track_index", 0),
                    params.get("device_index", None)
                ),
                "create_drum_rack_from_slices": lambda: self.handler.conversion_handler.create_drum_rack_from_slices(
                    params.get("track_index", 0),
                    params.get("device_index", None)
                ),
                # =============================================================
                # PHASE 1 COMMANDS
                # =============================================================
                # ChainHandler
                "get_chains": lambda: self.handler.chain_handler.get_chains(params.get("track_index", 0), params.get("device_index", 0)),
                "get_chain": lambda: self.handler.chain_handler.get_chain(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0)),
                "set_chain_name": lambda: self.handler.chain_handler.set_chain_name(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), params.get("name", "")),
                "set_chain_mute": lambda: self.handler.chain_handler.set_chain_bool(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), "mute", params.get("mute", True)),
                "set_chain_solo": lambda: self.handler.chain_handler.set_chain_bool(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), "solo", params.get("solo", True)),
                "set_chain_color": lambda: self.handler.chain_handler.set_chain_color(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), params.get("color", None)),
                "delete_chain_device": lambda: self.handler.chain_handler.delete_chain_device(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), params.get("chain_device_index", 0)),
                "get_chain_mixer": lambda: self.handler.chain_handler.get_chain_mixer(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0)),
                "set_chain_volume": lambda: self.handler.chain_handler.set_chain_mixer_volume(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), params.get("volume", 0.85)),
                "set_chain_pan": lambda: self.handler.chain_handler.set_chain_mixer_pan(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), params.get("pan", 0.0)),
                "set_chain_send": lambda: self.handler.chain_handler.set_chain_mixer_send(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), params.get("send_index", 0), params.get("value", 0.0)),
                "set_drum_chain_choke_group": lambda: self.handler.chain_handler.set_drum_chain_choke_group(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), params.get("group", 0)),
                "set_drum_chain_out_note": lambda: self.handler.chain_handler.set_drum_chain_out_note(params.get("track_index", 0), params.get("device_index", 0), params.get("chain_index", 0), params.get("note", 60)),
                
                # SpecializedDeviceHandler (Extended)
                "get_specialized_device_info": lambda: self.handler.specialized_device_handler.get_specialized_device_info(params.get("track_index", 0), params.get("device_index", 0)),
                "toggle_device_active": lambda: self.handler.specialized_device_handler.toggle_device_active(params.get("track_index", 0), params.get("device_index", 0), params.get("active", True)),
                "get_max_device_banks": lambda: self.handler.specialized_device_handler.get_max_device_banks(params.get("track_index", 0), params.get("device_index", 0)),
                "get_wavetable_oscillator": lambda: self.handler.specialized_device_handler.get_wavetable_oscillator(params.get("track_index", 0), params.get("device_index", 0), params.get("osc_index", 0)),
                "get_wavetable_modulation": lambda: self.handler.specialized_device_handler.get_wavetable_modulation(params.get("track_index", 0), params.get("device_index", 0)),
                "get_hybrid_reverb_ir": lambda: self.handler.specialized_device_handler.get_hybrid_reverb_ir(params.get("track_index", 0), params.get("device_index", 0)),
                
                # =============================================================
                # PHASE 2 COMMANDS
                # =============================================================
                # SongHandler (Additions)
                "scrub_by": lambda: self.handler.song_handler.scrub_by(params.get("beats", 1.0)),
                "set_groove_amount": lambda: self.handler.song_handler.set_groove_amount(params.get("amount", 0.5)),
                "get_groove_amount": lambda: self.handler.song_handler.get_groove_amount(),
                "capture_and_insert_scene": lambda: self.handler.song_handler.capture_and_insert_scene(params.get("scene_index", "selected")),
                "get_cue_points": lambda: self.handler.song_handler.get_cue_points(),
                
                # ClipHandler (Additions)
                "set_clip_audio_properties": lambda: self.handler.clip_handler.set_clip_audio_properties(
                    params.get("track_index", 0), params.get("clip_index", 0),
                    warp_mode=params.get("warp_mode"), warping=params.get("warping"),
                    pitch_coarse=params.get("pitch_coarse"), pitch_fine=params.get("pitch_fine"),
                    gain=params.get("gain")
                ),
                "scrub_clip": lambda: self.handler.clip_handler.scrub_clip(params.get("track_index", 0), params.get("clip_index", 0), params.get("position", 0.0)),
                "stop_scrub": lambda: self.handler.clip_handler.stop_scrub(params.get("track_index", 0), params.get("clip_index", 0)),
                "get_notes": lambda: self.handler.clip_handler.get_notes(
                     params.get("track_index", 0), params.get("clip_index", 0),
                     params.get("start_time", 0), params.get("time_span", 1000)
                ),
                "replace_selected_notes": lambda: self.handler.clip_handler.replace_selected_notes(
                     params.get("track_index", 0), params.get("clip_index", 0),
                     params.get("notes", [])
                ),
                # Note: get_clip_details from Phase 2 already registered? It should be.
                
                # Phase 5: Automation
                "get_clip_envelope": lambda: self.handler.clip_handler.get_clip_envelope(
                    params.get("track_index", 0), params.get("clip_index", 0),
                    params.get("device_id", "mixer"), params.get("parameter_id", 0)
                ),
                "set_clip_envelope_step": lambda: self.handler.clip_handler.set_clip_envelope_step(
                    params.get("track_index", 0), params.get("clip_index", 0),
                    params.get("device_id", "mixer"), params.get("parameter_id", 0),
                    params.get("time", 0.0), params.get("length", 1.0), params.get("value", 0.0)
                ),
                "clear_clip_envelope": lambda: self.handler.clip_handler.clear_clip_envelope(
                    params.get("track_index", 0), params.get("clip_index", 0),
                    params.get("device_id", "mixer"), params.get("parameter_id", 0)
                ),
                
                # Phase 6: Humanization
                "get_notes_extended": lambda: self.handler.clip_handler.get_notes_extended(
                     params.get("track_index", 0), params.get("clip_index", 0),
                     params.get("start_time", 0), params.get("time_span", 1000)
                ),
                "update_notes": lambda: self.handler.clip_handler.update_notes(
                     params.get("track_index", 0), params.get("clip_index", 0),
                     params.get("notes", [])
                ),
                
                "set_notes": lambda: self.handler.clip_handler.set_notes(params.get("track_index", 0), params.get("clip_index", 0), params.get("notes", [])),
                "remove_notes": lambda: self.handler.clip_handler.remove_notes(
                     params.get("track_index", 0), params.get("clip_index", 0),
                     params.get("start_time", 0), params.get("time_span", 1000),
                     params.get("start_pitch", 0), params.get("pitch_span", 128)
                ),
                "replace_selected_notes": lambda: self.handler.clip_handler.replace_selected_notes(params.get("track_index", 0), params.get("clip_index", 0), params.get("notes", [])),
                
                # TrackHandler (Additions)
                "set_track_fold_state": lambda: self.handler.track_handler.set_track_fold_state(params.get("track_index", 0), params.get("folded", True)),
                "get_track_meters": lambda: self.handler.track_handler.get_track_meters(params.get("track_index", 0)),
                "get_arrangement_clips": lambda: self.handler.track_handler.get_arrangement_clips(params.get("track_index", 0)),
                "jump_in_running_session_clip": lambda: self.handler.track_handler.jump_in_running_session_clip(params.get("track_index", 0), params.get("beats", 1.0)),
                "duplicate_clip_to_arrangement": lambda: self.handler.track_handler.duplicate_clip_to_arrangement(
                    params.get("track_index", 0), params.get("clip_index", 0), params.get("arrangement_time", 0.0)
                ),
                
                # DeviceHandler (Additions)
                "begin_parameter_gesture": lambda: self.handler.device_handler.begin_parameter_gesture(params.get("track_index", 0), params.get("device_index", 0), params.get("parameter", 0)),
                "end_parameter_gesture": lambda: self.handler.device_handler.end_parameter_gesture(params.get("track_index", 0), params.get("device_index", 0), params.get("parameter", 0)),
                "str_for_value": lambda: self.handler.device_handler.str_for_value(params.get("track_index", 0), params.get("device_index", 0), params.get("parameter", 0), params.get("value", 0.0)),
                "re_enable_automation": lambda: self.handler.device_handler.re_enable_automation(params.get("track_index", 0), params.get("device_index", 0), params.get("parameter", 0)),
                "set_device_routing": lambda: self.handler.device_handler.set_device_routing(
                     params.get("track_index", 0), params.get("device_index", 0),
                     routing_type=params.get("routing_type"), routing_channel=params.get("routing_channel")
                ),
                
                # Phase 7: Final Polish
                "get_data": lambda: self.handler.song_handler.get_data(params.get("key", "")),
                "set_data": lambda: self.handler.song_handler.set_data(params.get("key", ""), params.get("value", "")),
                "move_device": lambda: self.handler.song_handler.move_device(
                    params.get("track_index", 0), params.get("device_index", 0),
                    params.get("target_track_index", 0), params.get("target_index", -1)
                ),
                "store_variation": lambda: self.handler.device_handler.store_variation(
                    params.get("track_index", 0), params.get("device_index", 0), params.get("variation_index", -1)
                ),
                "recall_variation": lambda: self.handler.device_handler.recall_variation(
                    params.get("track_index", 0), params.get("device_index", 0), params.get("variation_index", -1)
                ),
                "delete_variation": lambda: self.handler.device_handler.delete_variation(
                    params.get("track_index", 0), params.get("device_index", 0), params.get("variation_index", -1)
                ),
                "randomize_macros": lambda: self.handler.device_handler.randomize_macros(
                    params.get("track_index", 0), params.get("device_index", 0)
                ),
                "copy_pad": lambda: self.handler.device_handler.copy_pad(
                    params.get("track_index", 0), params.get("device_index", 0),
                    params.get("from_note", 0), params.get("to_note", 0)
                ),
                
                
                # =============================================================
                # PHASE 3 COMMANDS
                # =============================================================
                # BrowserHandler (Updates)
                "preview_item_by_uri": lambda: self.handler.browser_handler.preview_item_by_uri(params.get("uri", "")),
                
                # SampleHandler (New)
                "get_sample_details": lambda: self.handler.sample_handler.get_sample_details(params.get("track_index", 0), params.get("clip_index", None), params.get("device_index", None)),
                "get_slices": lambda: self.handler.sample_handler.get_slices(params.get("track_index", 0), params.get("clip_index", None), params.get("device_index", None)),
                "insert_slice": lambda: self.handler.sample_handler.insert_slice(params.get("track_index", 0), params.get("slice_time", 0), params.get("clip_index", None), params.get("device_index", None)),
                "remove_slice": lambda: self.handler.sample_handler.remove_slice(params.get("track_index", 0), params.get("slice_time", 0), params.get("clip_index", None), params.get("device_index", None)),
                "clear_slices": lambda: self.handler.sample_handler.clear_slices(params.get("track_index", 0), params.get("clip_index", None), params.get("device_index", None)),
                "reset_slices": lambda: self.handler.sample_handler.reset_slices(params.get("track_index", 0), params.get("clip_index", None), params.get("device_index", None)),
                "set_sample_gain": lambda: self.handler.sample_handler.set_sample_gain(params.get("track_index", 0), params.get("gain", 1.0), params.get("clip_index", None), params.get("device_index", None)),
                "get_gain_display_string": lambda: self.handler.sample_handler.get_gain_display_string(params.get("track_index", 0), params.get("clip_index", None), params.get("device_index", None)),
                "beat_to_sample_time": lambda: self.handler.sample_handler.beat_to_sample_time(params.get("track_index", 0), params.get("beat_time", 0.0), params.get("clip_index", None), params.get("device_index", None)),
                "sample_to_beat_time": lambda: self.handler.sample_handler.sample_to_beat_time(params.get("track_index", 0), params.get("sample_time", 0.0), params.get("clip_index", None), params.get("device_index", None)),

                "create_drum_rack_from_audio_clip": lambda: self.handler.conversion_handler.create_drum_rack_from_audio_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                "move_devices_to_drum_rack": lambda: self.handler.conversion_handler.move_devices_to_drum_rack(
                    params.get("track_index", 0)
                ),
                "midi_to_audio": lambda: self.handler.conversion_handler.midi_to_audio(
                    params.get("track_index", 0)
                ),
                "consolidate_clip": lambda: self.handler.conversion_handler.consolidate_clip(
                    params.get("track_index", 0),
                    params.get("clip_index", 0)
                ),
                # Specialized Device Operations (uses modular SpecializedDeviceHandler)
                "set_eq8_band": lambda: self.handler.specialized_device_handler.set_eq8_band(
                    params.get("track_index", 0),
                    params.get("band_index", 1),
                    enabled=params.get("enabled", None),
                    freq=params.get("freq", None),
                    gain=params.get("gain", None),
                    q=params.get("q", None),
                    filter_type=params.get("filter_type", None),
                    device_index=params.get("device_index", None)
                ),
                "set_compressor_sidechain": lambda: self.handler.specialized_device_handler.set_compressor_sidechain(
                    params.get("track_index", 0),
                    enabled=params.get("enabled", None),
                    source_track_index=params.get("source_track_index", None),
                    gain=params.get("gain", None),
                    mix=params.get("mix", None),
                    device_index=params.get("device_index", None)
                )
            }

            if command_type == "get_session_info":
                response["result"] = self.handler._get_session_info()
            elif command_type == "get_track_info":
                track_index = params.get("track_index", 0)
                response["result"] = self.handler.track_handler.get_track_info(track_index)
            elif command_type == "list_clips":
                track_pattern = params.get("track_pattern", None)
                match_mode = params.get("match_mode", "contains")
                response["result"] = self.handler.track_handler.list_clips(track_pattern, match_mode)
            elif command_type in main_thread_commands:
                # Use a thread-safe approach with a response queue
                response_queue = queue.Queue()

                def main_thread_task():
                    try:
                        result = main_thread_commands[command_type]()
                        response_queue.put({"status": "success", "result": result})
                    except Exception as e:
                        # Log to handler's logger if possible
                        if hasattr(self.handler, "log_message"):
                            self.handler.log_message("Error in main thread task: " + str(e))
                            self.handler.log_message(traceback.format_exc())
                        response_queue.put({"status": "error", "message": str(e)})

                # Schedule the task on the main thread
                # This logic was previously in _process_command
                try:
                    self.handler.schedule_message(0, main_thread_task)
                except AssertionError:
                    main_thread_task()

                # Wait for response
                try:
                    task_response = response_queue.get(timeout=10.0)
                    if task_response.get("status") == "error":
                        response["status"] = "error"
                        response["message"] = task_response.get("message", "Unknown error")
                    else:
                        response["result"] = task_response.get("result", {})
                except queue.Empty:
                    response["status"] = "error"
                    response["message"] = "Timeout waiting for operation to complete"
                    
            elif command_type == "get_browser_item":
                uri = params.get("uri", None)
                path = params.get("path", None)
                response["result"] = self.handler._get_browser_item(uri, path)
            elif command_type == "get_browser_categories":
                # These were not in the big dict in __init__.py? 
                # Wait, I copied the original _process_command logic.
                # get_browser_categories and get_browser_items were in the original _process_command logic?
                # Ah, the original file I read in the view_file (earlier in conversation) had:
                # elif command_type == "get_browser_item": ...
                # elif command_type == "get_browser_categories": ...
                # elif command_type == "get_browser_items": ...
                # I should just delegate these if they exist on the handler
                
                # Double checking the original file content view...
                # Yes, they were present.
                if hasattr(self.handler, "_get_browser_categories"):
                    response["result"] = self.handler._get_browser_categories(params.get("category_type", "all"))
                else:
                     response["status"] = "error"; response["message"] = "Command not implemented"
                     
            elif command_type == "get_browser_items":
                if hasattr(self.handler, "_get_browser_items"):
                    response["result"] = self.handler._get_browser_items(params.get("path", ""), params.get("item_type", "all"))
                else:
                    response["status"] = "error"; response["message"] = "Command not implemented"
                    
            elif command_type == "get_browser_tree":
                response["result"] = self.handler.get_browser_tree(params.get("category_type", "all"))
            elif command_type == "get_browser_items_at_path":
                response["result"] = self.handler.get_browser_items_at_path(params.get("path", ""))
            else:
                response["status"] = "error"
                response["message"] = "Unknown command: " + command_type
                
        except Exception as e:
            if hasattr(self.handler, "log_message"):
                self.handler.log_message("Error processing command: " + str(e))
                self.handler.log_message(traceback.format_exc())
            response["status"] = "error"
            response["message"] = str(e)
            
        return response
