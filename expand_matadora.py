"""
Expand Matadora - Scenes 5 & 6
Varied MIDI performances (Funk, Reggae, Disco styles)
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import (
    generate_bassline_advanced_wrapper,
    generate_rhythmic_comp,
    pattern_generator
)

conn = get_ableton_connection()

print("=== EXPANDING MATADORA ===")

# Map from Output 3083
TRK_HAND = 1
TRK_KICK = 2
TRK_RIM = 3
TRK_BASS = 5
TRK_STABS = 7
TRK_TEX = 8 # 9-Analog

# Create Scenes 5 and 6 (Index 4 and 5)
# Current Scenes: 0(Intro), 1(Drop), 2(Var), 3(Break), 4(Outro - Wait, Outro was 3)
# So new scenes will be 4 and 5.
# Wait, let's insert them BEFORE Outro? Or Append?
# User said "add more scenes". Usually append.
# But Outro should be last.
# I will append 4 and 5, then rename 4->Bridge, 5->Build.
# Scene 3 was Outro. 
# So 4/5 will be AFTER Outro.
# User wants "more parts".
# I'll create 4 and 5. Then user can rearrange. Or I can insert?
# `create_scene` has `index`.
# If I insert at 3, existing 3 (Outro) shifts to 4.
# If I insert at 4, existing 3 shifts? No.
# I'll insert at 3 (Bridge) and 4 (Build), pushing Outro to 5.

# Scene 3: Bridge (Insert)
print("Creating Bridge (Scene 3)...")
conn.send_command("create_scene", {"index": 3}) 
conn.send_command("set_scene_name", {"scene_index": 3, "name": "Bridge"})

# Scene 4: Build (Insert)
print("Creating Build (Scene 4)...")
conn.send_command("create_scene", {"index": 4})
conn.send_command("set_scene_name", {"scene_index": 4, "name": "Build"})

# Now:
# 0: Intro
# 1: Drop
# 2: Breakdown
# 3: Bridge (New)
# 4: Build (New)
# 5: Outro (Old 3)

# === POPULATE BRIDGE (Scene 3) ===
# Vibe: Funky, sparse, different progression? 
# Matadora key is Am. Let's stay Am but maybe i-v-i-v (Dorian vibe).
prog_bridge = "i v i v"

# Bass (Track 5) - Funk Style
print(generate_bassline_advanced_wrapper(
    track_index=TRK_BASS, clip_index=3,
    key="A", scale="minor", progression=prog_bridge,
    style="funk", velocity=95, humanize=0.2
))

# Stabs (Track 7) - Reggae Skank (Sparse)
print(generate_rhythmic_comp(
    track_index=TRK_STABS, clip_index=3,
    key="A", scale="minor", progression=prog_bridge,
    style="reggae_skank", velocity=90, beats_per_chord=2.0
))

# Rim (Track 3) - Breakbeat?
# pattern_generator doesn't support 'breakbeat' in args? Check defaults.
# It supports 'breakbeat', 'house', etc.
conn.send_command("create_clip", {"track_index": TRK_RIM, "clip_index": 3, "length": 4.0})
# Actually use helper (which assumes 1 bar?)
# pattern_generator(track_index, clip_slot_index, pattern_type, bars, root_note, velocity)
# But generators.py doesn't export pattern_generator wrapper directly in same way?
# Checking generators.py... It DOES have pattern_generator? No, it imports it from `rhythmic_comp`? 
# Wait, `pattern_generator` implies `generators.py`. 
# Let's check `generators.py` (Output 3043).
# It does NOT define `pattern_generator`! It imports `get_comp_pattern`.
# Where is `pattern_generator`? 
# Ah, Output 3006: `viewed_code_item mcp_tooling.generators.pattern_generator`.
# It WAS in `generators.py`?
# In Output 3043, I see imports: `from .rhythmic_comp import ...`
# I DO NOT SEE `def pattern_generator` in the first 800 lines.
# Maybe it was further down? Or removed in refactor?
# If I can't find it, I'll use `generate_rhythmic_comp` for drums (using 'quarters' or similar)?
# Or use `add_basic_drum_pattern` command.
# I will use `add_basic_drum_pattern` for now to be safe.

conn.send_command("add_basic_drum_pattern", {"track_index": TRK_RIM, "clip_index": 3})


# === POPULATE BUILD (Scene 4) ===
# Vibe: Driving, Disco, build tension.
prog_build = "VI VII i i" (Climb)

# Bass (Track 5) - Disco octaves
print(generate_bassline_advanced_wrapper(
    track_index=TRK_BASS, clip_index=4,
    key="A", scale="minor", progression=prog_build,
    style="disco", velocity=105, humanize=0.1
))

# Stabs (Track 7) - Disco Octaves / Driving
print(generate_rhythmic_comp(
    track_index=TRK_STABS, clip_index=4,
    key="A", scale="minor", progression=prog_build,
    style="disco_octaves", velocity=100
))

# Hand Perc (Track 1) - Full Pattern
conn.send_command("create_clip", {"track_index": TRK_HAND, "clip_index": 4, "length": 4.0})
# Fill with 16th notes?
# Manual add_notes
notes = []
for i in range(16):
    notes.append({"pitch": 60, "start_time": i*0.25, "duration": 0.2, "velocity": 80 + (i%4)*10})
conn.send_command("add_notes_to_clip", {"track_index": TRK_HAND, "clip_index": 4, "notes": notes})

# Kick (Track 2) - Driving 4-on-floor
conn.send_command("add_basic_drum_pattern", {"track_index": TRK_KICK, "clip_index": 4})


print("\n=== FIRING SCENE 4 (BUILD) === ")
conn.send_command("fire_scene", {"scene_index": 4}) 
print("Done.")
