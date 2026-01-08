from mcp_tooling.automation import generate_cc_envelope

def test_cc_envelope():
    print("Testing CC Envelope Generation...")
    
    # Test Swell
    print("\n1. Swell Curve (4 beats):")
    envelope = generate_cc_envelope(4.0, curve_type="swell", start_value=0, end_value=127)
    print(f"Generated {len(envelope)} points.")
    print(f"First: {envelope[0]}, Mid: {envelope[len(envelope)//2]}, Last: {envelope[-1]}")
    
    # Validate swell (mid should be > start and end)
    mid_val = envelope[len(envelope)//2][1]
    if mid_val > envelope[0][1] and mid_val >= envelope[-1][1]:
        print("PASS: Swell curve peaks in middle.")
    else:
        print("FAIL: Swell curve incorrect shape.")
    
    # Test Fade In
    print("\n2. Fade In Curve:")
    envelope = generate_cc_envelope(4.0, curve_type="fade_in", start_value=0, end_value=127)
    if envelope[0][1] < envelope[-1][1]:
        print("PASS: Fade in ramps up.")
    else:
        print("FAIL: Fade in not ramping.")
        
    # Test Attack Release
    print("\n3. Attack/Release Curve:")
    envelope = generate_cc_envelope(8.0, curve_type="attack_release", start_value=20, end_value=127, attack_pct=0.2, release_pct=0.2)
    print(f"First: {envelope[0]}, Mid: {envelope[len(envelope)//2]}, Last: {envelope[-1]}")
    if envelope[len(envelope)//2][1] > envelope[0][1] and envelope[len(envelope)//2][1] > envelope[-1][1]:
        print("PASS: Attack/Release sustains in middle.")
    else:
        print("FAIL: Attack/Release shape wrong.")

if __name__ == "__main__":
    test_cc_envelope()
