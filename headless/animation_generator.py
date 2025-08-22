"""Animation generator for headless MIDI pose cycler."""

import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

# Add vendor path for mido
vendor_path = Path(__file__).parent.parent / "vendor"
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
        
        # Link the blend file to access its data
        with self.bpy.data.libraries.load(blend_file, link=True) as (data_from, data_to):
            # Look for actions that might contain poses
            for action_name in data_from.actions:
                if catalog_name.lower() in action_name.lower():
                    data_to.actions.append(action_name)
        
        # Find poses in the loaded actions
        for action in self.bpy.data.actions:
            if catalog_name.lower() in action.name.lower():
                # Get pose markers from this action
                for marker in action.pose_markers:
                    poses.append(marker.name)
        
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
        return action
    
    def apply_pose_to_action(self, action, 
                            pose_action,
                            pose_name: str, frame: int,
                            interpolation: str):
        """Apply a pose to an action at a specific frame."""
        # Find the pose marker
        marker = None
        for m in pose_action.pose_markers:
            if m.name == pose_name:
                marker = m
                break
        
        if not marker:
            print(f"Warning: Pose '{pose_name}' not found")
            return
        
        # Get the pose frame
        pose_frame = marker.frame
        
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
        # Load MIDI tracks
        midi_tracks = self.load_midi_tracks()
        
        # Create output blend file if needed
        output_path = Path(self.config.form.blendFileToOutputAction)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create main action
        action = self.create_action(self.config.form.actionNameToCreate)
        
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
            # First, we need to load the pose actions
            with self.bpy.data.libraries.load(self.config.form.poseBlendFile, link=False) as (data_from, data_to):
                for action_name in data_from.actions:
                    if dance_row.poseCatalog.lower() in action_name.lower():
                        data_to.actions.append(action_name)
            
            # Find the pose action
            pose_action = None
            for act in self.bpy.data.actions:
                if dance_row.poseCatalog.lower() in act.name.lower():
                    pose_action = act
                    break
            
            if pose_action:
                # Apply each keyframe
                for kf in keyframes:
                    self.apply_pose_to_action(
                        action, pose_action, kf.pose_name,
                        kf.frame, kf.interpolation
                    )
        
        # Save the blend file
        if not str(output_path).endswith('.blend'):
            output_path = output_path.with_suffix('.blend')
        
        if self.bpy:
            self.bpy.ops.wm.save_as_mainfile(filepath=str(output_path))
        
        print(f"Animation saved to: {output_path}")
        return str(output_path)