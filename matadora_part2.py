"""
Matadora Part 2 - Adding Layers
Add Rim, Texture, and Bass tracks
"""
from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.generators import pattern_generator
from mcp_tooling.devices import search_and_load_device
import time

conn = get_ableton_connection()

print("=== CHECKING SESSION ===")
info = conn.send_command("get_session_info", {})
print(f"Current tracks: {info.get('track_count', 0)}")

# We assume tracks 0 & 1 exist (Perc, Kick) needed from previous step
# If not, we'd need to rebuild, but let's assume valid state for now.

print("\n=== ADDING NEW TRACKS ===")

# Track 2: Rim/Stick (Percussion texture)
result = conn.send_command("create_midi_track", {"index": -1})
rim_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": rim_idx, "name": "Rim Perc"})
print(f"Created: Rim Perc (track {rim_idx})")

# Track 3: Texture (Audio)
result = conn.send_command("create_audio_track", {"index": -1})
tex_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": tex_idx, "name": "Texture"})
print(f"Created: Texture (track {tex_idx})")

# Track 4: Bass (MIDI) - No clips yet, just setup
result = conn.send_command("create_midi_track", {"index": -1})
bass_idx = result.get("index")
conn.send_command("set_track_name", {"track_index": bass_idx, "name": "Bass"})
print(f"Created: Bass (track {bass_idx})")

print("\n=== LOADING DEVICES ===")

# Load Rim kit
print("Loading Rim kit...")
search_and_load_device(rim_idx, "Drum Rack", "drums")
time.sleep(1.0)
# (In a real scenario we'd load specific samples, but using default Rack for now and hoping for valid hits or using 'Conga'/'Bongo' maybe?)
# Let's try loading a specific Percussion kit if possible, or just standard Drum Rack
# search_and_load_device(rim_idx, "Latin Percussion", "drums") # Example

# Load Texture FX
print("Loading Auto Filter on Texture...")
search_and_load_device(tex_idx, "Auto Filter", "audio_effects")
# Set filter to lowpass with movement
conn.send_command("set_device_parameter", {"track_index": tex_idx, "device_index": 0, "parameter_name": "Filter Type", "value": 0.0}) # Lowpass
conn.send_command("set_device_parameter", {"track_index": tex_idx, "device_index": 0, "parameter_name": "Frequency", "value": 0.4}) # ~600Hz
conn.send_command("set_device_parameter", {"track_index": tex_idx, "device_index": 0, "parameter_name": "LFO Amount", "value": 0.3}) # Movement

# Load Bass Synth
print("Loading Bass Synth (Analog)...")
search_and_load_device(bass_idx, "Analog", "instruments")

print("\n=== GENERATING RIM PATTERN ===")
# Use 'trap' style for Rim to get those fast hi-hat like rolls/offbeats? 
# Or 'rock_basic' for steady offbeats?
# Let's try pattern_generator with high swing
pattern_generator(
    track_index=rim_idx,
    clip_slot_index=0,
    pattern_type="breakbeat", # Syncopated
    bars=8,
    root_note=37, # Rim/Stick usually around C#1/D1
    velocity=80,
    swing=0.2, # Heavy swing
    humanize=0.3
)

print("\n=== UPDATING SCENE ===")
# Fire scene 0 again to include new clips
conn.send_command("fire_scene", {"scene_index": 0})

print("\n✓ Added Rim, Texture, and Bass tracks!")
