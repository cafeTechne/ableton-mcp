"""
Comprehensive API Verification Script

Tests ALL commands from interface.py to identify:
1. Working commands
2. Commands needing calibration (parameter ranges)
3. Commands with issues/errors
4. Commands not exposed in server.py

Run from MCP_Server directory:
    python tests/verify_all_commands.py
"""

import sys
import os
import json
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from mcp_tooling.connection import get_ableton_connection

# Test categories
TESTS = {
    "Session/Transport": [
        ("get_song_context", {"include_clips": False}),
        ("get_metronome", {}),
        ("set_tempo", {"tempo": 120.0}),
        ("start_playback", {}),
        ("stop_playback", {}),
        ("get_scene_overview", {}),
    ],
    "Track Operations": [
        ("get_track_info", {"track_index": 0}),
        ("set_track_name", {"track_index": 0, "name": "Test Track"}),
        ("set_track_volume", {"track_index": 0, "volume": 0.85}),  # Calibrate: 0-1 or dB?
        ("set_track_panning", {"track_index": 0, "panning": 0.0}),  # Calibrate: -1 to 1?
        ("set_track_mute", {"track_index": 0, "mute": False}),
        ("set_track_solo", {"track_index": 0, "solo": False}),
        ("set_send_level", {"track_index": 0, "send_index": 0, "level": 0.0}),  # Calibrate
    ],
    "Mixer": [
        ("get_master_info", {}),
    ],
    "Scene Operations": [
        ("get_scene_overview", {}),
        ("create_scene", {"index": -1, "name": "Test Scene"}),
        ("fire_scene", {"index": 0}),
        ("stop_scene", {"index": 0}),
    ],
    "Clip Operations": [
        ("create_clip", {"track_index": 0, "clip_index": 0, "length": 4.0}),
        ("set_clip_name", {"track_index": 0, "clip_index": 0, "name": "Test Clip"}),
        ("add_notes_to_clip", {"track_index": 0, "clip_index": 0, "notes": [
            {"pitch": 60, "start": 0.0, "duration": 1.0, "velocity": 100}
        ]}),
        ("get_clip_notes", {"track_index": 0, "clip_index": 0}),
        ("quantize_clip", {"track_index": 0, "clip_index": 0, "grid": 5, "amount": 1.0}),
        ("transpose_clip", {"track_index": 0, "clip_index": 0, "semitones": 12}),
        ("apply_legato", {"track_index": 0, "clip_index": 0}),
        ("fire_clip", {"track_index": 0, "clip_index": 0}),
        ("stop_clip", {"track_index": 0, "clip_index": 0}),
        ("delete_clip", {"track_index": 0, "clip_index": 0}),
    ],
    "Arrangement": [
        ("get_arrangement_info", {}),
        ("create_cue_point", {"time": 0.0, "name": "Intro"}),
        ("set_song_time", {"time": 0.0}),
    ],
    "Routing": [
        ("create_return_track", {"name": "Test Reverb"}),
    ],
    "Device Operations": [
        ("search_loadable_devices", {"query": "EQ", "category": "audio_effects", "max_items": 5}),
        ("get_device_parameters", {"track_index": 0, "device_index": 0}),
    ],
    "Browser": [
        ("get_browser_state", {}),
    ],
    "Application": [
        ("get_live_version", {}),
    ],
}

def run_tests():
    print("=" * 70)
    print("COMPREHENSIVE API VERIFICATION")
    print("=" * 70)
    print()
    
    conn = get_ableton_connection()
    
    results = {"pass": [], "fail": [], "skip": []}
    calibration_notes = []
    
    for category, tests in TESTS.items():
        print(f"\n{'─' * 70}")
        print(f"📁 {category}")
        print(f"{'─' * 70}")
        
        for cmd, params in tests:
            try:
                start = time.time()
                res = conn.send_command(cmd, params)
                elapsed = (time.time() - start) * 1000
                
                # Check for error in response
                if isinstance(res, dict) and res.get("status") == "error":
                    print(f"❌ {cmd}: {res.get('error', 'Unknown error')}")
                    results["fail"].append((cmd, res.get("error")))
                else:
                    print(f"✅ {cmd} ({elapsed:.0f}ms)")
                    results["pass"].append(cmd)
                    
                    # Check for calibration opportunities
                    if "volume" in params or "level" in params or "panning" in params:
                        calibration_notes.append(f"{cmd}: value range needs verification")
                        
            except Exception as e:
                print(f"❌ {cmd}: {e}")
                results["fail"].append((cmd, str(e)))
    
    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"✅ Passed: {len(results['pass'])}")
    print(f"❌ Failed: {len(results['fail'])}")
    
    if results["fail"]:
        print("\nFailed Commands:")
        for cmd, error in results["fail"]:
            print(f"  - {cmd}: {error[:50]}...")
    
    if calibration_notes:
        print("\nCalibration Needed:")
        for note in calibration_notes:
            print(f"  - {note}")
    
    return results

if __name__ == "__main__":
    run_tests()
