"""Test rhythmic comp patterns."""
from mcp_tooling.rhythmic_comp import get_comp_pattern, generate_comp_notes, list_comp_styles, COMP_PATTERNS

def test_patterns():
    print("Testing Rhythmic Comp Patterns...")
    print(f"\nAvailable styles: {list_comp_styles()}")
    
    # Test each pattern
    test_chord = [60, 64, 67]  # C major triad
    
    for style_name in list_comp_styles():
        pattern_data = get_comp_pattern(style_name)
        pattern = pattern_data["pattern"]
        
        # Generate notes for one bar
        notes = generate_comp_notes(
            chord_notes=test_chord,
            pattern=pattern,
            bar_offset=0.0,
            base_velocity=80
        )
        
        num_hits = len(pattern)
        num_notes = len(notes)  # num_hits * len(chord)
        
        print(f"\n{style_name}:")
        print(f"  Description: {pattern_data.get('description', 'N/A')}")
        print(f"  Hits per bar: {num_hits}")
        print(f"  Notes generated: {num_notes} (expected {num_hits * len(test_chord)})")
        print(f"  Groove: {pattern_data.get('humanize_profile', 'straight')}")
        
        # Show first few notes
        if notes:
            print(f"  First note: t={notes[0]['start_time']:.2f}, dur={notes[0]['duration']:.2f}, vel={notes[0]['velocity']}")

    print("\n" + "="*50)
    print("All patterns loaded successfully!")

if __name__ == "__main__":
    test_patterns()
