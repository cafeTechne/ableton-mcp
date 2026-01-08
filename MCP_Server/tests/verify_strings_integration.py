
import sys
import os
import json

sys.path.append(os.getcwd())

from mcp_tooling.strings.section import SectionConductor

def verify_strings_integration():
    print("Verifying Strings Integration...")
    
    # Test 1: Pop Style (Should contain legato, lead/bass roles)
    print("\n[Test 1] Pop Style (Pad/Legato)")
    conductor = SectionConductor("pop")
    chord = [60, 64, 67, 71] # C Maj 7
    notes = conductor.get_notes(chord, 0.0, 4.0, 100)
    
    if not notes:
        print("FAIL: No notes generated")
        return

    sample = notes[0]
    print(f"Keys present: {list(sample.keys())}")
    
    if "_section" in sample and sample["_section"] == "strings":
        print("SUCCESS: _section injected")
    else:
        print(f"FAIL: _section missing or wrong: {sample.get('_section')}")
        
    if "_articulation" in sample:
        print(f"Articulation: {sample['_articulation']}")
        if sample["_articulation"] == "legato":
             print("SUCCESS: Articulation mapped to legato")
    else:
         print("FAIL: _articulation missing")
         
    if "velocity_deviation" in sample:
        print("SUCCESS: Performance Humanizer ran (found velocity_deviation)")
        
    # Check Roles
    vl1 = next((n for n in notes if n["_part"] == "vl1"), None)
    vc = next((n for n in notes if n["_part"] == "vc"), None)
    
    if vl1 and vl1["_role"] == "lead":
        print("SUCCESS: vl1 role = lead")
    if vc and vc["_role"] == "bass":
        print("SUCCESS: vc role = bass")
        
    # Test 2: Disco Style (Should contain spicc/stab)
    print("\n[Test 2] Disco Style (Stab/Spicc)")
    conductor_disco = SectionConductor("disco")
    notes_disco = conductor_disco.get_notes(chord, 0.0, 4.0, 100)
    
    if notes_disco:
         sample_disco = notes_disco[0]
         print(f"Disco Articulation: {sample_disco['_articulation']}")
         if sample_disco["_articulation"] == "spicc":
              print("SUCCESS: Articulation mapped to spicc for Disco")

if __name__ == "__main__":
    verify_strings_integration()
