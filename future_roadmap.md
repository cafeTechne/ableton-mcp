# Future Roadmap & Backwards Planning

This model outlines the missing capabilities needed to support advanced workflows like "Fix the Mix", "Full Arrangement", and "Deep Sound Design".

## 1. Advanced Routing & Mixing
**Goal**: Enable complex routing (sidechaining, sub-mixes) and return track management.

| Tool Name | Purpose | Implementation Idea |
|:---|:---|:---|
| `set_device_sidechain` | Route audio from Track A to Compressor on Track B | Requires `Live.DeviceParameter` routing API access |
| `create_return_track` | Create A/B return tracks (Reverb/Delay) | Live API: `song.create_return_track()` |
| `get_routing_options` | List valid inputs/outputs for a track | Live API: `track.available_input_routing_types` |
| `set_track_output` | Route Pad -> Bus Group | Live API: `track.output_routing_type` |

## 2. Arrangement View Control
**Goal**: Move beyond Session View loops to linear song structure.

| Tool Name | Purpose | Implementation Idea |
|:---|:---|:---|
| `set_locator` | Add "Chorus", "Verse" markers to timeline | Live API: `song.add_cue_point(time, name)` |
| `record_to_arrangement` | Record session clips to arrangement | Trigger "Global Record" + "Session Record" |
| `get_arrangement_structure` | Read markers and time signature changes | Iterate `song.cue_points` |
| `arrange_clip` | Place specific clip at time | Live API: `track.create_clip(time, length)` |

## 3. Advanced Clip Operations
**Goal**: Humanize, polish, and fix generated content.

| Tool Name | Purpose | Implementation Idea |
|:---|:---|:---|
| `quantize_clip` | Fix timing of MIDI/Audio | Live API: `clip.quantize(quantization_grid, amount)` |
| `transpose_clip` | Key changes for existing content | Iterate notes -> `note.pitch += shift` |
| `apply_legato` | Extend notes to touch next note | Python logic: modify `duration` of notes |
| `get_clip_notes` | Read notes from a clip | Live API: `clip.get_notes(start, time, pitch, rang)` |

## 4. Racks & Sound Design
**Goal**: Create custom instruments and complex effect chains.

| Tool Name | Purpose | Implementation Idea |
|:---|:---|:---|
| `group_devices` | Put selected devices into a Rack | Live API: `view.selected_track.view.select_device; view.group_selected_devices` |
| `map_macro` | Map Filter Cutoff -> Macro 1 | Live API: `parameter.map_to_macro(macro_index)` |
| `set_chain_vol_pan` | Mix chains inside a drum rack | Access `device.chains[i].mixer_device` |

## 5. Sample Manipulation
**Goal**: Deep control over audio handling.

| Tool Name | Purpose | Implementation Idea |
|:---|:---|:---|
| `slice_to_drum_rack` | Convert loop to kit | Live API: custom command or built-in action |
| `set_sample_start_end` | Trim sample playback | Simpler API: `start_marker`, `end_marker` |
| `reverse_clip` | Reverse audio | Live API: `clip.audio_clip.reverse()` |


## 6. Pro Workflows (User Feedback)
**Goal**: Support advanced production techniques and third-party tools.

| Tool Name | Purpose | Implementation Idea |
|:---|:---|:---|
| `load_vst` | Load 3rd party plugins (Serum, Vital) | Use `search_and_load_device` with "Plug-ins" category |
| `set_arpeggiator` | Control Ableton Arp device | Load "Arpeggiator" -> Set Rate/Style params |
| `generate_arpeggio` | Python-based MIDI arp generation | Implement `arpeggiate` flag in `generators.py` |
| `save_vst_preset` | Save VST state as .adg for recall | User manual step or key command emulation |
| `custom_chord_prog` | "I V vi IV" string input | **Already Supported** (Document it!) |

## Implementation Priority (Tomorrow)

1.  **Quantize & Transpose** (`quantize_clip`, `transpose_clip`) - Immediate musical value.
2.  **Sidechain Routing** (`set_device_sidechain`) - Critical for mixing.
3.  **Return Tracks** (`create_return_track`) - Essential for professional production.
4.  **Arpeggiator Workflow** (`set_arpeggiator`) - High leverage for electronic music.
5.  **VST Support Guide** - Documentation only (functionality exists).
