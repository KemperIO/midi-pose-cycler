import bpy
import os
import sys
from datetime import datetime
from bpy.types import Operator
from bpy.props import StringProperty, CollectionProperty, BoolProperty, IntProperty, EnumProperty, FloatProperty
from bpy_extras.io_utils import ImportHelper
from . import midi_core
from . import animation_renderer
from . import config_manager
from .midi_core import get_note_events_for_track
from .animation_renderer import RenderConfig, render_animation

class MIDIPOSE_OT_load_midi(Operator, ImportHelper):
    """Load MIDI file for analysis"""
    bl_idname = "midipose.load_midi"
    bl_label = "Load MIDI File"
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".mid"
    filter_glob: StringProperty(default="*.mid;*.midi", options={'HIDDEN'})
    
    def execute(self, context):
        scene = context.scene
        props = scene.midi_pose_props
        props.midi_file = self.filepath
        
        # Clear previous data
        props.track_items.clear()
        props.note_items.clear()
        props.selected_track = ""
        
        # Analyze the MIDI file
        analysis = midi_core.analyze_midi_file(self.filepath)
        if analysis:
            # Populate track list with unique names only (tracks are already merged)
            seen_names = set()
            for track in analysis.tracks:
                if track.name not in seen_names:
                    item = props.track_items.add()
                    item.name = track.name
                    item.note_count = track.note_count
                    item.track_index = track.index
                    seen_names.add(track.name)
            
            # Store the analysis data for later use (Blender ID properties format)
            context.scene['midi_analysis_bpm'] = analysis.bpm
            # Store tracks as a simple dict that Blender can handle
            tracks_data = {}
            for t in analysis.tracks:
                tracks_data[t.name] = t.index
            context.scene['midi_analysis_tracks'] = tracks_data
            
            # Log to console
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n{'='*60}")
            print(f"MIDI Analysis - {timestamp}")
            print(f"{'='*60}")
            print(f"File: {os.path.basename(self.filepath)}")
            print(f"BPM: {analysis.bpm}")
            print(f"Ticks per beat: {analysis.ticks_per_beat}")
            print(f"Total tracks with notes: {len(analysis.tracks)}")
            print(f"{'-'*60}")
            for track in analysis.tracks:
                print(f"Track {track.index}: {track.name}")
                print(f"  Notes: {track.note_count}")
                print(f"  Duration: {track.first_note_time:.2f}s - {track.last_note_time:.2f}s")
            print(f"{'='*60}\n")
            sys.stdout.flush()
            
            self.report({'INFO'}, f"MIDI loaded: {len(analysis.tracks)} tracks found (details in System Console)")
        else:
            self.report({'ERROR'}, "Failed to load MIDI file - check System Console for details")
            print(f"\nERROR: Failed to load MIDI file: {self.filepath}")
            print("Possible reasons:")
            print("  - File does not exist or is not readable")
            print("  - File is not a valid MIDI file")
            print("  - mido library not installed\n")
            sys.stdout.flush()
            
        return {'FINISHED'}

class MIDIPOSE_OT_analyze_midi(Operator):
    """Analyze selected MIDI track"""
    bl_idname = "midipose.analyze_midi"
    bl_label = "Analyze Track"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        
        if not props.midi_file:
            self.report({'ERROR'}, "No MIDI file loaded")
            return {'CANCELLED'}
        
        if not props.selected_track:
            self.report({'ERROR'}, "No track selected")
            return {'CANCELLED'}
        
        # Analyze the specific track
        analysis = midi_core.analyze_midi_file(props.midi_file)
        if not analysis:
            return {'CANCELLED'}
        
        # Find the selected track
        selected_track_data = None
        for track in analysis.tracks:
            if track.name == props.selected_track:
                selected_track_data = track
                break
        
        if selected_track_data:
            # Clear and populate note items
            props.note_items.clear()
            
            # Log detailed analysis to console
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\n{'='*60}")
            print(f"Track Analysis - {timestamp}")
            print(f"{'='*60}")
            print(f"Track: {selected_track_data.name} (index {selected_track_data.index})")
            print(f"Total Notes: {selected_track_data.note_count}")
            print(f"Duration: {selected_track_data.first_note_time:.2f}s - {selected_track_data.last_note_time:.2f}s")
            print(f"Channels: {', '.join(str(c) for c in sorted(selected_track_data.channels))}")
            print(f"{'-'*60}")
            print(f"{'Note':>5} {'Name':>6} {'Count':>7}")
            print(f"{'-'*60}")
            
            for note_num, count in sorted(selected_track_data.notes.items()):
                note_name = midi_core.midi_note_to_name(note_num)
                print(f"{note_num:5d} {note_name:>6s} {count:7d}")
                
                # Add to selectable notes
                item = props.note_items.add()
                item.note_number = note_num
                item.note_name = note_name
                item.count = count
                item.selected = True  # Default to all selected
            
            print(f"{'='*60}\n")
            sys.stdout.flush()
            
            self.report({'INFO'}, f"Track analysis logged to System Console at {timestamp}")
        
        return {'FINISHED'}

