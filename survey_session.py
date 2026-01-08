"""
Survey Session State
List all tracks, devices, and clip status
"""
from mcp_tooling.connection import get_ableton_connection

conn = get_ableton_connection()

print("=== SESSION SURVEY ===")
info = conn.send_command("get_session_info", {})
tracks = info.get("tracks", [])
scenes = info.get("scenes", [])

print(f"Total Tracks: {len(tracks)}")
print(f"Total Scenes: {len(scenes)}")

for t in tracks:
    t_idx = t['index']
    t_name = t['name']
    
    # Get devices
    # Note: get_track_info returns device list
    t_info = conn.send_command("get_track_info", {"track_index": t_idx})
    devices = t_info.get("devices", [])
    dev_names = [d['name'] for d in devices]
    
    # Check clips
    clip_status = []
    for s_idx in range(len(scenes)):
        # Check if clip slot has clip
        # get_clip_info returns None if empty? No, it errors or returns loaded=False
        # simpler: check has_clip property if available?
        # Let's try get_clip_info for first 2 scenes
        try:
            c_info = conn.send_command("get_clip_info", {"track_index": t_idx, "clip_index": s_idx})
            if c_info:
                 clip_status.append(f"S{s_idx}:[x]")
            else:
                 clip_status.append(f"S{s_idx}:[ ]")
        except:
             clip_status.append(f"S{s_idx}:[ ]")

    print(f"Track {t_idx} '{t_name}': Devices={dev_names}, Clips={', '.join(clip_status)}")
    
print("======================")
