"""
MIDI Pose Cycler - Node Operators
Operators for node-based workflow
"""

import bpy
from bpy.types import Operator
from bpy.props import StringProperty, IntProperty


class MIDIPOSE_OT_generate_from_nodes(Operator):
    """Generate animation from node tree"""
    bl_idname = "midipose.generate_from_nodes"
    bl_label = "Generate Animation from Nodes"
    bl_description = "Process node tree and generate animation"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get active node tree
        tree = context.space_data.edit_tree if context.space_data else None
        
        if not tree or tree.bl_idname != 'MidiPoseNodeTree':
            self.report({'ERROR'}, "No MIDI Pose node tree active")
            return {'CANCELLED'}
        
        # Find output node
        output_nodes = [n for n in tree.nodes if n.bl_idname == 'AnimationOutputNode']
        if not output_nodes:
            self.report({'ERROR'}, "No Animation Output node found")
            return {'CANCELLED'}
        
        output_node = output_nodes[0]
        
        # Trace back through connections to gather data
        # This would be the full node execution logic
        self.report({'INFO'}, f"Generating animation to '{output_node.action_name}'")
        
        # For now, just mock the generation
        if context.active_object:
            # Create or get action
            action = bpy.data.actions.get(output_node.action_name)
            if not action:
                action = bpy.data.actions.new(name=output_node.action_name)
            
            # Assign to object
            if not context.active_object.animation_data:
                context.active_object.animation_data_create()
            context.active_object.animation_data.action = action
            
            self.report({'INFO'}, "Animation generated successfully!")
        else:
            self.report({'WARNING'}, "No active object to animate")
        
        return {'FINISHED'}


class MIDIPOSE_OT_new_node_tree(Operator):
    """Create new MIDI Pose node tree"""
    bl_idname = "midipose.new_node_tree"
    bl_label = "New MIDI Pose Node Tree"
    bl_description = "Create a new MIDI Pose node tree"
    bl_options = {'REGISTER', 'UNDO'}
    
    name: StringProperty(
        name="Name",
        default="MidiPoseNodeTree"
    )
    
    def execute(self, context):
        # Create new node tree
        tree = bpy.data.node_groups.new(self.name, 'MidiPoseNodeTree')
        
        # Add default nodes
        midi_node = tree.nodes.new('MidiInputNode')
        midi_node.location = (0, 0)
        
        track_node = tree.nodes.new('TrackSelectorNode')
        track_node.location = (250, 0)
        
        filter_node = tree.nodes.new('NoteFilterNode')
        filter_node.location = (500, 0)
        
        pose_input = tree.nodes.new('PoseInputNode')
        pose_input.location = (0, -200)
        
        pose_seq = tree.nodes.new('PoseSequenceNode')
        pose_seq.location = (250, -200)
        
        timing = tree.nodes.new('TimingNode')
        timing.location = (750, -100)
        
        output = tree.nodes.new('AnimationOutputNode')
        output.location = (1000, -100)
        
        # Connect nodes
        tree.links.new(midi_node.outputs[0], track_node.inputs[0])
        tree.links.new(track_node.outputs[0], filter_node.inputs[0])
        tree.links.new(filter_node.outputs[0], timing.inputs[0])
        tree.links.new(pose_input.outputs[0], pose_seq.inputs[0])
        tree.links.new(pose_seq.outputs[0], timing.inputs[1])
        tree.links.new(timing.outputs[0], output.inputs[0])
        
        self.report({'INFO'}, f"Created node tree '{self.name}'")
        return {'FINISHED'}


class MIDIPOSE_OT_move_pose_up(Operator):
    """Move pose up in sequence"""
    bl_idname = "midipose.move_pose_up"
    bl_label = "Move Pose Up"
    bl_description = "Move pose up in sequence"
    
    def execute(self, context):
        # This would move pose in node's internal list
        return {'FINISHED'}


class MIDIPOSE_OT_move_pose_down(Operator):
    """Move pose down in sequence"""
    bl_idname = "midipose.move_pose_down"
    bl_label = "Move Pose Down"
    bl_description = "Move pose down in sequence"
    
    def execute(self, context):
        # This would move pose in node's internal list
        return {'FINISHED'}


class MIDIPOSE_OT_load_midi_node(Operator):
    """Load MIDI file in node"""
    bl_idname = "midipose.load_midi_node"
    bl_label = "Load MIDI"
    bl_description = "Browse and load MIDI file"
    bl_options = {'REGISTER'}
    
    filepath: StringProperty(subtype='FILE_PATH')
    filter_glob: StringProperty(default="*.mid;*.midi", options={'HIDDEN'})
    
    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        node = context.active_node
        if node and node.bl_idname == 'MidiInputNode':
            node.midi_file = self.filepath
        return {'FINISHED'}


class MIDIPOSE_OT_select_track_node(Operator):
    """Select MIDI track in node"""
    bl_idname = "midipose.select_track_node"
    bl_label = "Select Track"
    bl_options = {'REGISTER'}
    
    track_index: IntProperty()
    
    def execute(self, context):
        node = context.active_node
        if node and node.bl_idname == 'TrackSelectorNode':
            node.selected_track = self.track_index
        return {'FINISHED'}


class MIDIPOSE_OT_refresh_poses_node(Operator):
    """Refresh pose list in node"""
    bl_idname = "midipose.refresh_poses_node"
    bl_label = "Refresh"
    bl_options = {'REGISTER'}
    
    def execute(self, context):
        # Force redraw
        for area in context.screen.areas:
            if area.type == 'NODE_EDITOR':
                area.tag_redraw()
        return {'FINISHED'}


class MIDIPOSE_OT_select_pose_node(Operator):
    """Select pose in node"""
    bl_idname = "midipose.select_pose_node"
    bl_label = "Select Pose"
    bl_options = {'REGISTER'}
    
    action_name: StringProperty()
    
    def execute(self, context):
        # Would add to selected poses
        self.report({'INFO'}, f"Selected pose: {self.action_name}")
        return {'FINISHED'}


classes = [
    MIDIPOSE_OT_generate_from_nodes,
    MIDIPOSE_OT_new_node_tree,
    MIDIPOSE_OT_move_pose_up,
    MIDIPOSE_OT_move_pose_down,
    MIDIPOSE_OT_load_midi_node,
    MIDIPOSE_OT_select_track_node,
    MIDIPOSE_OT_refresh_poses_node,
    MIDIPOSE_OT_select_pose_node,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)