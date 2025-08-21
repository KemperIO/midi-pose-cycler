from typing import Dict, List, Optional, Set
from dataclasses import dataclass
import sys
import os

# Ensure vendor mido is imported
def import_bundled_mido():
    """Import the bundled mido library"""
    import importlib.util
    import importlib
    
    # Check if mido is already imported and return it
    if 'mido' in sys.modules:
        return sys.modules['mido']
    
    # Get the path to our bundled mido (vendor is at root, not in src)
    # Use __file__ to get current module path
    try:
        current_file = __file__
    except NameError:
        # If __file__ is not defined, try to get it from the frame
        import inspect
        current_file = inspect.getfile(inspect.currentframe())
    
    current_dir = os.path.dirname(os.path.abspath(current_file))
    
    # Check multiple possible vendor locations
    vendor_candidates = [
        os.path.join(current_dir, 'vendor'),  # vendor in same dir as this file
        os.path.join(os.path.dirname(current_dir), 'vendor'),  # vendor in parent dir
    ]
    
    # Find the first existing vendor directory
    vendor_dir = None
    for candidate in vendor_candidates:
        if os.path.exists(os.path.join(candidate, 'mido', '__init__.py')):
            vendor_dir = candidate
            break
    
    if vendor_dir is None:
        # Fallback logic if vendor not found yet
        if current_dir.endswith('src'):
            # Development: vendor might be at ../vendor from src/
            parent_dir = os.path.dirname(current_dir)
            vendor_dir = os.path.join(parent_dir, 'vendor')
        elif 'midi-pose-cycler' in current_dir:
            # Installed addon: vendor is at midi-pose-cycler/vendor
            # Find the midi-pose-cycler directory
            parts = current_dir.split(os.sep)
            for i, part in enumerate(parts):
                if part == 'midi-pose-cycler':
                    addon_root = os.sep.join(parts[:i+1])
                    vendor_dir = os.path.join(addon_root, 'vendor')
                    break
            else:
                vendor_dir = os.path.join(current_dir, 'vendor')
        else:
            # Fallback: assume vendor is in same directory
            vendor_dir = os.path.join(current_dir, 'vendor')
    
    mido_path = os.path.join(vendor_dir, 'mido', '__init__.py')
    
    if not os.path.exists(mido_path):
        # Silently fail - mido might be installed globally
        return None
    
    # Add vendor to path first
    if vendor_dir not in sys.path:
        sys.path.insert(0, vendor_dir)
    
    try:
        # Try normal import first (in case it works)
        import mido
        return mido
    except ImportError:
        pass
        
    try:
        # Manually load the module if normal import fails
        spec = importlib.util.spec_from_file_location("mido", mido_path)
        if spec and spec.loader:
            mido = importlib.util.module_from_spec(spec)
            sys.modules['mido'] = mido
            spec.loader.exec_module(mido)
            return mido
    except Exception:
        # Silently fail - mido might be installed globally
        return None

# Try to import mido - reimport each time to ensure it's available
def get_mido():
    """Get mido module, importing if necessary"""
    global mido, MIDO_AVAILABLE
    if mido is None:
        mido = import_bundled_mido()
        MIDO_AVAILABLE = mido is not None
    return mido

# Initial import
mido = import_bundled_mido()
MIDO_AVAILABLE = mido is not None

@dataclass
class MidiTrackInfo:
    """Information about a MIDI track"""
    index: int
    name: str
    note_count: int
    notes: Dict[int, int]  # note number -> count
    channels: Set[int]
    first_note_time: Optional[float]
    last_note_time: Optional[float]

@dataclass  
class MidiAnalysis:
    """Complete MIDI file analysis"""
    file_path: str
    ticks_per_beat: int
    bpm: int
    tracks: List[MidiTrackInfo]

