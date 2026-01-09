---
description: How to generate chiptune tracks with authentic sounds, structures, and progressions
---

# Chiptune Generation Workflow

Generate authentic chiptune tracks using the MCP tooling. This workflow covers sound selection, arrangement, and clip generation.

## 1. Project Setup

Create the base tracks:
```python
from mcp_tooling.connection import get_ableton_connection
conn = get_ableton_connection()

# Create 4-5 MIDI tracks
conn.send_command("create_midi_track", {"index": -1})  # Lead
conn.send_command("create_midi_track", {"index": -1})  # Arp/Chords
conn.send_command("create_midi_track", {"index": -1})  # Bass
conn.send_command("create_midi_track", {"index": -1})  # Drums
```

## 2. Load Instruments

### Chip Leads
Search terms: `chip`, `8-bit`, `retro`, `square`, `Chipped`
```python
search_and_load_device(track_index=0, query="Chipped")
```

### Chip Bass
Search terms: `retro bass`, `sub`, `triangle`, `Retromancer`
```python
search_and_load_device(track_index=2, query="Retromancer Bass")
```

### Drums
Search terms: `606`, `808`, `909`
```python
search_and_load_device(track_index=3, query="606 Core Kit")
```

### Add Bitcrush (optional)
```python
search_and_load_device(track_index=0, query="Redux")
```

## 3. Choose Chord Progressions

Use progressions from `constants.py` by mood:

| Mood | Progression Name | Chords |
|:---|:---|:---|
| **Heroic** | `chip_heroic` | I → V → vi → IV |
| **Action** | `chip_action` | I → bVII → IV → I |
| **Gothic** | `chip_gothic` | i → bVI → bVII → i |
| **Bouncy** | `chip_bouncy` | I → I → IV → IV → V → V → I → I |
| **Power** | `chip_power` | I → V → I → V |
| **Boss** | `chip_boss_minor` | i → bVI → bVII → V |

```python
generate_chord_progression_advanced(
    track_index=1,
    clip_index=0,
    key="F#",
    scale="mixolydian",
    progression="chip_action",
    beats_per_chord=4.0
)
```

## 4. Generate Bass

### Walking Bass (Jazz feel)
```python
generate_advanced_bassline(
    track_index=2,
    clip_index=0,
    key="F#",
    scale="mixolydian",
    style="jazz_walking",
    octave=2,
    bars=16
)
```

### Standard Bass Styles
- `simple` - Root notes only
- `octave` - Root + octave jumps
- `syncopated` - Funky offbeats
- `jazz_walking` - Quarter-note walk

## 5. Generate Drums

### Driving Punk Patterns
Use custom pattern generation:
```python
# Punk Drive: kick 1+3, snare 2+4, 8th hats
generate_drum_pattern(
    track_index=3,
    clip_index=0,
    genre="rock",
    pattern_name="Rock 1_break",
    bars=4
)
```

### Pattern Types by Feel
| Feel | Pattern Style | Key Elements |
|:---|:---|:---|
| Driving | 4-on-floor + offbeat hats | Steady kick |
| Punk | Kick 1+3, snare 2+4 | 8th note hats |
| Dance | 4-on-floor + open hat | Sizzle on 8 |
| Half-time | Snare on 3 | Verse feel |

## 6. Arpeggiation

### Chord Simulation (1/32 speed)
```python
# Arpeggiator settings
arp_style = "up"  # or "down", "updown"
arp_rate = "1/32"
arp_pattern = [0, 4, 7]  # Major triad in semitones
```

### Common Arp Patterns
| Name | Pattern | Speed | Use |
|:---|:---|:---|:---|
| Major Chord | 1-3-5 | 1/32 | Bright |
| Minor Chord | 1-b3-5 | 1/32 | Dark |
| Power | 1-5 | 1/16 | Punk |
| Octave | 1-8 | 1/16 | Thick lead |

## 7. Song Structure Templates

### Standard (Action/Adventure)
```
Intro (4-8 bars) → Theme A (16 bars) → Theme B (16 bars) 
→ Theme A → Bridge → Theme A → Outro
```

### Punk/Rock
```
Intro (8) → Verse (16) → Chorus (16) → Verse (16) 
→ Chorus → Bridge (8) → Chorus → Outro
```

