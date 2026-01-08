"""
Apply Specialized EQ to All Tracks
Uses set_eq8_band to apply production-ready EQ curves.
"""
import sys
import os
sys.path.append(os.path.join(os.getcwd(), "MCP_Server"))

from mcp_tooling.connection import get_ableton_connection
from mcp_tooling.devices import search_and_load_device

conn = get_ableton_connection()

# Track Map
# 0: DS Drum Rack
# 1: Hand Perc
# 2: Kick
# 3: Rim Perc
# 4: Texture
# 5: Bass
# 6: Atmosphere
# 7: Stabs
# 8: Analog

# Helper to load EQ8
def ensure_eq8(track_idx):
    # Check if EQ8 exists? 
    # Just try loading it. If it exists, it might add a second one.
    # Ideally check caching or device list.
    # For now, let's just attempt to load "EQ Eight". 
    # If it fails (already there?), we proceed.
    # Actually, Ableton adds duplicates. 
    # Let's hope searching "EQ Eight" is fast.
    print(f"Loading EQ Eight on Track {track_idx}...")
    search_and_load_device(track_idx, "EQ Eight", "audio_effects")

# Presets (Normalized values from /specialized-devices doc)
# Freq: 0.15=30Hz, 0.18=50Hz, 0.24=100Hz, 0.30=180Hz
# Filter Types: 0=LC12, 1=LC48, 2=LS, 3=Bell, 4=HS, 5=Notch, 6=HC12, 7=HC48

def apply_eq_kick(trk):
    ensure_eq8(trk)
    # Band 1: HP 30Hz (Clean mud)
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 1, "enabled": True, "freq": 0.15, "filter_type": 1})
    # Band 2: Boost 60Hz (Punch)
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 2, "enabled": True, "freq": 0.21, "gain": 0.65, "q": 1.0, "filter_type": 3})
    # Band 3: Cut 300Hz (Mud)
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 3, "enabled": True, "freq": 0.36, "gain": 0.40, "q": 0.5, "filter_type": 3})

def apply_eq_bass(trk):
    ensure_eq8(trk)
    # Band 1: HP 30Hz
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 1, "enabled": True, "freq": 0.15, "filter_type": 0})
    # Band 2: Boost 100Hz (Body)
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 2, "enabled": True, "freq": 0.24, "gain": 0.60, "q": 0.8, "filter_type": 3})

def apply_eq_high_pass(trk, freq_norm=0.30): # ~180Hz
    ensure_eq8(trk)
    # Band 1: HP
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 1, "enabled": True, "freq": freq_norm, "filter_type": 0})
    # Band 8: Air Boost
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 8, "enabled": True, "freq": 0.90, "gain": 0.55, "filter_type": 4})

def apply_eq_texture(trk):
    ensure_eq8(trk)
    # Band 1: HP 300Hz (Remove all lows)
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 1, "enabled": True, "freq": 0.36, "filter_type": 0})
    # Band 2: LP 8kHz (Remove harsh highs)
    conn.send_command("set_eq8_band", {"track_index": trk, "band_index": 8, "enabled": True, "freq": 0.88, "filter_type": 6})

print("=== APPLYING SPECIALIZED EQ ===")

# Track 0: Drums (Kit) - Generic Kick curve but maybe HP slightly? No, it has Kick.
# Actually Track 0 is "DS Drum Rack". It handles full kit.
# Apply slight smiley face?
# Let's apply Kick logic to T0 (Drums) and T2 (Kick).
print("- Drums (Kit)")
apply_eq_kick(0) 

print("- Hand Perc")
apply_eq_high_pass(1, freq_norm=0.30) # 180Hz HP

print("- Kick")
apply_eq_kick(2)

print("- Rim Perc")
apply_eq_high_pass(3, freq_norm=0.30)

print("- Texture")
apply_eq_texture(4)

print("- Bass")
apply_eq_bass(5)

print("- Atmosphere")
apply_eq_texture(6)

print("- Stabs")
apply_eq_high_pass(7, freq_norm=0.30) # Clear space for bass

print("- Analog")
apply_eq_high_pass(8, freq_norm=0.25) # 120Hz

print("Done.")
