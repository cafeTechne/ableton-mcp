
import sys
import os
import json

sys.path.append(os.getcwd())

from mcp_tooling.woodwinds.section import WoodwindConductor

def verify_woodwinds_integration():
    print("Verifying Woodwinds Integration...")
    
    # Test 1: Pop Style (Should be legato)
    print("\n[Test 1] Pop Style")
    conductor = WoodwindConductor("pop")
    chord = [60, 64, 67, 71]
    notes = conductor.get_notes(chord, 0.0, 4.0, 100)
    
    if not notes:
        print("FAIL: No notes generated")
        return

    sample = notes[0]
    
    if "_section" in sample and sample["_section"] == "woodwinds":
        print("SUCCESS: _section injected")
        
    if "_articulation" in sample:
        print(f"Articulation: {sample['_articulation']}")
        if sample["_articulation"] == "legato":
             print("SUCCESS: Articulation mapped to legato")
             
    if "velocity_deviation" in sample:
        print("SUCCESS: Performance Humanizer ran")
        
    # Test 2: Reggae Style (Should be stab)
    print("\n[Test 2] Reggae Style")
    conductor_reggae = WoodwindConductor("reggae")
    notes_reggae = conductor_reggae.get_notes(chord, 0.0, 4.0, 100)
    
    if notes_reggae:
         sample_reggae = notes_reggae[0]
         print(f"Reggae Articulation: {sample_reggae['_articulation']}")
         if sample_reggae["_articulation"] == "stab":
              print("SUCCESS: Articulation mapped to stab for Reggae")

if __name__ == "__main__":
    verify_woodwinds_integration()
