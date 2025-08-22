"""Test markdown table parser."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from headless.parser import MarkdownTableParser
from headless.models import HeadlessConfig


def test_parse_single_table():
    """Test parsing a single markdown table."""
    print("Testing single table parsing...")
    
    table_text = """
| Header1 | Header2 | notes |
|---------|---------|-------|
| value1  | value2  | note1 |
| value3  | value4  | note2 |
"""
    
    rows = MarkdownTableParser.parse_table(table_text)
    
    assert len(rows) == 2, f"Expected 2 rows, got {len(rows)}"
    assert rows[0]["Header1"] == "value1", "First row first column incorrect"
    assert rows[1]["Header2"] == "value4", "Second row second column incorrect"
    assert "notes" not in rows[0], "Notes column should be removed"
    
    print("✓ Single table parsing test passed")
    return True


def test_find_table_sections():
    """Test finding different table sections in markdown."""
    print("Testing table section identification...")
    
    markdown = """
## Form Table

| Form label | value |
|------------|-------|
| actionNameToCreate | test |
| bpm | 120 |

## Dance Table

| poseCatalog | track | cycle mode |
|-------------|-------|------------|
| hips | drums | loop |

## Video Table

| Form label | value |
|------------|-------|
| audioFile | test.mp3 |
"""
    
    sections = MarkdownTableParser.find_table_sections(markdown)
    
    print(f"Found sections: {sections.keys()}")
    
    assert "form" in sections, "Should find form section"
    assert "dance" in sections, "Should find dance section"
    assert "video" in sections, "Should find video section"
    
    print("✓ Table section identification test passed")
    return True


def test_parse_form_table():
    """Test parsing form table specifically."""
    print("Testing form table parsing...")
    
    form_text = """
| Form label | value |
|------------|-------|
| actionNameToCreate | my_action |
| bpm | 96 |
| beatsPerBar | 4 |
| midiFile | test.mid |
"""
    
    form = MarkdownTableParser.parse_form_table(form_text)
    
    assert form.actionNameToCreate == "my_action", "Action name incorrect"
    assert form.bpm == 96.0, "BPM incorrect"
    assert form.beatsPerBar == 4, "Beats per bar incorrect"
    assert form.midiFile == "test.mid", "MIDI file incorrect"
    
    print("✓ Form table parsing test passed")
    return True


def test_parse_dance_table():
    """Test parsing dance table with defaults."""
    print("Testing dance table parsing...")
    
    dance_text = """
| poseCatalog | track | cycle mode | interpolation | preHold | postHold |
|-------------|-------|------------|---------------|---------|----------|
| hips | drums | random | back | 2 | 5 |
| hands | melody | | | | 3 |
"""
    
    dance = MarkdownTableParser.parse_dance_table(dance_text)
    
    assert len(dance.rows) == 2, "Should have 2 dance rows"
    
    # Check first row
    row1 = dance.rows[0]
    assert row1.poseCatalog == "hips", "First row catalog incorrect"
    assert row1.track == "drums", "First row track incorrect"
    assert row1.cycleMode == "random", "First row cycle mode incorrect"
    assert row1.interpolation == "back", "First row interpolation incorrect"
    assert row1.preHold == 2, "First row preHold incorrect"
    assert row1.postHold == 5, "First row postHold incorrect"
    
    # Check second row with defaults
    row2 = dance.rows[1]
    assert row2.poseCatalog == "hands", "Second row catalog incorrect"
    assert row2.cycleMode == "loop", "Second row should use default cycle mode"
    assert row2.interpolation == "cubic", "Second row should use default interpolation"
    assert row2.preHold == 8, "Second row should use default preHold"
    assert row2.postHold == 3, "Second row postHold incorrect"
    
    print("✓ Dance table parsing test passed")
    return True


def test_parse_complete_config():
    """Test parsing complete configuration."""
    print("Testing complete configuration parsing...")
    
    markdown = """
## Form Table

| Form label | value |
|------------|-------|
| actionNameToCreate | test_action |
| bpm | 120 |
| midiFile | test.mid |
| poseBlendFile | poses.blend |

## Dance Table  

| poseCatalog | track | cycle mode |
|-------------|-------|------------|
| hips | drums | loop |
| hands | melody | random |

## Video Table

| Form label | value |
|------------|-------|
| shouldCreateVideo? | yes |
| audioFile | audio.mp3 |
| renderDir | renders/ |
"""
    
    config = MarkdownTableParser.parse(markdown)
    
    assert isinstance(config, HeadlessConfig), "Should return HeadlessConfig"
    print(f"actionNameToCreate: '{config.form.actionNameToCreate}'")
    assert config.form.actionNameToCreate == "test_action", "Form parsing failed"
    assert len(config.dance.rows) == 2, "Dance parsing failed"
    assert config.form.shouldCreateVideo == True, "Video parsing failed"
    assert config.form.audioFile == "audio.mp3", "Audio file parsing failed"
    
    print("✓ Complete configuration parsing test passed")
    return True


def main():
    """Run all parser tests."""
    print("\n=== Testing Markdown Parser ===\n")
    
    tests = [
        test_parse_single_table,
        test_find_table_sections,
        test_parse_form_table,
        test_parse_dance_table,
        test_parse_complete_config
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
    
    print("\n✓ All parser tests passed!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)