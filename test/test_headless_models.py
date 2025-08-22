"""Test headless models and validation."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from headless.models import FormTable, DanceTable, DanceRow, ValidationResult


def test_form_table_validation():
    """Test FormTable validation."""
    print("Testing FormTable validation...")
    
    # Test valid form
    form = FormTable(
        actionNameToCreate="test_action",
        bpm=120.0,
        beatsPerBar=4,
        blendFileToOutputAction="output.blend",
        poseBlendFile="poses.blend",
        poseCatalog="test_catalog",
        midiFile="test.mid"
    )
    
    results = form.validate()
    
    # Check required fields are validated
    has_action_check = any(r.field == "actionNameToCreate" for r in results)
    has_midi_check = any(r.field == "midiFile" for r in results)
    
    assert has_action_check, "Should validate action name"
    assert has_midi_check, "Should validate MIDI file"
    
    # Test invalid BPM
    form.bpm = -1
    results = form.validate()
    bpm_results = [r for r in results if r.field == "bpm"]
    assert len(bpm_results) > 0, "Should validate BPM"
    assert not bpm_results[0].valid, "Negative BPM should be invalid"
    
    print("✓ FormTable validation tests passed")
    return True


def test_dance_row_validation():
    """Test DanceRow validation."""
    print("Testing DanceRow validation...")
    
    # Test valid row
    row = DanceRow(
        poseCatalog="hips",
        track="drums",
        cycleMode="loop",
        interpolation="cubic",
        preHold=5,
        postHold=3
    )
    
    results = row.validate()
    all_valid = all(r.valid for r in results)
    assert all_valid, "Valid row should pass all validation"
    
    # Test invalid cycle mode
    row.cycleMode = "invalid_mode"
    results = row.validate()
    cycle_results = [r for r in results if "cycleMode" in r.field]
    assert len(cycle_results) > 0, "Should validate cycle mode"
    assert not cycle_results[0].valid, "Invalid cycle mode should fail"
    
    # Test invalid interpolation
    row.cycleMode = "loop"
    row.interpolation = "not_real"
    results = row.validate()
    interp_results = [r for r in results if "interpolation" in r.field]
    assert len(interp_results) > 0, "Should validate interpolation"
    assert not interp_results[0].valid, "Invalid interpolation should fail"
    
    print("✓ DanceRow validation tests passed")
    return True


def test_dance_table_validation():
    """Test DanceTable validation."""
    print("Testing DanceTable validation...")
    
    table = DanceTable()
    
    # Test empty table
    results = table.validate()
    assert len(results) > 0, "Empty table should have validation results"
    assert not results[0].valid, "Empty table should be invalid"
    
    # Add valid rows
    table.add_row(DanceRow("hips", "drums"))
    table.add_row(DanceRow("hands", "melody"))
    
    results = table.validate()
    all_valid = all(r.valid for r in results if "Row" in r.field)
    assert all_valid, "Valid rows should pass validation"
    
    # Test duplicate catalogs warning
    table.add_row(DanceRow("hips", "bass"))  # Duplicate catalog
    results = table.validate()
    duplicate_results = [r for r in results if "Duplicate" in r.message]
    assert len(duplicate_results) > 0, "Should warn about duplicate catalogs"
    
    print("✓ DanceTable validation tests passed")
    return True


def main():
    """Run all model tests."""
    print("\n=== Testing Headless Models ===\n")
    
    tests = [
        test_form_table_validation,
        test_dance_row_validation,
        test_dance_table_validation
    ]
    
    for test in tests:
        try:
            if not test():
                print(f"✗ {test.__name__} failed")
                return False
        except Exception as e:
            print(f"✗ {test.__name__} failed with error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n✓ All model tests passed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)