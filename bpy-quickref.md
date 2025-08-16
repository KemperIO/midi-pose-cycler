# Blender Python API Quick Reference for MIDI Pose Cycler

## Core Concepts

### Actions & Animation
```python
# Create new action
action = bpy.data.actions.new(name="MyAction")

# Get or create action
if "MyAction" in bpy.data.actions:
    action = bpy.data.actions["MyAction"]
else:
    action = bpy.data.actions.new(name="MyAction")

# Assign action to object
obj.animation_data_create()
obj.animation_data.action = action

# Clear FCurves (keyframes)
action.fcurves.clear()

# Create FCurve for property
fcurve = action.fcurves.new(data_path="location", index=0)  # index: 0=X, 1=Y, 2=Z

# Insert keyframe
keyframe = fcurve.keyframe_points.insert(frame=10, value=5.0, options={'FAST'})
keyframe.interpolation = 'CONSTANT'  # or 'LINEAR', 'BEZIER', 'EXPO'

# Check if action has keyframes
has_keyframes = any(fc.keyframe_points for fc in action.fcurves)
```

### Keyframe Interpolation Types
```python
INTERPOLATION_TYPES = [
    ('CONSTANT', 'Constant', 'No interpolation'),
    ('LINEAR', 'Linear', 'Linear interpolation'),
    ('BEZIER', 'Bezier', 'Smooth interpolation'),
    ('SINE', 'Sinusoidal', 'Sinusoidal easing'),
    ('QUAD', 'Quadratic', 'Quadratic easing'),
    ('CUBIC', 'Cubic', 'Cubic easing'),
    ('QUART', 'Quartic', 'Quartic easing'),
    ('QUINT', 'Quintic', 'Quintic easing'),
    ('EXPO', 'Exponential', 'Exponential easing'),
    ('CIRC', 'Circular', 'Circular easing'),
    ('BACK', 'Back', 'Overshooting cubic easing'),
    ('BOUNCE', 'Bounce', 'Exponentially decaying bounce'),
    ('ELASTIC', 'Elastic', 'Exponentially decaying sine wave'),
]
```

### Custom Properties & Scene Data
```python
# Store custom data in scene (persistent)
scene = bpy.context.scene

# Simple values
scene["my_value"] = 42
scene["my_string"] = "Hello"

# Complex data (use JSON for nested structures)
import json
config_data = {"poses": ["pose1", "pose2"], "settings": {"fps": 24}}
scene["my_config"] = json.dumps(config_data)

# Retrieve data
if "my_config" in scene:
    config = json.loads(scene["my_config"])

# Property Groups (structured data)
class MyProperties(bpy.types.PropertyGroup):
    my_int: IntProperty(name="Integer", default=0, min=0, max=100)
    my_string: StringProperty(name="String", default="")
    my_bool: BoolProperty(name="Boolean", default=False)
    my_enum: EnumProperty(
        name="Choice",
        items=[
            ('OPT1', 'Option 1', 'First option'),
            ('OPT2', 'Option 2', 'Second option'),
        ]
    )

# Register property group
bpy.utils.register_class(MyProperties)
bpy.types.Scene.my_props = PointerProperty(type=MyProperties)
```

### Collections & Lists
```python
# Collection Properties for dynamic lists
class ListItem(bpy.types.PropertyGroup):
    name: StringProperty()
    value: IntProperty()
    selected: BoolProperty()

class MyProps(bpy.types.PropertyGroup):
    items: CollectionProperty(type=ListItem)
    active_index: IntProperty()

# Add items
item = props.items.add()
item.name = "Item 1"
item.value = 10

# Clear items
props.items.clear()

# Iterate items
for item in props.items:
    print(item.name, item.value)
```

### UI Lists
```python
class MY_UL_list(UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.prop(item, "name", text="", emboss=False)
            layout.prop(item, "selected", text="")
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text=item.name)

# Use in panel
layout.template_list(
    "MY_UL_list", "",
    props, "items",
    props, "active_index",
    rows=5
)
```

### Operators
```python
class MY_OT_operator(bpy.types.Operator):
    """Tooltip description"""
    bl_idname = "my_category.operator_name"
    bl_label = "Operator Label"
    bl_options = {'REGISTER', 'UNDO'}  # Enable undo
    
    # Properties
    my_prop: StringProperty(default="")
    
    @classmethod
    def poll(cls, context):
        # Return True if operator can run
        return context.active_object is not None
    
    def invoke(self, context, event):
        # Called when operator is invoked (for dialogs)
        return context.window_manager.invoke_props_dialog(self)
    
    def draw(self, context):
        # Draw dialog UI
        layout = self.layout
        layout.prop(self, "my_prop")
    
    def execute(self, context):
        # Main execution
        self.report({'INFO'}, "Operation complete")
        return {'FINISHED'}
```

