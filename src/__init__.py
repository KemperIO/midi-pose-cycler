bl_info = {
    "name": "MIDI Pose Cycler",
    "author": "Voldemort Project",
    "version": (0, 5, 0),
    "blender": (4, 5, 0),
    "location": "View3D > Sidebar > MIDI Pose",
    "description": "Animate a loop of poses to MIDI events",
    "category": "Animation",
}

import bpy
from bpy.props import PointerProperty
import importlib

# Import all modules with reload for development
from . import midi_core
from . import animation_renderer
from . import config_manager
from . import ui_operators
from . import workspace_creator
from . import ui_properties_panels
from . import node_tree
from . import node_operators
from . import workspace_node_based

# Reload modules for development (helps with updates)
importlib.reload(midi_core)
importlib.reload(animation_renderer)
importlib.reload(config_manager)
importlib.reload(ui_operators)
importlib.reload(workspace_creator)
importlib.reload(ui_properties_panels)
importlib.reload(node_tree)
importlib.reload(node_operators)
importlib.reload(workspace_node_based)

# Classes to register
classes = [
    # Property Groups
    ui_operators.TrackItem,
    ui_operators.NoteItem,
    ui_operators.PoseItem,
    ui_operators.MidiPoseProperties,
    
    # Operators
    ui_operators.MIDIPOSE_OT_load_midi,
    ui_operators.MIDIPOSE_OT_reload_midi,
    ui_operators.MIDIPOSE_OT_analyze_midi,
    ui_operators.MIDIPOSE_OT_select_track,
    ui_operators.MIDIPOSE_OT_render_animation,
    ui_operators.MIDIPOSE_OT_refresh_poses,
    ui_operators.MIDIPOSE_OT_select_all_poses,
    ui_operators.MIDIPOSE_OT_deselect_all_poses,
    ui_operators.MIDIPOSE_OT_invert_pose_selection,
    ui_operators.MIDIPOSE_OT_move_pose,
    ui_operators.MIDIPOSE_OT_save_config,
    ui_operators.MIDIPOSE_OT_save_config_as,
    ui_operators.MIDIPOSE_OT_load_config,
    ui_operators.MIDIPOSE_OT_delete_config,
    
    # Workspace Creator
    workspace_creator.MIDIPOSE_OT_create_workspace,
    workspace_creator.MIDIPOSE_OT_setup_drag_drop,
    workspace_node_based.MIDIPOSE_OT_generate_node_workspace,
    
    # Properties Panels
    ui_properties_panels.MIDIPOSE_PT_properties_main,
    ui_properties_panels.MIDIPOSE_PT_properties_poses,
    ui_properties_panels.MIDIPOSE_PT_properties_midi,
]

def menu_func(self, context):
    """Add menu items for MIDI Pose workspaces"""
    self.layout.operator("midipose.create_workspace", 
                        text="MIDI Pose Cycler",
                        icon='FILE_SOUND')
    self.layout.operator("mpc.generate_node_workspace",
                        text="MIDI Pose Nodes",
                        icon='NODETREE')

def register():
    """Register all classes and properties"""
    # Register node system first
    node_tree.register()
    node_operators.register()
    
    # Register other classes
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add properties to scene
    bpy.types.Scene.midi_pose_props = PointerProperty(type=ui_operators.MidiPoseProperties)
    
    # Add menu entries
    bpy.types.TOPBAR_MT_window.append(menu_func)
    if hasattr(bpy.types, 'VIEW3D_MT_editor_menus'):
        bpy.types.VIEW3D_MT_editor_menus.append(menu_func)
    
    print("MIDI Pose Cycler addon registered")

def unregister():
    """Unregister all classes and properties"""
    # Remove menu entries (with error handling)
    try:
        bpy.types.TOPBAR_MT_window.remove(menu_func)
    except:
        pass
    
    try:
        if hasattr(bpy.types, 'VIEW3D_MT_editor_menus'):
            bpy.types.VIEW3D_MT_editor_menus.remove(menu_func)
    except:
        pass
    
    # Remove properties from scene
    del bpy.types.Scene.midi_pose_props
    
    # Unregister classes in reverse order
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Unregister node system
    node_operators.unregister()
    node_tree.unregister()
    
    print("MIDI Pose Cycler addon unregistered")

if __name__ == "__main__":
    register()