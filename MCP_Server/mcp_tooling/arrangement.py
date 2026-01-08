import json
import logging
from typing import Optional
from .constants import GENRE_TEMPLATES
from .connection import get_ableton_connection
from .util import resolve_uri_by_name
from .generators import generate_chord_progression_advanced, generate_bassline_advanced_wrapper, add_basic_drum_pattern

logger = logging.getLogger("mcp_server.arrangement")

def create_song_blueprint(genre: str = "pop", key: str = "C", scale: str = "major") -> str:
    """
    Generate a song blueprint (JSON) for a given genre.
    Returns a JSON string describing tracks and scenes.
    """
    template = GENRE_TEMPLATES.get(genre.lower(), GENRE_TEMPLATES["pop"])
    
    blueprint = {
        "genre": genre,
        "key": key,
        "scale": scale,
        "tracks": template["tracks"],
        "scenes": []
    }
    
    for section_name in template["structure"]:
        prog = template["progression_map"].get(section_name, "pop_1")
        scene = {
            "name": section_name,
            "clips": []
        }
        
        # Populate clips for each track
        for track in template["tracks"]:
            clip_def = {
                "track_name": track["name"],
                "type": track["type"],
                "progression": prog,
                "bars": 4 # Standard length
            }
            scene["clips"].append(clip_def)
            
        blueprint["scenes"].append(scene)
        
    return json.dumps(blueprint, indent=2)

def construct_song(blueprint_json: str) -> str:
    """
    Construct a song from a blueprint JSON string.
    Creates tracks, loads instruments, creates scenes, and populates clips.
    """
    try:
        plan = json.loads(blueprint_json)
        ableton = get_ableton_connection()
        
        genre = plan.get("genre", "pop")
        key = plan.get("key", "C")
        scale = plan.get("scale", "major")
        
        # 1. Setup Tracks
        track_map = {} # name -> index
        # Use get_song_context instead of deprecated get_session_info
        context = ableton.send_command("get_song_context", {"include_clips": False})
        start_track = len(context.get("tracks", []))
        
        created_tracks_log = []
        
        for i, track_def in enumerate(plan["tracks"]):
            t_idx = start_track + i
            ableton.send_command("create_midi_track", {"index": t_idx})
            ableton.send_command("set_track_name", {"track_index": t_idx, "name": track_def["name"]})
            track_map[track_def["name"]] = t_idx
            
            # Load Instrument
            inst = track_def.get("instrument")
            if inst:
                 uri = resolve_uri_by_name(inst, "instruments") or resolve_uri_by_name(inst, "sounds") or resolve_uri_by_name(inst, "drums")
                 if uri:
                     ableton.send_command("load_device", {"track_index": t_idx, "device_uri": uri})
                     created_tracks_log.append(f"Track {t_idx} '{track_def['name']}': Loaded {inst}")
                 else:
                     created_tracks_log.append(f"Track {t_idx} '{track_def['name']}': Instrument '{inst}' not found")
        
        # 2. Setup Scenes & Clips
        created_scenes_log = []
        start_scene = len(context.get("scenes", []))
        
        for i, scene_def in enumerate(plan["scenes"]):
            s_idx = start_scene + i
            # Create scene with name
            ableton.send_command("create_scene", {"index": s_idx, "name": scene_def["name"]}) 
            
            # 3. Generate Content
            for clip_def in scene_def["clips"]:
                t_name = clip_def["track_name"]
                t_idx = track_map.get(t_name)
                if t_idx is None: continue
                
                ctype = clip_def.get("type")
                prog = clip_def.get("progression")
                
                if ctype == "chords":
                    generate_chord_progression_advanced(
                        track_index=t_idx, clip_index=s_idx, 
                        key=key, scale=scale, progression=prog
                    )
                elif ctype == "bass":
                    # Use walking bass for Jazz/Shuffle contexts if hinted
                    style = "walking" if genre == "jazz" or "fifties" in genre else "pulse"
                    generate_bassline_advanced_wrapper(
                        track_index=t_idx, clip_index=s_idx,
                        key=key, scale=scale, progression=prog, style=style
                    )
                elif ctype == "drums":
                    style = "four_on_floor"
                    if genre == "jazz": style = "rock_basic" # Placeholder for jazz drums
                    add_basic_drum_pattern(t_idx, s_idx, 4.0, 100, style)
                    
            created_scenes_log.append(f"Scene {s_idx} '{scene_def['name']}' populated.")

        return f"Song Constructed!\nTracks: {len(track_map)}\nScenes: {len(plan['scenes'])}\n\nLog:\n" + "\n".join(created_tracks_log + created_scenes_log)

    except Exception as e:
        logger.error(f"Error constructing song: {e}")
        return f"Error: {e}"
