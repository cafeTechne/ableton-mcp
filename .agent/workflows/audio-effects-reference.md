---
description: Comprehensive reference for built-in Audio Effects
---

# Audio Effect Reference

Live's built-in effects range from essential mixing tools (EQ, Compression) to creative sound design modules (Echo, Beat Repeat, Corpus).

## 1. Dynamics & Mixing

Control the volume and "energy" of your signals.

- **Compressor**: Standard gain reduction. Use **RMS** mode for musicality, **Peak** for aggressive control. Supports **Sidechain** (ducking).
- **Glue Compressor**: Analog-modeled bus compressor. Use for "gluing" groups together. Features **Soft Clip** to tame transients.
- **Gate**: Passes signal only above a threshold. Useful for removing noise or rhythmic triggering (via **Sidechain**).
- **Drum Buss**: All-in-one drum processor. Includes distortion (**Soft/Med/Hard**), **Crunch**, and **Boom** (resonant low-end).

```python
# Enable Compressor Sidechain from Track 2
conn.send_command("set_compressor_sidechain", {
    "track_index": 0, "device_index": 0, "source_track_index": 2
})
```

## 2. Filters & EQ

Shape the frequency spectrum.

- **EQ Eight**: 8-band parametric EQ. Supports **Stereo**, **L/R**, and **M/S** (Mid/Side) modes. Use **Oversampling** for high-frequency precision.
- **Auto Filter**: Analog-modeled filter with **LFO** and **Envelope Follower**. Circuit models: **OSR**, **MS2**, **SMP**, **PRD**.
- **Channel EQ**: Simple 3-band EQ inspired by classic desks (Low 80Hz HP, Mid Sweep, High Shelving).

## 3. Time, Space & Modulation

Create depth, movement, and rhythm.

- **Delay**: Independent Left/Right lines. Transition modes: **Repitch** (analog-style), **Fade** (smooth), **Jump**. Supports **Ping Pong**.
- **Echo**: Modulation delay with "Tunnel" visualization. Includes **Ducking**, **Noise**, and **Wobble** (tape-style) character.
- **Beat Repeat**: Rhythmic repetitions. Use **Chance** for randomness and **Variation** for grid-size shifts.
- **Chorus-Ensemble**: Thickening effects. Modes: **Classic**, **Ensemble** (thick 70s style), **Vibrato**.
- **Auto Pan**: LFO-driven amplitude/panning. Perfect for tremolo or "chopped" effects.

## 4. Saturation & Distortion

Add grit, warmth, and harmonics.

- **Amp / Cabinet**: Guitar amp and speaker emulation. 7 Amp models (Clean, Boost, Blues, Rock, Lead, Heavy, Bass).
- **Dynamic Tube**: Analog tube saturation with an integrated envelope follower for bias modulation.
- **Erosion**: Digital degradation via noise/sine waves. Adds "aliasing" grit.

## 5. Creative & Specialized

- **Corpus**: Physical modeling resonator (Beam, Marimba, Pipe, etc.). Can be played via **MIDI Sidechain**.
- **Shifter / Frequency Shifter**: Moves frequencies by Hz (not Pitch). Creates dissonant, metallic, or phasing effects.
- **Grain Delay**: Slices audio into "grains". Pitch and Spray randomization creates complex textures.

```python
# Tune Drum Buss Boom to the nearest MIDI note
conn.send_command("set_device_parameter", {
    "track_index": 0, "device_index": 1, "parameter_name": "Boom Force To Note", "value": 1.0
})
```

## 6. Utilities

- **External Audio Effect**: Use hardware processors. Set **Hardware Latency** (ms/samples) to sync with Live's delay compensation.

## 7. Reverb & Space

Create depth, ambience, and room simulations.

- **Reverb**: Classic algorithmic reverb. **Diffusion Network** + **Early Reflections** + **Chorus** for rich tails.
- **Hybrid Reverb**: Convolution + Algorithmic in one. Algorithms: **Dark Hall**, **Quartz**, **Shimmer** (pitch-shifted tail), **Tides** (spectral ripples), **Prism** (velvet noise).

| Algorithm | Character |
|:---|:---|
| Dark Hall | Smooth, classic, metallic at small sizes |
| Quartz | Clear early reflections, good for drums/voice |
| Shimmer | Pitch-shifted feedback for ethereal pads |
| Prism | Bright, "ghost" reverb for non-linear decays |

> [!TIP]
> In **Hybrid Reverb**, drop any audio file into the convolution display to use it as a custom impulse response.

## 8. Mastering & Dynamics

- **Limiter**: Prevents clipping on the Master. Use **Lookahead** for transient handling.
- **Multiband Dynamics**: Up to 6 simultaneous dynamics processes (upward/downward compression/expansion across 3 bands). Good for de-essing (only high band) or "uncompression" (restoring life to squashed masters).
- **Saturator**: Waveshaping from soft to hard. **Waveshaper** mode gives 6 extra parameters (Drive, Lin, Curve, Damp, Depth, Period).

## 9. Spectral Effects

- **Spectral Resonator**: Add tonal character via pitched harmonics. Feed it **MIDI** to create vocoder-like effects or tonal drum loops.
- **Spectral Time**: Freeze audio + spectral delay. Use **Tilt** and **Spray** to smear frequencies over time.
- **Vocoder**: Classic carrier/modulator synthesis. Use **Pitch Tracking** for a monophonic carrier synced to the modulator's pitch.

## 10. Utilities

- **Utility**: Phase inversion, Width control, **Bass Mono** (mono-ize sub-bass), DC offset filtering, and Mute.
- **Spectrum**: Frequency analyzer (not an effect). Set **Block** size for accuracy vs. CPU tradeoff.
- **Tuner**: Monophonic pitch detection. Adjust **Reference** (default 440Hz) for alternate tunings.
- **Looper**: Real-time looping device. Syncs to tempo or sets tempo from incoming audio. **Drag me!** to export loops as clips.

> [!TIP]
> Use **Sidechain Listen** (Headphone icon) on devices like Gate or Compressor to find the perfect trigger frequency without affecting the output.