class MIDIPOSE_OT_render_animation(Operator):
    """Render pose cycling animation to current action"""
    bl_idname = "midipose.render_animation"
    bl_label = "Render Animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def invoke(self, context, event):
        """Check for existing keyframes and warn user"""
        props = context.scene.midi_pose_props
        
        # Check if action exists and has keyframes
        if not props.skip_keyframe_warning:
            action = bpy.data.actions.get(props.action_name)
            if action and action.fcurves and any(fc.keyframe_points for fc in action.fcurves):
                # Show warning dialog
                return context.window_manager.invoke_props_dialog(self, width=400)
        
        return self.execute(context)
    
    def draw(self, context):
        """Draw warning dialog"""
        layout = self.layout
        props = context.scene.midi_pose_props
        
        col = layout.column()
        col.label(text=f"Action '{props.action_name}' has existing keyframes!", icon='ERROR')
        col.label(text="They will be cleared to generate new animation.")
        col.separator()
        col.prop(props, "skip_keyframe_warning", text="Don't ask again for this action")
    
    def execute(self, context):
        scene = context.scene
        props = scene.midi_pose_props
        
        # Validation
        if not props.midi_file:
            print("ERROR: No MIDI file loaded")
            sys.stdout.flush()
            self.report({'ERROR'}, "No MIDI file loaded")
            return {'CANCELLED'}
        
        if not props.selected_track:
            print("ERROR: No track selected")
            sys.stdout.flush()
            self.report({'ERROR'}, "No track selected")
            return {'CANCELLED'}
        
        if not context.active_object:
            print("ERROR: No active object to animate")
            sys.stdout.flush()
            self.report({'ERROR'}, "No active object to animate")
            return {'CANCELLED'}
        
        # Gather selected poses
        poses = []
        for pose_item in props.pose_items:
            if pose_item.selected:
                poses.append(pose_item.name)
        
        if not poses:
            print("ERROR: No poses selected")
            sys.stdout.flush()
            self.report({'ERROR'}, "No poses selected")
            return {'CANCELLED'}
        
        # Gather selected notes (if filtering)
        target_notes = None
        if props.filter_notes:
            target_notes = set()
            for note_item in props.note_items:
                if note_item.selected:
                    target_notes.add(note_item.note_number)
        
        # Determine frame limit
        max_frames = props.frame_limit if props.use_frame_limit else props.total_frames
        
        # Get note events
        note_frames = get_note_events_for_track(
            props.midi_file,
            props.selected_track,
            target_notes,
            scene.render.fps,
            max_frames
        )
        
        if not note_frames:
            warning_msg = f"No matching notes found in track '{props.selected_track}'"
            if props.filter_notes and target_notes:
                warning_msg += f" with note filter: {target_notes}"
            print(f"WARNING: {warning_msg}")
            print(f"  - MIDI file: {props.midi_file}")
            print(f"  - Track: {props.selected_track}")
            print(f"  - Filter enabled: {props.filter_notes}")
            if target_notes:
                print(f"  - Target notes: {sorted(target_notes)}")
            sys.stdout.flush()
            self.report({'WARNING'}, warning_msg)
            return {'CANCELLED'}
        
        # Create render configuration
        config = RenderConfig(
            midi_path=props.midi_file,
            track_name=props.selected_track,
            poses=poses,
            target_notes=target_notes,
            frames_to_hold=props.frames_to_hold,
            interpolation_type=props.interpolation_type,
            fps=scene.render.fps,
            total_frames=max_frames,
            action_name=props.action_name,
            pose_cycle_mode=props.pose_cycle_mode
        )
        
        # Render the animation
        if render_animation(config, note_frames):
            self.report({'INFO'}, f"Rendered {len(note_frames)} keyframes")
        else:
            self.report({'ERROR'}, "Failed to render animation")
            return {'CANCELLED'}
        
        return {'FINISHED'}

