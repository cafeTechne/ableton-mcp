---
description: How to generate drum patterns from the library
---

# Drum Pattern Generation Workflow

This workflow covers generating drum patterns using the 1437-pattern drum library.

## Available Genres

Use `list_drum_genres` to see all available genres. Current genres include:
- **Electronic**: techno, house, dnb, dubstep, footwork, garage, trap
- **Acoustic**: rock, jazz, blues, latin, bossa_nova, ballad
- **Urban**: hip_hop, funk, disco, breakbeat
- **Special**: fills, classic_songs

## Quick Start

### 1. List Genres
```
list_drum_genres()
```

### 2. Browse Patterns in a Genre
```
list_drum_patterns(genre="latin")
list_drum_patterns(genre="house", variation="A")
```

### 3. Search for Specific Patterns
```
search_drum_patterns(query="funk", limit=10)
search_drum_patterns(query="shuffle", genre="rock")
```

## Generating Patterns

### Basic Pattern Generation
```python
# Random pattern from genre
generate_drum_pattern(
    track_index=0,      # Drum rack track
    clip_index=0,       # Scene
    genre="latin",
    bars=4
)

# Specific pattern
generate_drum_pattern(
    track_index=0,
    clip_index=0,
    genre="latin",
    pattern_name="Afro-Cuban 1_measure_a",
    bars=4
)
```

### With Humanization & Swing
```python
generate_drum_pattern(
    track_index=0,
    clip_index=0,
    genre="funk",
    variation="A",
    bars=4,
    velocity_scale=0.9,   # Slightly quieter
    humanize=0.2,         # Timing/velocity variation
    swing=0.3             # Offbeat swing
)
```

### Generate Fills
```python
# Perfect for transitions
generate_drum_fill(
    track_index=0,
    clip_index=3,         # Last scene before drop
    genre="rock",
    bars=1
)
```

### Generate Full Sections (A/B + Fill)
```python
# Creates varied patterns across multiple clips
generate_drum_section(
    track_index=0,
    clip_indices="0,1,2,3",   # 4 scenes
    genre="house",
    include_fill=True,
    bars_per_clip=4
)
# Result: A, B, A, Fill patterns
```

## Pattern Variations

Each pattern typically has:
- **A**: Main groove variation
- **B**: Alternate groove  
- **fill**: Transition fill

Filter by variation:
```python
list_drum_patterns(genre="rock", variation="fill")
generate_drum_pattern(..., variation="A")
```

## MIDI Note Mapping

Patterns use General MIDI drum mapping:
- 36: Kick
- 37: Sidestick
- 38: Snare
- 42: Closed Hi-Hat
- 43: Low Tom
- 46: Open Hi-Hat
- 47: Mid Tom
- 49: Crash

## Tips

1. **Match your kit**: Ensure your Drum Rack uses GM MIDI mapping
2. **Layer patterns**: Combine patterns from different genres
3. **Build sections**: Use `generate_drum_section` for quick arrangements
4. **Humanize**: Values 0.1-0.3 add realistic feel without chaos
5. **Swing**: Use 0.2-0.4 for funk/hip-hop feels
