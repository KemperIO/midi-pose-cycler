"""
MIDI Pose Cycler - Run Tab
Main execution panel with generate button, settings, and configurations
"""

import bpy
from bpy.types import Panel
import os

# Base class for all panels
class MidiPosePanel:
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    
    @classmethod
    def poll(cls, context):
        # Show in object and pose modes
        return context.mode in ('OBJECT', 'POSE')


# MAIN RUN PANEL - Generate button only
class MIDIPOSE_PT_run_main(Panel, MidiPosePanel):
    """Main run panel with generate button"""
    bl_label = "Run"
    bl_idname = "MIDIPOSE_PT_run_main"
    bl_category = "MPC-Run"
    bl_order = 0
    
    def draw_header(self, context):
        self.layout.label(text="", icon='PLAY')
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.midi_pose_props
        
        # Main Generate Button - At the top for visibility
        row = layout.row()
        row.scale_y = 2.0
        
        # Check what's missing for generation
        selected_tracks = [t for t in props.track_items if t.selected]
        selected_poses = [p for p in props.pose_items if p.selected]
        
        # Build status message
        missing = []
        if not props.midi_file:
            missing.append("MIDI file")
        if not selected_tracks:
            missing.append("tracks")
        if not selected_poses:
            missing.append("poses")
        
        # Enable button only if we have required data
        can_generate = len(missing) == 0
        
        row.enabled = can_generate
        op = row.operator("midipose.render_animation", 
                         text="GENERATE ANIMATION", 
                         icon='PLAY')
        
        # Show tooltip explaining what's missing
        if not can_generate:
            row.alert = True
            if missing:
                tooltip = "Missing: " + ", ".join(missing)
            else:
                tooltip = "Ready to generate"
        
        # Status info
        selected_tracks = [t for t in props.track_items if t.selected]
        selected_poses = [p for p in props.pose_items if p.selected]
        
        # Update can_generate for multi-track
        can_generate = (bool(props.midi_file) and 
                       len(selected_tracks) > 0 and 
                       len(selected_poses) > 0)
        
        if not can_generate:
            col = layout.column()
            col.alert = True
            if not props.midi_file:
                col.label(text="❌ No MIDI file loaded", icon='ERROR')
            if props.midi_file and not selected_tracks:
                col.label(text="❌ No tracks selected", icon='ERROR')
            if selected_tracks and not selected_poses:
                col.label(text="❌ No poses selected", icon='ERROR')
        else:
            col = layout.column()
            col.label(text="Ready to generate!", icon='CHECKMARK')


# OUTPUT PANEL
class MIDIPOSE_PT_run_output(Panel, MidiPosePanel):
    """Output action settings"""
    bl_label = "Output"
    bl_idname = "MIDIPOSE_PT_run_output"
    bl_category = "MPC-Run"
    bl_parent_id = "MIDIPOSE_PT_run_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        col = layout.column()
        
        # Action selection dropdown
        row = col.row()
        row.label(text="Output Action:")
        row.prop_search(props, "action_name", bpy.data, "actions", text="")
        
        # Helper text
        row = col.row()
        row.scale_y = 0.7
        if props.action_name and props.action_name not in bpy.data.actions:
            row.label(text="Will create new action", icon='ADD')
        elif props.action_name:
            row.label(text="Will update existing action", icon='FILE_REFRESH')
        else:
            row.label(text="Enter name for new action", icon='INFO')
        
        # Warning if action exists and has keyframes
        if props.action_name:  # Only check if action name is set
            action = bpy.data.actions.get(props.action_name)
            if action and action.fcurves:
                # Check if action actually has keyframes
                has_keyframes = any(fc.keyframe_points for fc in action.fcurves)
                if has_keyframes:
                    box = col.box()
                    box.alert = True
                    # Yellow warning color through alert flag
                    col_warn = box.column()
                    col_warn.alert = True
                    col_warn.label(text="⚠️ Action has keyframes!", icon='ERROR')
                    box.prop(props, "skip_keyframe_warning", text="Don't warn about overwriting")


