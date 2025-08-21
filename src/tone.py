"""
Tone class for MIDI note representation
"""
from typing import Dict

class Tone:
    """Represents a MIDI tone with value and human-readable name"""
    
    # Static map for note names
    NOTE_NAMES: Dict[int, str] = {
        0: 'C', 1: 'C#', 2: 'D', 3: 'D#', 
        4: 'E', 5: 'F', 6: 'F#', 7: 'G', 
        8: 'G#', 9: 'A', 10: 'A#', 11: 'B'
    }
    
    def __init__(self, midi_value: int):
        """Initialize with MIDI value (0-127)"""
        if not 0 <= midi_value <= 127:
            raise ValueError(f"MIDI value must be 0-127, got {midi_value}")
        self.value = midi_value
    
    @property
    def name(self) -> str:
        """Get human-readable name (e.g., 'C3', 'D#4')"""
        note = self.NOTE_NAMES[self.value % 12]
        octave = (self.value // 12) - 1
        return f"{note}{octave}"
    
    def __str__(self) -> str:
        """String representation: 'C3 (60)'"""
        return f"{self.name} ({self.value})"
    
    def __repr__(self) -> str:
        """Developer representation"""
        return f"Tone({self.value})"
    
    def __eq__(self, other) -> bool:
        """Equality based on MIDI value"""
        if isinstance(other, Tone):
            return self.value == other.value
        return False
    
    def __lt__(self, other) -> bool:
        """Less than for sorting"""
        if isinstance(other, Tone):
            return self.value < other.value
        return NotImplemented
    
    def __hash__(self) -> int:
        """Hash for use in sets/dicts"""
        return hash(self.value)
    
    @staticmethod
    def from_name(name: str) -> 'Tone':
        """Create Tone from name like 'C3' or 'D#4'
        
        Args:
            name: Note name with octave (e.g., 'C3', 'D#4', 'Bb2')
            
        Returns:
            Tone instance
        """
        # Handle flats by converting to sharps
        flat_to_sharp = {
            'Cb': 'B', 'Db': 'C#', 'Eb': 'D#', 
            'Fb': 'E', 'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#'
        }
        for flat, sharp in flat_to_sharp.items():
            if name.startswith(flat):
                name = name.replace(flat, sharp, 1)
                break
        
        # Parse note and octave
        if '#' in name:
            note_str = name[:2]
            octave_str = name[2:]
        else:
            note_str = name[0]
            octave_str = name[1:]
        
        # Find note index
        note_map = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3,
            'E': 4, 'F': 5, 'F#': 6, 'G': 7,
            'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        
        if note_str not in note_map:
            raise ValueError(f"Invalid note: {note_str}")
        
        try:
            octave = int(octave_str)
        except ValueError:
            raise ValueError(f"Invalid octave: {octave_str}")
        
        # Calculate MIDI value
        midi_value = (octave + 1) * 12 + note_map[note_str]
        
        if not 0 <= midi_value <= 127:
            raise ValueError(f"Note {name} is out of MIDI range")
        
        return Tone(midi_value)