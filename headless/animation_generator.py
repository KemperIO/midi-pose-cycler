"""Animation generator for headless MIDI pose cycler."""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Add vendor path for mido
vendor_path = Path(__file__).parent.parent / "src" / "vendor"
if str(vendor_path) not in sys.path:
    sys.path.insert(0, str(vendor_path))

try:
    import mido
except ImportError:
    mido = None

from .models import HeadlessConfig, DanceRow
from .const import MIN_FORCED_TRANSITION_FRAMES, DEFAULT_FPS


@dataclass
class MidiEvent:
    """Represents a MIDI note event."""
    time: float  # Time in seconds
    frame: int   # Frame number
    note: int    # MIDI note number
    velocity: int


@dataclass
class PoseKeyframe:
    """Represents a pose keyframe to be created."""
    frame: int
    pose_name: str
    interpolation: str
    pre_hold: int
    post_hold: int


class AnimationGenerator:
    """Generate animations from MIDI and pose data."""
    
    def __init__(self, config: HeadlessConfig):
        self.config = config
        self.fps = DEFAULT_FPS
        self.frames_per_beat = (60.0 / config.form.bpm) * self.fps
        
        # Import bpy only when needed (in Blender context)
        try:
            import bpy
            self.bpy = bpy
        except ImportError:
            self.bpy = None
        
    def load_midi_tracks(self) -> Dict[str, List[MidiEvent]]:
        """Load and parse MIDI file, returning tracks with events."""
        tracks = {}
        
        if not mido:
            print("Warning: mido library not available for MIDI parsing")
            return tracks
        
        try:
            mid = mido.MidiFile(self.config.form.midiFile)
            
            # Process each track
            for track_idx, track in enumerate(mid.tracks):
                track_name = track.name if track.name else f"Track_{track_idx}"
                events = []
                current_time = 0
                
                for msg in track:
                    current_time += msg.time
                    if msg.type == 'note_on' and msg.velocity > 0:
                        time_seconds = mido.tick2second(
                            current_time, mid.ticks_per_beat, 
                            mido.bpm2tempo(self.config.form.bpm)
                        )
                        frame = int(time_seconds * self.fps) + 1
                        
                        events.append(MidiEvent(
                            time=time_seconds,
                            frame=frame,
                            note=msg.note,
                            velocity=msg.velocity
                        ))
                
                if events:
                    tracks[track_name] = events
                    
        except Exception as e:
            print(f"Error loading MIDI file: {e}")
            
        return tracks
    
    def get_poses_for_catalog(self, catalog_name: str, blend_file: str) -> List[str]:
        """Get poses from a catalog in the blend file."""
        if not self.bpy:
            return []
            
        poses = []
        
        # Read the catalog file to get catalog ID mapping
        catalog_file = Path(blend_file).parent / "blender_assets.cats.txt"
        catalog_id = None
        
        if catalog_file.exists():
            with open(catalog_file, 'r') as f:
                for line in f:
                    if line.strip() and not line.startswith('#'):
                        parts = line.strip().split(':')
                        if len(parts) >= 3 and parts[2] == catalog_name:
                            catalog_id = parts[0]
                            break
        
        # Link the blend file to access its data
        with self.bpy.data.libraries.load(blend_file, link=False) as (data_from, data_to):
            # Load all actions to check their catalog IDs
            data_to.actions = list(data_from.actions)
        
        # Find actions belonging to this catalog
        for action in self.bpy.data.actions:
            # Check if action has asset data with matching catalog ID
            if hasattr(action, 'asset_data') and action.asset_data:
                if catalog_id and str(action.asset_data.catalog_id) == catalog_id:
                    poses.append(action.name)
            # Also try name-based matching as fallback
            elif catalog_name.lower() in action.name.lower():
                poses.append(action.name)
        
        # Sort alphabetically as specified
        poses.sort()
        return poses
    
    def cycle_poses(self, poses: List[str], num_events: int, 
                   cycle_mode: str) -> List[str]:
        """Generate pose sequence based on cycle mode."""
        if not poses:
            return []
        
        result = []
        cycle_mode = cycle_mode.lower().replace(" ", "_")
        
        if cycle_mode == "loop":
            for i in range(num_events):
                result.append(poses[i % len(poses)])
                
        elif cycle_mode == "random":
            import random
            for _ in range(num_events):
                result.append(random.choice(poses))
                
        elif cycle_mode == "boomerang":
            sequence = poses + poses[-2:0:-1]  # Forward then backward
            for i in range(num_events):
                result.append(sequence[i % len(sequence)])
                
        elif cycle_mode == "pitch_follow":
            # This would need tone data from MIDI events
            # For now, use loop as fallback
            for i in range(num_events):
                result.append(poses[i % len(poses)])
        
        else:
            # Default to loop
            for i in range(num_events):
                result.append(poses[i % len(poses)])
        
        return result
    
    def calculate_keyframes(self, events: List[MidiEvent], poses: List[str],
                          dance_row: DanceRow) -> List[PoseKeyframe]:
        """Calculate keyframe positions with pre/post hold logic."""
        keyframes = []
        
        for i, (event, pose) in enumerate(zip(events, poses)):
            # Calculate actual hold frames considering constraints
            pre_hold = dance_row.preHold
            post_hold = dance_row.postHold
            
            # Check if we need to adjust for next event
            if i < len(events) - 1:
                next_frame = events[i + 1].frame
                available_frames = next_frame - event.frame
                
                # Ensure minimum transition frames
                max_hold = available_frames - MIN_FORCED_TRANSITION_FRAMES
                if max_hold < 0:
                    max_hold = 0
                
                # Adjust post-hold if needed
                if post_hold > max_hold:
                    post_hold = max_hold
            
            keyframes.append(PoseKeyframe(
                frame=event.frame,
                pose_name=pose,
                interpolation=dance_row.interpolation,
                pre_hold=pre_hold,
                post_hold=post_hold
            ))
        
        return keyframes
    
    def create_action(self, action_name: str):
        """Create or get an action for animation."""
        if not self.bpy:
            return None
            
        # Remove existing action if it exists
        if action_name in self.bpy.data.actions:
            self.bpy.data.actions.remove(self.bpy.data.actions[action_name])
        
        # Create new action
        action = self.bpy.data.actions.new(name=action_name)
        print(f"DEBUG: Created action {action.name}, ID: {action}, users: {action.users}")
        
        # Make sure the action has at least one user so it's saved
        action.use_fake_user = True
        
        # Verify it's in the actions list
        if action.name in self.bpy.data.actions:
            print(f"DEBUG: Action {action.name} is in bpy.data.actions")
        else:
            print(f"DEBUG: Action {action.name} is NOT in bpy.data.actions!")
            print(f"DEBUG: Available actions: {list(self.bpy.data.actions.keys())[:5]}...")
        
        return action
    
    def apply_pose_to_action(self, action, 
                            pose_action,
                            pose_name: str, frame: int,
                            interpolation: str):
        """Apply a pose to an action at a specific frame."""
        # If pose_name is actually an action name, use frame 0 as the pose
        pose_frame = 0
        
        # Check if this is a pose library with markers
        if hasattr(pose_action, 'pose_markers') and pose_action.pose_markers:
            # Find the pose marker
            marker = None
            for m in pose_action.pose_markers:
                if m.name == pose_name:
                    marker = m
                    break
            
            if not marker:
                print(f"Warning: Pose '{pose_name}' not found in markers")
                return
            
            pose_frame = marker.frame
        else:
            # For regular actions, use frame 0 as the pose
            pose_frame = 0
        
        # Copy keyframes from pose to target action
        for fcurve_src in pose_action.fcurves:
            # Create or get corresponding fcurve in target action
            fcurve_dst = action.fcurves.find(
                fcurve_src.data_path, index=fcurve_src.array_index
            )
            if not fcurve_dst:
                fcurve_dst = action.fcurves.new(
                    fcurve_src.data_path, index=fcurve_src.array_index
                )
            
            # Find keyframe at pose frame
            for kf in fcurve_src.keyframe_points:
                if abs(kf.co[0] - pose_frame) < 0.01:
                    # Insert keyframe at target frame
                    new_kf = fcurve_dst.keyframe_points.insert(frame, kf.co[1])
                    
                    # Set interpolation
                    if interpolation.upper() in ['LINEAR', 'BEZIER', 'CONSTANT']:
                        new_kf.interpolation = interpolation.upper()
                    else:
                        # Map other interpolations to Blender types
                        new_kf.interpolation = 'BEZIER'
                        if interpolation in ['back', 'bounce', 'elastic']:
                            new_kf.easing = 'EASE_IN_OUT'
                    
                    break
    
    def generate(self) -> str:
        """Generate the complete animation.
        
        Returns:
            Path to the output blend file
        """
        # First, load all pose actions from the pose blend file
        with self.bpy.data.libraries.load(self.config.form.poseBlendFile, link=False) as (data_from, data_to):
            data_to.actions = list(data_from.actions)
        
        # Load MIDI tracks
        midi_tracks = self.load_midi_tracks()
        
        # Create output blend file if needed
        output_path = Path(self.config.form.blendFileToOutputAction)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create main action
        action = self.create_action(self.config.form.actionNameToCreate)
        print(f"Created action: {action.name if action else 'None'}")
        
        # Process each dance row
        for dance_row in self.config.dance.rows:
            # Find matching MIDI track
            track_events = None
            for track_name, events in midi_tracks.items():
                if dance_row.track.lower() in track_name.lower():
                    track_events = events
                    break
            
            if not track_events:
                print(f"Warning: MIDI track '{dance_row.track}' not found")
                continue
            
            # Get poses for this catalog
            poses = self.get_poses_for_catalog(
                dance_row.poseCatalog, 
                self.config.form.poseBlendFile
            )
            
            if not poses:
                print(f"Warning: No poses found in catalog '{dance_row.poseCatalog}'")
                continue
            
            # Generate pose sequence
            pose_sequence = self.cycle_poses(
                poses, len(track_events), dance_row.cycleMode
            )
            
            # Calculate keyframes
            keyframes = self.calculate_keyframes(
                track_events, pose_sequence, dance_row
            )
            
            # Apply keyframes to action
            # Apply each keyframe
            for kf in keyframes:
                # Find the pose action for this specific pose
                pose_action = None
                for act in self.bpy.data.actions:
                    if act.name == kf.pose_name:
                        pose_action = act
                        break
                
                if pose_action:
                    self.apply_pose_to_action(
                        action, pose_action, kf.pose_name,
                        kf.frame, kf.interpolation
                    )
                else:
                    print(f"Warning: Pose action '{kf.pose_name}' not found")
        
        # Save the blend file
        if not str(output_path).endswith('.blend'):
            output_path = output_path.with_suffix('.blend')
        
        if self.bpy:
            print(f"Actions before save:")
            for act in self.bpy.data.actions:
                print(f"  - {act.name}")
                if act.name == self.config.form.actionNameToCreate:
                    print(f"    ^^^ FOUND TARGET ACTION!")
            
            # Try to find our action explicitly
            if self.config.form.actionNameToCreate in self.bpy.data.actions:
                print(f"Target action '{self.config.form.actionNameToCreate}' exists!")
            else:
                print(f"Target action '{self.config.form.actionNameToCreate}' NOT FOUND!")
            
            self.bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
        
        print(f"Animation saved to: {output_path}")
        return str(output_path)