# TIMING PANEL
class MIDIPOSE_PT_run_timing(Panel, MidiPosePanel):
    """Timing settings"""
    bl_label = "Timing"
    bl_idname = "MIDIPOSE_PT_run_timing"
    bl_category = "MPC-Run"
    bl_parent_id = "MIDIPOSE_PT_run_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.midi_pose_props
        
        # BPM settings
        row = layout.row(align=True)
        row.label(text="BPM:")
        row.prop(props, "bpm", text="")
        row.label(text="Beats/Bar:")
        row.prop(props, "beats_per_bar", text="")
        
        # Smart/dumb timing toggle
        layout.prop(props, "use_smart_timing", text="Use Musical Timing")
        
        if props.use_smart_timing:
            # Smart controls with side-by-side display
            box = layout.box()
            box.label(text="Smart Timing Controls", icon='TIME')
            
            # Start position table
            grid = box.grid_flow(columns=2, align=True)
            
            # Labels
            grid.label(text="Start Frame")
            grid.label(text="Start Bar/Beat")
            
            # Values
            grid.prop(props, "midi_start_frame", text="")
            row = grid.row(align=True)
            row.prop(props, "midi_start_bar", text="")
            row.prop(props, "midi_start_beat", text="")
            
            box.separator()
            
            # Length controls
            row = box.row(align=True)
            row.label(text="Length:")
            row.prop(props, "midi_length_bars", text="Bars")
            row.prop(props, "midi_length_beats", text="+ Beats")
        else:
            # Dumb controls (frames)
            col = layout.column()
            
            row = col.row()
            row.label(text="Start Frame:")
            row.prop(props, "midi_start_frame", text="")
            
            row = col.row(align=True)
            row.prop(props, "use_frame_limit", text="Limit")
            if props.use_frame_limit:
                row.prop(props, "frame_limit", text="")
        
        # Info
        col = layout.column()
        col.scale_y = 0.8
        info_text = f"Max: {props.frame_limit} frames" if props.use_frame_limit else "Using all MIDI events"
        col.label(text=info_text, icon='INFO')
        col.label(text=f"Project FPS: {scene.render.fps}", icon='TIME')


# INPUT SUMMARY PANEL - Shows current selection summary
class MIDIPOSE_PT_run_input(Panel, MidiPosePanel):
    """Input summary of current setup"""
    bl_label = "Input Summary"
    bl_idname = "MIDIPOSE_PT_run_input"
    bl_category = "MPC-Run"
    bl_parent_id = "MIDIPOSE_PT_run_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        scene = context.scene
        
        # Settings table
        box = layout.box()
        box.label(text="Settings:", icon='SETTINGS')
        
        # Create a two-column grid
        grid = box.grid_flow(columns=2, align=True)
        
        # Mode
        grid.label(text="Mode:")
        grid.label(text=props.animation_mode)
        
        # Cycle
        grid.label(text="Cycle:")
        grid.label(text=props.pose_cycle_mode.replace('_', ' ').title())
        
        # Hold Frames
        grid.label(text="Hold:")
        grid.label(text=f"{props.frames_to_hold} frames")
        
        # Interpolation
        grid.label(text="Interpolation:")
        grid.label(text=props.interpolation_type.replace('_', ' ').title())
        
        layout.separator()
        
        # MIDI info table
        if props.midi_file:
            box = layout.box()
            box.label(text="MIDI Data:", icon='FILE_SOUND')
            
            # File name
            row = box.row()
            row.label(text="File:")
            row.label(text=os.path.basename(props.midi_file))
            
            # Selected tracks
            selected_tracks = [t for t in props.track_items if t.selected]
            if selected_tracks:
                box.separator(factor=0.5)
                
                # Table header
                row = box.row()
                row.label(text="Track")
                row.label(text="Notes")
                row.label(text="Tones")
                
                box.separator(factor=0.2)
                
                # Track rows
                for track in selected_tracks:
                    row = box.row()
                    
                    # Track name (truncate if needed)
                    name = track.name
                    if len(name) > 15:
                        name = name[:12] + "..."
                    row.label(text=name)
                    
                    # Note count
                    row.label(text=str(track.note_count))
                    
                    # Tone info
                    if track.is_dynamic:
                        row.label(text="Dynamic")
                    elif track.filter_notes and track.note_filters:
                        selected_tones = [n for n in track.note_filters if n.selected]
                        row.label(text=f"{len(selected_tones)}/{len(track.note_filters)}")
                    else:
                        row.label(text="All")
            else:
                box.label(text="No tracks selected", icon='ERROR')
        else:
            box = layout.box()
            box.label(text="No MIDI file loaded", icon='ERROR')


# CONFIGURATION PANEL
class MIDIPOSE_PT_run_config(Panel, MidiPosePanel):
    """Save/Load configurations"""
    bl_label = "Configurations"
    bl_idname = "MIDIPOSE_PT_run_config"
    bl_category = "MPC-Run"
    bl_parent_id = "MIDIPOSE_PT_run_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        col = layout.column()
        
        # Current config
        if props.active_config:
            row = col.row()
            row.label(text="Active:")
            row.label(text=props.active_config)
            col.separator()
        
        # Config actions
        row = col.row(align=True)
        row.operator("midipose.save_config", text="Save", icon='FILE_TICK')
        row.operator("midipose.save_config_as", text="Save As", icon='FILE_NEW')
        
        row = col.row(align=True)
        row.operator("midipose.load_config", text="Load", icon='FILE_FOLDER')
        if props.active_config:
            row.operator("midipose.delete_config", text="Delete", icon='X')


# Registration
classes = [
    MIDIPOSE_PT_run_main,
    MIDIPOSE_PT_run_output,
    MIDIPOSE_PT_run_timing,
    MIDIPOSE_PT_run_input,
    MIDIPOSE_PT_run_config,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)