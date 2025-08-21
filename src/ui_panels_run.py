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
        
        # Enable button only if we have required data
        can_generate = (bool(props.midi_file) and 
                       bool(props.selected_track) and 
                       any(p.selected for p in props.pose_items))
        
        row.enabled = can_generate
        row.operator("midipose.render_animation", 
                    text="GENERATE ANIMATION", 
                    icon='PLAY')
        
        # Status info
        if not can_generate:
            col = layout.column()
            col.alert = True
            if not props.midi_file:
                col.label(text="❌ No MIDI file loaded", icon='ERROR')
            if props.midi_file and not props.selected_track:
                col.label(text="❌ No track selected", icon='ERROR')
            if props.selected_track and not any(p.selected for p in props.pose_items):
                col.label(text="❌ No poses selected", icon='ERROR')
        else:
            # Show preview of what will be generated
            col = layout.column()
            col.label(text="Ready to generate:", icon='CHECKMARK')
            
            box = col.box()
            box.scale_y = 0.9
            
            # Track info
            row = box.row()
            row.label(text="Track:", icon='NLA')
            row.label(text=props.selected_track)
            
            # Pose count
            selected_count = sum(1 for p in props.pose_items if p.selected)
            row = box.row()
            row.label(text="Poses:", icon='ARMATURE_DATA')
            row.label(text=f"{selected_count} selected")
            
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
            # Smart controls (bars/beats)
            col = layout.column()
            
            row = col.row(align=True)
            row.label(text="Start:")
            row.prop(props, "midi_start_bar", text="Bar")
            row.prop(props, "midi_start_beat", text="Beat")
            
            row = col.row(align=True)
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