class MIDIPOSE_OT_reload_midi(Operator):
    """Reload the current MIDI file"""
    bl_idname = "midipose.reload_midi"
    bl_label = "Reload MIDI"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        
        if not props.midi_file:
            self.report({'ERROR'}, "No MIDI file to reload")
            return {'CANCELLED'}
        
        # Clear and reload
        filepath = props.midi_file
        props.track_items.clear()
        props.note_items.clear()
        props.selected_track = ""
        
        # Analyze the MIDI file
        analysis = midi_core.analyze_midi_file(filepath)
        if analysis:
            # Populate track list with unique names only (tracks are already merged)
            seen_names = set()
            for track in analysis.tracks:
                if track.name not in seen_names:
                    item = props.track_items.add()
                    item.name = track.name
                    item.note_count = track.note_count
                    item.track_index = track.index
                    seen_names.add(track.name)
            
            # Store the analysis data (Blender ID properties format)
            context.scene['midi_analysis_bpm'] = analysis.bpm
            tracks_data = {}
            for t in analysis.tracks:
                tracks_data[t.name] = t.index
            context.scene['midi_analysis_tracks'] = tracks_data
            
            # Log to console
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"\nMIDI Reloaded at {timestamp}")
            print(f"Tracks found: {len(analysis.tracks)}")
            sys.stdout.flush()
            
            self.report({'INFO'}, f"Reloaded: {len(analysis.tracks)} tracks found")
        else:
            self.report({'ERROR'}, "Failed to reload MIDI file")
            
        return {'FINISHED'}

class MIDIPOSE_OT_select_track(Operator):
    """Select and analyze a MIDI track"""
    bl_idname = "midipose.select_track"
    bl_label = "Select Track"
    bl_options = {'REGISTER'}
    
    track_name: StringProperty(name="Track Name")
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        
        # Set the selected track
        props.selected_track = self.track_name
        
        # Now analyze the track if we have a valid selection
        if self.track_name:
            # Call analyze directly rather than through operator
            return bpy.ops.midipose.analyze_midi()
        
        return {'FINISHED'}

class MIDIPOSE_OT_refresh_poses(Operator):
    """Refresh available poses from project"""
    bl_idname = "midipose.refresh_poses"
    bl_label = "Refresh Poses"
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        props.pose_items.clear()
        
        poses = animation_renderer.get_available_poses()
        for pose_name in poses:
            item = props.pose_items.add()
            item.name = pose_name
            item.selected = False
        
        self.report({'INFO'}, f"Found {len(poses)} poses")
        return {'FINISHED'}

class MIDIPOSE_OT_select_all_poses(Operator):
    """Select all poses"""
    bl_idname = "midipose.select_all_poses"
    bl_label = "Select All"
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        for pose in props.pose_items:
            pose.selected = True
        return {'FINISHED'}

class MIDIPOSE_OT_deselect_all_poses(Operator):
    """Deselect all poses"""
    bl_idname = "midipose.deselect_all_poses"
    bl_label = "Deselect All"
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        for pose in props.pose_items:
            pose.selected = False
        return {'FINISHED'}

class MIDIPOSE_OT_invert_pose_selection(Operator):
    """Invert pose selection"""
    bl_idname = "midipose.invert_pose_selection"
    bl_label = "Invert Selection"
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        for pose in props.pose_items:
            pose.selected = not pose.selected
        return {'FINISHED'}

class MIDIPOSE_OT_save_config(Operator):
    """Save current configuration"""
    bl_idname = "midipose.save_config"
    bl_label = "Save Config"
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        
        if not props.active_config:
            self.report({'WARNING'}, "No config name set - use Save As")
            return bpy.ops.midipose.save_config_as('INVOKE_DEFAULT')
        
        if config_manager.save_config_to_scene(props.active_config, props):
            self.report({'INFO'}, f"Config saved: {props.active_config}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to save config")
            return {'CANCELLED'}

class MIDIPOSE_OT_save_config_as(Operator):
    """Save configuration with new name"""
    bl_idname = "midipose.save_config_as"
    bl_label = "Save Config As"
    
    config_name: StringProperty(
        name="Config Name",
        description="Name for this configuration",
        default="Animation Config"
    )
    
    def invoke(self, context, event):
        props = context.scene.midi_pose_props
        if props.active_config:
            self.config_name = props.active_config
        return context.window_manager.invoke_props_dialog(self)
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        
        if not self.config_name:
            self.report({'ERROR'}, "Config name required")
            return {'CANCELLED'}
        
        if config_manager.save_config_to_scene(self.config_name, props):
            self.report({'INFO'}, f"Config saved as: {self.config_name}")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to save config")
            return {'CANCELLED'}