### Loop (Game style)
```
Intro (2-4 bars) → Main Loop (16-32 bars) → repeat
```

## 8. Tempo & Key Reference

### Tempos by Style
| Style | BPM |
|:---|:---|
| Action | 140-180 |
| Exploration | 100-120 |
| Boss | 160-200 |
| Menu | 80-100 |
| Dance | 128-140 |

### Recommended Keys
- **Bright/Energetic**: F#, G, A major
- **Neutral**: C, D major
- **Dark/Dramatic**: D minor, A minor, E minor

## 9. Full Generation Example

```python
from mcp_tooling.generators import generate_chord_progression_advanced
from mcp_tooling.basslines import generate_advanced_bassline
from mcp_tooling.drummer import generate_drum_pattern
from mcp_tooling.devices import search_and_load_device

# Setup tracks
conn.send_command("create_midi_track", {"index": -1})
conn.send_command("set_track_name", {"track_index": 0, "name": "Lead"})

# Load sounds
search_and_load_device(track_index=0, query="Chipped")
search_and_load_device(track_index=1, query="606 Core Kit")

# Generate content
generate_chord_progression_advanced(
    track_index=0, clip_index=0,
    key="F#", scale="mixolydian",
    progression="chip_heroic"
)

generate_drum_pattern(
    track_index=1, clip_index=0,
    genre="rock", bars=4
)

# Play
conn.send_command("fire_scene", {"scene_index": 0})
```

## 10. Quick Reference

### Ableton Search Terms
| Sound | Search |
|:---|:---|
| Chip Lead | `chip`, `8-bit`, `Chipped` |
| Chip Bass | `retro bass`, `Retromancer` |
| Drums | `606 Core Kit` |
| Bitcrush | `Redux` |
| Synth | `Operator`, `Wavetable` |

### Progression Shortcuts
| Mood | Use |
|:---|:---|
| `chip_heroic` | Main theme |
| `chip_action` | Stage/driving |
| `chip_gothic` | Dark/dungeon |
| `chip_bouncy` | Playful |
| `chip_boss_minor` | Boss battle |

---

## 11. 1bitdragon VST Plugins

Specialized chiptune VST plugins. Load manually via Ableton's Plugin Browser (Plug-ins → VST).

### Synthesizers (1bs_)

| Plugin | DLL Name | Character |
|:---|:---|:---|
| **PulseSynth** | `1bs_pulsesynth_x64` | Classic pulse/square waves |
| **WaveSynth** | `1bs_wavesynth_x64` | Wavetable synthesis |
| **NoiseSynth** | `1bs_noisesynth_x64` | Noise-based textures |
| **OverSynth** | `1bs_oversynth_x64` | Overdriven chip sounds |
| **PhaseSynth** | `1bs_phasesynth_x64` | Phase modulation |
| **PhatSynth** | `1bs_phatsynth_x64` | Thick, detuned leads |
| **SerialSynth** | `1bs_serialsynth_x64` | Sequential synthesis |
| **SweepSynth** | `1bs_sweepsynth_x64` | Filter sweeps |

### Drums (1bs_)

| Plugin | DLL Name | Character |
|:---|:---|:---|
| **NoiseDrums** | `1bs_noisedrums_x64` | Noise-based percussion |
| **ClickyDrums** | `1bs_clickydrums_x64` | Snappy, clicky hits |
| **TapeDrums** | `1bs_tapedrums_x64` | Lo-fi, warm drums |
| **TNDrums** | `1bs_tndrums_x64` | Tight, punchy drums |

### Effects (1be_)

| Plugin | DLL Name | Use |
|:---|:---|:---|
| **BitDrive** | `1be_bitdrive_x64` | Bitcrush + drive |
| **PulseDrive** | `1be_pulsedrive_x64` | Pulse shaping + saturation |

### Recommended Combos

#### Classic Chip Lead
- **PulseSynth** → Square wave lead

#### Thick Pad/Chord
- **PhatSynth** → Detuned chip chords

#### Authentic Drums
- **NoiseDrums** or **ClickyDrums** → Chip percussion

#### Add Grit
- Any synth → **BitDrive** → Authentic distortion

### Loading in Ableton
1. Open Plug-ins → VST → 1bitdragon folder
2. Drag plugin to track
3. Use x64 versions for 64-bit Ableton


