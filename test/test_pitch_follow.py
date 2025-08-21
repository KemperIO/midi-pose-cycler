"""Test pitch follow mapper functionality"""
import sys
import os

# Add src to path
src_dir = os.path.join(os.path.dirname(__file__), '..', 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from tone import Tone
from pitch_follow_mapper import PitchFollowMapper

def test_basic_mapping():
    """Test basic pitch to pose mapping"""
    print("\n=== Testing Basic Mapping ===")
    
    # Create mapper with C2 to C4 range
    lowest = Tone.from_name('C2')
    highest = Tone.from_name('C4')
    mapper = PitchFollowMapper(lowest, highest)
    
    # Test with 5 poses
    tones = [
        Tone.from_name('C2'),   # Lowest -> 0
        Tone.from_name('C3'),   # Middle -> 2
        Tone.from_name('C4'),   # Highest -> 4
    ]
    
    result = mapper.map(tones, 5)
    expected = [0, 2, 4]
    
    print(f"Tones: {[str(t) for t in tones]}")
    print(f"Result: {result}")
    print(f"Expected: {expected}")
    
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Basic mapping works")
    return True

def test_bounce_out():
    """Test bounce_out logic for repeated notes"""
    print("\n=== Testing Bounce Out ===")
    
    # Create mapper
    lowest = Tone.from_name('C2')
    highest = Tone.from_name('C4')
    mapper = PitchFollowMapper(lowest, highest)
    
    # Test case from requirements: [C2, C3, C4, C4, C4] with 5 poses
    tones = [
        Tone.from_name('C2'),   # -> 0
        Tone.from_name('C3'),   # -> 2
        Tone.from_name('C4'),   # -> 4
        Tone.from_name('C4'),   # -> 3 (bounce_out from 4)
        Tone.from_name('C4'),   # -> 4 (different from 3)
    ]
    
    result = mapper.map(tones, 5)
    expected = [0, 2, 4, 3, 4]
    
    print(f"Tones: {[t.name for t in tones]}")
    print(f"Result: {result}")
    print(f"Expected: {expected}")
    
    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ Bounce out works correctly")
    return True

def test_no_consecutive_duplicates():
    """Test that result never has consecutive duplicates"""
    print("\n=== Testing No Consecutive Duplicates ===")
    
    lowest = Tone.from_name('C2')
    highest = Tone.from_name('G4')
    mapper = PitchFollowMapper(lowest, highest)
    
    # Create a sequence with many repeated notes
    tones = []
    for _ in range(3):
        tones.extend([
            Tone.from_name('C2'),
            Tone.from_name('C2'),
            Tone.from_name('E3'),
            Tone.from_name('E3'),
            Tone.from_name('E3'),
            Tone.from_name('G4'),
            Tone.from_name('G4'),
        ])
    
    result = mapper.map(tones, 7)
    
    # Check no consecutive duplicates
    for i in range(1, len(result)):
        if result[i] == result[i-1]:
            print(f"✗ Found consecutive duplicates at index {i-1},{i}: {result[i-1]},{result[i]}")
            print(f"Full result: {result}")
            return False
    
    print(f"Mapped {len(tones)} tones to poses")
    print(f"Sample result: {result[:10]}...")
    print("✓ No consecutive duplicates found")
    return True

def test_edge_cases():
    """Test edge cases"""
    print("\n=== Testing Edge Cases ===")
    
    lowest = Tone(60)  # C4
    highest = Tone(72)  # C5
    mapper = PitchFollowMapper(lowest, highest)
    
    # Test with minimum poses (2)
    tones = [Tone(60), Tone(72), Tone(60), Tone(60)]
    result = mapper.map(tones, 2)
    print(f"2 poses result: {result}")
    
    # Should bounce between 0 and 1
    assert result == [0, 1, 0, 1], f"Expected alternating with 2 poses"
    print("✓ Works with 2 poses")
    
    # Test error with 1 pose
    try:
        mapper.map(tones, 1)
        print("✗ Should have raised error for 1 pose")
        return False
    except ValueError as e:
        print(f"✓ Correctly raised error for 1 pose: {e}")
    
    # Test empty tones
    result = mapper.map([], 5)
    assert result == [], "Empty tones should return empty list"
    print("✓ Empty tones handled")
    
    return True

def test_tone_class():
    """Test Tone class functionality"""
    print("\n=== Testing Tone Class ===")
    
    # Test creation and properties
    tone = Tone(60)
    assert tone.value == 60
    assert tone.name == "C4"
    assert str(tone) == "C4 (60)"
    print(f"✓ Tone(60) = {tone}")
    
    # Test from_name
    tone2 = Tone.from_name("C4")
    assert tone2.value == 60
    assert tone == tone2
    print(f"✓ from_name('C4') = {tone2}")
    
    # Test sharps and flats
    sharp = Tone.from_name("C#4")
    assert sharp.value == 61
    print(f"✓ C#4 = {sharp}")
    
    flat = Tone.from_name("Db4") 
    assert flat.value == 61  # Converts to sharp
    print(f"✓ Db4 converts to C#4 = {flat}")
    
    # Test comparison
    assert Tone(60) < Tone(61)
    assert Tone(60) == Tone(60)
    print("✓ Comparison operators work")
    
    return True

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("Testing Pitch Follow Mapper")
    print("="*60)
    
    tests = [
        test_tone_class,
        test_basic_mapping,
        test_bounce_out,
        test_no_consecutive_duplicates,
        test_edge_cases,
    ]
    
    for test in tests:
        if not test():
            print(f"\n✗ Test {test.__name__} failed")
            return False
    
    print("\n" + "="*60)
    print("✓ All pitch follow tests passed!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)