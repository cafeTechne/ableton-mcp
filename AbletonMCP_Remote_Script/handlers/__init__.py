"""
Handler Modules for AbletonMCP Remote Script.

This package contains modular handlers for different aspects of Ableton Live control.

For Future Agents:
    Import handlers from this package and instantiate with an MCP reference:
    
    >>> from handlers import TrackHandler, SongHandler, SceneHandler
    >>> track_handler = TrackHandler(mcp_instance)
    >>> scene_handler = SceneHandler(mcp_instance)

Available Handlers:
    - TrackHandler: Core track and clip operations (create, edit, delete)
    - SongHandler: Song-level operations (transport, record, undo, metronome)
    - SceneHandler: Scene operations (create, launch, tempo, properties)
    - ClipHandler: Extended clip operations (fire, loop, warp, launch settings)
    - ClipSlotHandler: Session View slot operations (fire, stop, create clips)
    - MixerHandler: Mixer operations (master, returns, crossfader, sends)
    - ApplicationHandler: View control, browser, dialogs, version info
    - TrackGroupHandler: Group track operations (fold, members, colors)
    - BrowserHandler: Browser navigation and content loading
    - ConversionHandler: Audio-to-MIDI and other conversions
    - SpecializedDeviceHandler: EQ8, Compressor, Max, Wavetable, HybridReverb, Transmute
    - ChainHandler: Rack chain operations (name, mute, solo, mixer, drum chain)
    - DrumRackHandler: Drum Rack pad management (info, copy, choke groups)
    - GrooveHandler: Groove pool operations (apply, commit grooves)
    - SimplerHandler: Simpler/Sampler device control (reverse, crop, warp)
    - ArrangementHandler: Arrangement view (cue points, loops, navigation)
"""
from __future__ import absolute_import, print_function, unicode_literals

from .base import HandlerBase
from .track import TrackHandler
from .song import SongHandler
from .scene import SceneHandler
from .clip import ClipHandler
from .clip_slot import ClipSlotHandler
from .mixer import MixerHandler
from .application import ApplicationHandler
from .track_group import TrackGroupHandler
from .browser import BrowserHandler
from .conversion import ConversionHandler
from .specialized import SpecializedDeviceHandler
from .chain import ChainHandler
from .drum_rack import DrumRackHandler
from .groove import GrooveHandler
from .simpler import SimplerHandler
from .arrangement import ArrangementHandler
from .device import DeviceHandler
from .sample import SampleHandler

__all__ = [
    "HandlerBase",
    "TrackHandler",
    "SongHandler",
    "SceneHandler",
    "ClipHandler",
    "ClipSlotHandler",
    "MixerHandler",
    "ApplicationHandler",
    "TrackGroupHandler",
    "BrowserHandler",
    "ConversionHandler",
    "SpecializedDeviceHandler",
    "ChainHandler",
    "DrumRackHandler",
    "GrooveHandler",
    "SimplerHandler",
    "ArrangementHandler",
    "DeviceHandler",
    "SampleHandler",
]

