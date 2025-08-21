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


# MAIN RUN PANEL - Generate button and core settings
class MIDIPOSE_PT_run_main(Panel, MidiPosePanel):
    """Main run panel with generate button"""
    bl_label = "Run Animation"
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
            # Show summary table
            col = layout.column()
            col.label(text="Ready to generate:", icon='CHECKMARK')
            
            # Track summary table
            box = col.box()
            box.label(text="Selected Tracks:", icon='NLA')
            
            # Table header
            row = box.row()
            row.scale_y = 0.8
            sub = row.row()
            sub.scale_x = 2.0
            sub.label(text="Track")
            sub = row.row()
            sub.label(text="Events")
            sub = row.row()
            sub.label(text="Tones")
            
            box.separator(factor=0.5)
            
            # Table rows
            for track in selected_tracks:
                row = box.row()
                row.scale_y = 0.9
                
                # Track name
                sub = row.row()
                sub.scale_x = 2.0
                sub.label(text=track.name, icon='NLA_PUSHDOWN')
                
                # Event count
                sub = row.row()
                sub.label(text=f"{track.note_count}")
                
                # Tone filter info
                sub = row.row()
                if track.is_dynamic:
                    sub.label(text="N/A", icon='TIME')
                elif track.filter_notes and track.note_filters:
                    selected_tones = [n for n in track.note_filters if n.selected]
                    if selected_tones:
                        # Show first few selected tones
                        tone_names = [f"{t.note_name}" for t in selected_tones[:3]]
                        text = ", ".join(tone_names)
                        if len(selected_tones) > 3:
                            text += f" (+{len(selected_tones)-3})"
                        sub.label(text=text, icon='FILTER')
                    else:
                        sub.label(text="None", icon='X')
                else:
                    sub.label(text="All", icon='CHECKBOX_HLT')
            
            # Pose summary
            box.separator()
            row = box.row()
            row.label(text="Poses:", icon='ARMATURE_DATA')
            row.label(text=f"{len(selected_poses)} selected")
            
            # Action name
            row = box.row()
            row.label(text="Output:", icon='ACTION')
            row.label(text=props.action_name)


# ACTION SETTINGS PANEL
class MIDIPOSE_PT_run_action(Panel, MidiPosePanel):
    """Action and animation settings"""
    bl_label = "Action Settings"
    bl_idname = "MIDIPOSE_PT_run_action"
    bl_category = "MPC-Run"
    bl_parent_id = "MIDIPOSE_PT_run_main"
    bl_options = {'DEFAULT_CLOSED'}
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        col = layout.column()
        
        # Action selection dropdown
        row = col.row()
        row.label(text="Action:")
        row.prop_search(props, "action_name", bpy.data, "actions", text="")
        
        # Create new action button
        row = col.row()
        row.operator("action.new", text="New Action", icon='ADD')
        
        # Warning if action exists
        action = bpy.data.actions.get(props.action_name)
        if action and action.fcurves and any(fc.keyframe_points for fc in action.fcurves):
            box = col.box()
            box.alert = True
            box.label(text="⚠️ Action has keyframes!", icon='ERROR')
            box.prop(props, "skip_keyframe_warning", text="Don't warn about overwriting")
        
        col.separator()
        
        # Animation mode
        row = col.row()
        row.label(text="Mode:")
        row.prop(props, "animation_mode", text="")
        
        # Cycle mode
        row = col.row()
        row.label(text="Cycle:")
        row.prop(props, "pose_cycle_mode", text="")
        
        # Frame settings
        col.separator()
        row = col.row()
        row.label(text="Hold Frames:")
        row.prop(props, "frames_to_hold", text="")
        
        row = col.row()
        row.label(text="Interpolation:")
        row.prop(props, "interpolation_type", text="")


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


# PREVIEW PANEL - Shows current selection summary
class MIDIPOSE_PT_run_preview(Panel, MidiPosePanel):
    """Preview of current setup"""
    bl_label = "Preview"
    bl_idname = "MIDIPOSE_PT_run_preview"
    bl_category = "MPC-Run"
    bl_parent_id = "MIDIPOSE_PT_run_main"
    
    def draw(self, context):
        layout = self.layout
        props = context.scene.midi_pose_props
        
        if props.midi_file:
            # MIDI info
            box = layout.box()
            box.label(text="MIDI:", icon='FILE_SOUND')
            box.label(text=os.path.basename(props.midi_file))
            
            if props.selected_track:
                box.label(text=f"Track: {props.selected_track}")
                
                # Note filtering info
                if props.filter_notes:
                    selected_notes = sum(1 for n in props.note_items if n.selected)
                    box.label(text=f"Notes: {selected_notes} selected")
                else:
                    box.label(text="Notes: All")
        
        # Pose info
        selected_poses = [p for p in props.pose_items if p.selected]
        if selected_poses:
            box = layout.box()
            box.label(text="Poses:", icon='ARMATURE_DATA')
            
            # Show first few poses
            for i, pose in enumerate(selected_poses[:3]):
                box.label(text=f"  {i+1}. {pose.name}")
            
            if len(selected_poses) > 3:
                box.label(text=f"  ... and {len(selected_poses) - 3} more")


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
    MIDIPOSE_PT_run_action,
    MIDIPOSE_PT_run_timing,
    MIDIPOSE_PT_run_preview,
    MIDIPOSE_PT_run_config,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)