class MIDIPOSE_OT_load_config(Operator):
    """Load saved configuration"""
    bl_idname = "midipose.load_config"
    bl_label = "Load Config"
    
    config_name: StringProperty(
        name="Config Name",
        description="Configuration to load"
    )
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        
        config_to_load = self.config_name if self.config_name else props.active_config
        
        if not config_to_load:
            self.report({'ERROR'}, "No config selected")
            return {'CANCELLED'}
        
        if config_manager.load_config_from_scene(config_to_load, props):
            self.report({'INFO'}, f"Config loaded: {config_to_load}")
            
            # Reload MIDI file if needed
            if props.midi_file:
                bpy.ops.midipose.reload_midi()
            
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, f"Failed to load config: {config_to_load}")
            return {'CANCELLED'}

class MIDIPOSE_OT_delete_config(Operator):
    """Delete saved configuration"""
    bl_idname = "midipose.delete_config"
    bl_label = "Delete Config"
    
    def execute(self, context):
        props = context.scene.midi_pose_props
        
        if not props.active_config:
            self.report({'ERROR'}, "No config selected")
            return {'CANCELLED'}
        
        if config_manager.delete_config_from_scene(props.active_config):
            self.report({'INFO'}, f"Config deleted: {props.active_config}")
            props.active_config = ""
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to delete config")
            return {'CANCELLED'}

class TrackItem(bpy.types.PropertyGroup):
    """Property group for MIDI tracks"""
    name: StringProperty(name="Track Name")
    note_count: IntProperty(name="Note Count")
    track_index: IntProperty(name="Track Index")

class NoteItem(bpy.types.PropertyGroup):
    """Property group for MIDI notes"""
    note_number: IntProperty(name="Note Number")
    note_name: StringProperty(name="Note Name")
    count: IntProperty(name="Count")
    selected: BoolProperty(name="Selected", default=True)
    nickname: StringProperty(
        name="Nickname",
        description="Custom name for this note (e.g., 'snare', 'kick')",
        default=""
    )

class PoseItem(bpy.types.PropertyGroup):
    """Property group for poses"""
    name: StringProperty(name="Pose Name")
    selected: BoolProperty(name="Selected", default=False)

class MidiPoseProperties(bpy.types.PropertyGroup):
    """Main property group for the addon"""
    midi_file: StringProperty(
        name="MIDI File",
        description="Path to MIDI file",
        subtype='FILE_PATH'
    )
    
    selected_track: StringProperty(
        name="Track",
        description="Selected MIDI track"
    )
    
    analysis_result: StringProperty(
        name="Analysis",
        description="MIDI analysis results",
        default=""
    )
    
    track_items: CollectionProperty(type=TrackItem)
    note_items: CollectionProperty(type=NoteItem)
    pose_items: CollectionProperty(type=PoseItem)
    
    filter_notes: BoolProperty(
        name="Filter Notes",
        description="Only use selected notes",
        default=False
    )
    
    frames_to_hold: IntProperty(
        name="Hold Frames",
        description="Frames to hold each pose",
        default=3,
        min=0,
        max=30
    )
    
    interpolation_type: EnumProperty(
        name="Interpolation",
        description="Interpolation type for transitions",
        items=animation_renderer.get_interpolation_types(),
        default='EXPO'
    )
    
    total_frames: IntProperty(
        name="Total Frames",
        description="Maximum animation length",
        default=240,
        min=1,
        max=10000
    )
    
    # New fields for enhanced functionality
    action_name: StringProperty(
        name="Action Name",
        description="Name for the generated action",
        default="MidiPoseCyclingAnimation"
    )
    
    pose_cycle_mode: EnumProperty(
        name="Cycle Mode",
        description="How poses cycle through the sequence",
        items=[
            ('LOOP', 'Loop', 'Cycle through poses in order, restart at beginning'),
            ('BOOMERANG', 'Boomerang', 'Cycle forward then backward'),
            ('RANDOM', 'Random', 'Random pose selection'),
        ],
        default='LOOP'
    )
    
    use_frame_limit: BoolProperty(
        name="Use Frame Limit",
        description="Limit animation to specific frame count",
        default=False
    )
    
    frame_limit: IntProperty(
        name="Frame Limit",
        description="Maximum frames to generate (when limited)",
        default=240,
        min=1,
        max=10000
    )
    
    # Config management
    active_config: StringProperty(
        name="Active Config",
        description="Currently loaded configuration"
    )
    
    # UI list indices
    active_pose_index: IntProperty()
    active_track_index: IntProperty()
    active_note_index: IntProperty()
    
    # Warning preferences
    skip_keyframe_warning: BoolProperty(
        name="Skip Keyframe Warning",
        description="Don't warn about overwriting keyframes",
        default=False
    )