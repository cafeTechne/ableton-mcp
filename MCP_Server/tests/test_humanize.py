from mcp_tooling.humanization import HumanizeProfile, apply_humanization
from mcp_tooling.generators import finalize_notes

def test_humanization():
    print("Testing Humanization...")
    
    # 1. Create a simple grid note list
    notes = [
        {"pitch": 60, "start_time": 0.0, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 0.5, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 1.0, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 1.5, "duration": 0.25, "velocity": 100}
    ]
    
    # 2. Apply Swing
    print("Applying Swing...")
    profile = HumanizeProfile.get_preset("swing")
    # Force deterministic jitter for test? No, just check ranges.
    profile.timing_jitter = 0
    profile.velocity_range = 0
    apply_humanization(notes, profile)
    
    for n in notes:
        print(f"Start: {n['start_time']:.3f}, Vel: {n['velocity']}")
        
    # Check if 0.5 moved
    offbeat = notes[1]
    if offbeat["start_time"] > 0.5:
        print("PASS: Offbeat delayed (Swing working)")
    else:
        print("FAIL: Offbeat not delayed")

    # 3. Apply Velocity Map
    print("\nApplying Ska Velocity Map...")
    notes = [
        {"pitch": 60, "start_time": 0.0, "duration": 0.25, "velocity": 100},
        {"pitch": 60, "start_time": 0.5, "duration": 0.25, "velocity": 100}
    ]
    profile = HumanizeProfile.get_preset("ska")
    profile.timing_jitter = 0
    profile.velocity_range = 0
    apply_humanization(notes, profile)
    
    print(f"Downbeat Vel: {notes[0]['velocity']} (Expect < 100)")
    print(f"Offbeat Vel: {notes[1]['velocity']} (Expect > 100)")
    
    if notes[0]['velocity'] < 100 and notes[1]['velocity'] > 100:
        print("PASS: Ska velocity map applied")
    else:
        print("FAIL: Velocity map logic failed")

if __name__ == "__main__":
    test_humanization()