def midi_note_to_name(note: int) -> str:
    """Convert MIDI note number to musical notation"""
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (note // 12) - 1
    note_name = notes[note % 12]
    return f"{note_name}{octave}"

def analyze_midi_file(file_path: str) -> Optional[MidiAnalysis]:
    """Analyze a MIDI file and return track information"""
    # Try to get mido, reimporting if necessary
    mido_module = get_mido()
    if not mido_module:
        print("ERROR: mido library not available")
        return None
        
    try:
        mid = mido_module.MidiFile(file_path)
        print(f"Successfully loaded MIDI file: {file_path}")
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return None
    
    tempo = 500000  # Default tempo (microseconds per beat)
    bpm = 120  # Default BPM
    
    # Find tempo from first track
    for msg in mid.tracks[0]:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            bpm = int(60_000_000 / tempo)
            break
    
    # First collect all track data
    raw_tracks = []
    
    for i, track in enumerate(mid.tracks):
        track_name = f"Track {i}"
        notes_data = {}
        channels = set()
        elapsed_ticks = 0
        first_note_time = None
        last_note_time = None
        
        for msg in track:
            elapsed_ticks += msg.time
            
            if msg.type == 'track_name':
                track_name = msg.name
            elif msg.type == 'note_on' and msg.velocity > 0:
                note = msg.note
                notes_data[note] = notes_data.get(note, 0) + 1
                
                if hasattr(msg, 'channel'):
                    channels.add(msg.channel)
                
                time_seconds = (elapsed_ticks / mid.ticks_per_beat) * (tempo / 1_000_000)
                if first_note_time is None:
                    first_note_time = time_seconds
                last_note_time = time_seconds
        
        if notes_data:  # Only include tracks with notes
            raw_tracks.append({
                'index': i,
                'name': track_name,
                'notes': notes_data,
                'channels': channels,
                'first_note_time': first_note_time,
                'last_note_time': last_note_time
            })
    
    # Merge tracks with the same name
    merged_tracks = {}
    for track_data in raw_tracks:
        name = track_data['name']
        
        if name not in merged_tracks:
            # First track with this name
            merged_tracks[name] = track_data
        else:
            # Merge with existing track
            existing = merged_tracks[name]
            
            # Merge notes (sum counts)
            for note, count in track_data['notes'].items():
                existing['notes'][note] = existing['notes'].get(note, 0) + count
            
            # Merge channels
            existing['channels'].update(track_data['channels'])
            
            # Update time range
            if track_data['first_note_time'] is not None:
                if existing['first_note_time'] is None:
                    existing['first_note_time'] = track_data['first_note_time']
                else:
                    existing['first_note_time'] = min(existing['first_note_time'], track_data['first_note_time'])
            
            if track_data['last_note_time'] is not None:
                if existing['last_note_time'] is None:
                    existing['last_note_time'] = track_data['last_note_time']
                else:
                    existing['last_note_time'] = max(existing['last_note_time'], track_data['last_note_time'])
    
    # Convert to MidiTrackInfo objects
    tracks_info = []
    for name, data in merged_tracks.items():
        tracks_info.append(MidiTrackInfo(
            index=data['index'],  # Use first track's index
            name=name,
            note_count=sum(data['notes'].values()),
            notes=data['notes'],
            channels=data['channels'],
            first_note_time=data['first_note_time'],
            last_note_time=data['last_note_time']
        ))
    
    return MidiAnalysis(
        file_path=file_path,
        ticks_per_beat=mid.ticks_per_beat,
        bpm=bpm,
        tracks=tracks_info
    )

def get_note_events_for_track(file_path: str, track_name: str, target_notes: Optional[Set[int]], 
                            fps: int, max_frames: int) -> List[int]:
    """Extract frame timing of specific MIDI notes from a track"""
    # Try to get mido, reimporting if necessary
    mido_module = get_mido()
    if not mido_module:
        print("ERROR: mido not available in get_note_events_for_track")
        return []
        
    try:
        mid = mido_module.MidiFile(file_path)
        print(f"DEBUG: Loading MIDI for track extraction: {track_name}")
    except Exception as e:
        print(f"Error loading MIDI file: {e}")
        return []
    
    # Find tempo
    tempo = 500000
    for msg in mid.tracks[0]:
        if msg.type == 'set_tempo':
            tempo = msg.tempo
            break
    
    # Find ALL tracks with the specified name (to handle merged tracks)
    target_tracks = []
    for i, track in enumerate(mid.tracks):
        track_actual_name = None
        for msg in track:
            if msg.type == 'track_name':
                track_actual_name = msg.name
                break
        
        # If no track_name message, use default name
        if track_actual_name is None:
            track_actual_name = f"Track {i}"
        
        if track_actual_name == track_name:
            target_tracks.append(track)
            print(f"DEBUG: Found matching track at index {i}: {track_actual_name}")
    
    if not target_tracks:
        print(f"WARNING: No tracks found with name '{track_name}'")
        print("Available track names:")
        for i, track in enumerate(mid.tracks):
            track_name_found = f"Track {i}"
            for msg in track:
                if msg.type == 'track_name':
                    track_name_found = msg.name
                    break
            print(f"  - Index {i}: {track_name_found}")
        return []
    
    # Collect note events from all matching tracks
    note_frames = []
    max_seconds = max_frames / fps
    total_notes_found = 0
    filtered_notes = 0
    
    print(f"DEBUG: Processing {len(target_tracks)} track(s), max_seconds: {max_seconds:.2f}")
    if target_notes:
        print(f"DEBUG: Filtering for notes: {sorted(target_notes)}")
    
    for track_idx, track in enumerate(target_tracks):
        elapsed_ticks = 0
        track_notes = 0
        for msg in track:
            elapsed_ticks += msg.time
            time_seconds = (elapsed_ticks / mid.ticks_per_beat) * (tempo / 1_000_000)
            
            if time_seconds > max_seconds:
                continue
            
            if msg.type == 'note_on' and msg.velocity > 0:
                total_notes_found += 1
                if target_notes is None or msg.note in target_notes:
                    frame = int(time_seconds * fps)
                    note_frames.append(frame)
                    track_notes += 1
                else:
                    filtered_notes += 1
        
        print(f"DEBUG: Track {track_idx}: {track_notes} notes added to animation")
    
    print(f"DEBUG: Total notes found: {total_notes_found}, filtered out: {filtered_notes}, used: {len(note_frames)}")
    
    # Sort frames since we're merging from multiple tracks
    note_frames.sort()
    
    return note_frames