"""
Matadora Part 3 - The Drop (Bass Entry) -- DEBUG MODE
Create Scene 2, copy percussion, generate syncopated bass
"""
import sys
import os

# Diagnostic: Print sys.path and inspect generators
print("DEBUG: sys.path:", sys.path)
try:
    import mcp_tooling.generators as generators
    print("DEBUG: generators loaded from:", generators.__file__)
    print("DEBUG: Available in generators:", [x for x in dir(generators) if "bass" in x.lower()])
except ImportError:
    print("DEBUG: Failed to import mcp_tooling.generators")
    # Try adding MCP_Server to path manually if needed
    svr_path = os.path.join(os.getcwd(), "MCP_Server")
    if svr_path not in sys.path:
        sys.path.append(svr_path)
    try:
        import mcp_tooling.generators as generators
        print("DEBUG: generators loaded (retry) from:", generators.__file__)
    except Exception as e:
        print("DEBUG: Retry failed:", e)

from mcp_tooling.connection import get_ableton_connection

# Try importing the wrapper again
try:
    from mcp_tooling.generators import generate_bassline_advanced_wrapper
except ImportError:
    print("WARNING: generate_bassline_advanced_wrapper import failed. Using fallback loop.")
    generate_bassline_advanced_wrapper = None

conn = get_ableton_connection()

print("=== SETTING UP SCENE 2 (BASS ENTRY) ===")

# Create Scene 1 (Index 1) - "Bass Entry"
try:
    conn.send_command("create_scene", {"index": 1})
    conn.send_command("set_scene_name", {"scene_index": 1, "name": "Bass Entry"})
except Exception as e:
    print(f"Scene creation note: {e}")

# Copy clips from Scene 0 to Scene 1
info = conn.send_command("get_session_info", {})
tracks = info.get("tracks", [])
track_map = {t["name"]: t["index"] for t in tracks}

perc_idx = track_map.get("Hand Perc")
kick_idx = track_map.get("Kick")
rim_idx = track_map.get("Rim Perc")
bass_idx = track_map.get("Bass")

def copy_clip_down(t_idx):
    if t_idx is None: return
    try:
        conn.send_command("duplicate_clip", {
            "track_index": t_idx,
            "clip_index": 0,
            "destination_index": 1
        })
    except Exception as e:
        pass

copy_clip_down(perc_idx)
copy_clip_down(kick_idx)
copy_clip_down(rim_idx)

# Generate Bassline for Scene 2
print("\n=== GENERATING BASSLINE ===")
if bass_idx is not None:
    if generate_bassline_advanced_wrapper:
        generate_bassline_advanced_wrapper(
            track_index=bass_idx,
            clip_index=1,
            key="A",
            scale="minor",
            progression="i i VI V",
            style="syncopated"
        )
        print("Generated A Minor Bassline (i-i-VI-V)")
    else:
        print("Using basic pattern fallback due to import error")
        from mcp_tooling.generators import pattern_generator
        pattern_generator(
            track_index=bass_idx,
            clip_slot_index=1,
            pattern_type="breakbeat",
            bars=8,
            root_note=45, # A1
            velocity=100
        )

print("\n=== FIRING SCENE 2 ===")
conn.send_command("fire_scene", {"scene_index": 1})

print("\n✓ Scene 2 (Bass Entry) playing!")
