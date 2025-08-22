"""Integration test for headless MIDI pose cycler."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from headless.parser import MarkdownTableParser
from headless.models import HeadlessConfig


def test_parse_example_input():
    """Test parsing the example input file."""
    print("Testing example input parsing...")
    
    # Read example input
    input_path = Path(__file__).parent / "example_input.md"
    if not input_path.exists():
        print(f"✗ Example input file not found: {input_path}")
        return False
    
    markdown = input_path.read_text()
    
    # Parse configuration
    try:
        config = MarkdownTableParser.parse(markdown)
    except Exception as e:
        print(f"✗ Failed to parse example input: {e}")
        return False
    
    # Validate configuration
    is_valid = config.print_validation_table()
    
    # Check expected values
    assert config.form.actionNameToCreate == "integration-test-04", "Action name mismatch"
    assert config.form.bpm == 96.0, "BPM mismatch"
    assert len(config.dance.rows) == 4, "Should have 4 dance rows"
    
    # Check dance rows
    assert config.dance.rows[0].poseCatalog == "hips", "First row catalog mismatch"
    assert config.dance.rows[0].cycleMode == "random", "First row cycle mode mismatch"
    assert config.dance.rows[1].preHold == 8, "Second row should use default preHold"
    assert config.dance.rows[2].cycleMode == "pitch_follow", "Third row cycle mode mismatch"
    
    print("✓ Example input parsed successfully")
    return True


def test_validate_only_mode():
    """Test the validate-only mode."""
    print("Testing validate-only mode...")
    
    # Create a simple test input
    test_markdown = """
## Form Table

| Form label | value |
|------------|-------|
| actionNameToCreate | test |
| midiFile | nonexistent.mid |

## Dance Table

| poseCatalog | track |
|-------------|-------|
| test | drums |
"""
    
    config = MarkdownTableParser.parse(test_markdown)
    results = config.validate()
    
    # Should have validation errors for missing files
    has_midi_error = any("not found" in r.message.lower() for r in results if r.field == "midiFile")
    assert has_midi_error, "Should detect missing MIDI file"
    
    print("✓ Validate-only mode works correctly")
    return True


def test_default_values():
    """Test that default values are applied correctly."""
    print("Testing default values...")
    
    test_markdown = """
## Form Table

| Form label | value |
|------------|-------|
| actionNameToCreate | test |
| midiFile | test.mid |

## Dance Table

| poseCatalog | track |
|-------------|-------|
| test | drums |
"""
    
    config = MarkdownTableParser.parse(test_markdown)
    
    # Check form defaults
    assert config.form.bpm == 120.0, f"Default BPM should be 120, got {config.form.bpm}"
    assert config.form.beatsPerBar == 4, f"Default beats per bar should be 4, got {config.form.beatsPerBar}"
    
    # Check dance row defaults
    row = config.dance.rows[0]
    assert row.cycleMode == "loop", f"Default cycle mode should be 'loop', got {row.cycleMode}"
    assert row.interpolation == "cubic", f"Default interpolation should be 'cubic', got {row.interpolation}"
    assert row.preHold == 8, f"Default preHold should be 8, got {row.preHold}"
    assert row.postHold == 2, f"Default postHold should be 2, got {row.postHold}"
    
    print("✓ Default values applied correctly")
    return True


def main():
    """Run all integration tests."""
    print("\n=== Headless Integration Tests ===\n")
    
    tests = [
        test_parse_example_input,
        test_validate_only_mode,
        test_default_values
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
    
    print("\n✓ All integration tests passed!")
    print("\nNote: Full Blender integration test requires running within Blender:")
    print("  blender --background --python mpc_headless.py -- test/example_input.md --validate-only")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)