### Panels
```python
class MY_PT_panel(bpy.types.Panel):
    bl_label = "Panel Title"
    bl_idname = "MY_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Tool"
    bl_options = {'DEFAULT_CLOSED'}  # Start collapsed
    
    @classmethod
    def poll(cls, context):
        return True  # Show when True
    
    def draw_header(self, context):
        # Custom header content
        self.layout.label(text="", icon='SETTINGS')
    
    def draw(self, context):
        layout = self.layout
        
        # Column layout
        col = layout.column()
        col.label(text="Settings")
        
        # Row layout
        row = layout.row(align=True)
        row.operator("my.operator")
        
        # Box for grouping
        box = layout.box()
        box.label(text="Group")
        
        # Split layout
        split = layout.split(factor=0.3)
        split.label(text="Label:")
        split.prop(context.scene, "property")
```

### File Operations
```python
# Import helper for file browser
from bpy_extras.io_utils import ImportHelper

class MY_OT_import(Operator, ImportHelper):
    bl_idname = "my.import"
    bl_label = "Import File"
    
    filename_ext = ".txt"
    filter_glob: StringProperty(default="*.txt", options={'HIDDEN'})
    
    def execute(self, context):
        # self.filepath contains selected file
        with open(self.filepath, 'r') as f:
            content = f.read()
        return {'FINISHED'}
```

### Context & Active Object
```python
# Get context
context = bpy.context
scene = context.scene
obj = context.active_object
selected = context.selected_objects

# Check object type
if obj and obj.type == 'ARMATURE':
    armature = obj.data

# Ensure animation data exists
if not obj.animation_data:
    obj.animation_data_create()

# Get current frame
frame = scene.frame_current
fps = scene.render.fps
```

### Workspace & Areas
```python
# Get current workspace
workspace = context.window.workspace

# Iterate areas
for area in context.screen.areas:
    if area.type == 'VIEW_3D':
        # Access 3D view settings
        for space in area.spaces:
            if space.type == 'VIEW_3D':
                space.shading.type = 'SOLID'

# Split area
with context.temp_override(area=area):
    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)

# Create new workspace
bpy.ops.workspace.duplicate()
new_workspace = context.window.workspace
new_workspace.name = "My Workspace"
```

### Registration Pattern
```python
classes = [
    MyProperties,
    MY_OT_operator,
    MY_PT_panel,
    MY_UL_list,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    
    # Add properties
    bpy.types.Scene.my_props = PointerProperty(type=MyProperties)
    
    # Add to menus
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)

def unregister():
    # Remove from menus
    bpy.types.VIEW3D_MT_mesh_add.remove(menu_func)
    
    # Remove properties
    del bpy.types.Scene.my_props
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
```

## Asset Browser & Pose Assets

```python
# Mark action as asset
action = bpy.data.actions["MyPose"]
action.asset_mark()
action.asset_data.description = "Character pose"

# Add tags
action.asset_data.tags.new("character")
action.asset_data.tags.new("standing")

# Generate preview
action.asset_generate_preview()

# Clear asset status
action.asset_clear()

# Get all pose assets
pose_assets = [a for a in bpy.data.actions if a.asset_data]
```

## Custom Space Type (Advanced)

**Note**: Creating truly custom Space types requires modifying Blender's C++ source code. Addons can only use existing space types. However, you can create the appearance of a custom editor:

```python
# Best approach: Use existing space with custom context
class MY_PT_main(Panel):
    bl_space_type = 'PROPERTIES'  # or 'NODE_EDITOR'
    bl_region_type = 'WINDOW'
    bl_context = "scene"  # Properties editor context
    
    # Hide in normal properties editor
    @classmethod
    def poll(cls, context):
        # Show only in specific workspace or with specific flag
        return context.workspace.name == "My Custom Editor"
```

## Tips & Best Practices

1. **Always check if data exists before accessing**:
```python
if obj and obj.animation_data and obj.animation_data.action:
    action = obj.animation_data.action
```

2. **Use try/except for file operations**:
```python
try:
    with open(filepath, 'r') as f:
        data = f.read()
except Exception as e:
    self.report({'ERROR'}, f"Failed to read file: {e}")
```

3. **Batch operations for performance**:
```python
# Bad: Individual updates
for i in range(100):
    obj.location.x = i
    bpy.context.view_layer.update()

# Good: Batch update
for i in range(100):
    obj.location.x = i
bpy.context.view_layer.update()  # Update once at end
```

4. **Use context.temp_override for specific operations**:
```python
with context.temp_override(active_object=obj):
    bpy.ops.object.shade_smooth()
```

5. **Report operator status**:
```python
self.report({'INFO'}, "Success")     # Info message
self.report({'WARNING'}, "Warning")  # Warning
self.report({'ERROR'}, "Failed")     # Error
```