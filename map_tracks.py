"""
Track Mapper
Iterate indices to find names since get_song_context is failing
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

print("=== TRACK MAPPER ===")
track_map = {}

for i in range(20):
    try:
        info = conn.send_command("get_track_info", {"track_index": i})
        name = info.get("name")
        if name:
            print(f"[{i}] {name}")
            track_map[name] = i
            
            # Check Clip Slot 1
            clip = conn.send_command("get_clip_info", {"track_index": i, "clip_index": 1})
            if clip:
                print(f"    Scene 1 Clip: {clip.get('name', 'Untitled')} (Playing: {clip.get('is_playing')})")
            else:
                print(f"    Scene 1 Clip: [EMPTY]")
                
    except Exception as e:
        # Likely index out of range or error
        # print(f"[{i}] Error: {e}")
        pass

print("====================")
