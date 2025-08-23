"""Video rendering module for headless animation export."""

from pathlib import Path
from datetime import datetime
from typing import Optional
from .models import HeadlessConfig
from .const import (
    VIDEO_CODEC, VIDEO_CONTAINER, VIDEO_QUALITY,
    RENDER_RESOLUTION_X, RENDER_RESOLUTION_Y, 
    RENDER_RESOLUTION_PERCENTAGE, DEFAULT_FPS
)


class VideoRenderer:
    """Handle video rendering with audio synchronization."""
    
    def __init__(self, config: HeadlessConfig):
        self.config = config
        
        # Import bpy only when needed (in Blender context)
        try:
            import bpy
            self.bpy = bpy
        except ImportError:
            self.bpy = None
        
    def setup_render_scene(self, char_file: str, action_name: str) -> bool:
        """Setup scene for rendering with character and action.
        
        Args:
            char_file: Path to character blend file
            action_name: Name of action to apply
            
        Returns:
            True if setup successful, False otherwise
        """
        # Clear existing scene
        self.bpy.ops.wm.read_homefile(use_empty=True)
        
        # Link character from file
        try:
            with self.bpy.data.libraries.load(char_file, link=False) as (data_from, data_to):
                # Find character collection
                char_collection = None
                char_name = Path(char_file).stem  # Use filename as hint
                
                print(f"Looking for character collection. File stem: {char_name}")
                print(f"Available collections: {list(data_from.collections)}")
                
                # First try exact match (case-insensitive) with base name
                base_name = char_name.split('-')[0]  # Get first part before hyphen
                for coll_name in data_from.collections:
                    if coll_name.lower() == base_name.lower():
                        data_to.collections.append(coll_name)
                        char_collection = coll_name
                        print(f"Found exact match collection: {coll_name}")
                        break
                
                # If no exact match, try contains match
                if not char_collection:
                    for coll_name in data_from.collections:
                        if base_name.lower() in coll_name.lower() and '.' not in coll_name:
                            # Avoid nested collections like "Refs.Dobby"
                            data_to.collections.append(coll_name)
                            char_collection = coll_name
                            print(f"Found matching collection: {coll_name}")
                            break
                
                if not char_collection and data_from.collections:
                    # Fallback to first collection
                    data_to.collections.append(data_from.collections[0])
                    char_collection = data_from.collections[0]
                    print(f"Using fallback collection: {char_collection}")
            
            # Link collection to scene
            if char_collection and char_collection in self.bpy.data.collections:
                scene_collection = self.bpy.context.scene.collection
                scene_collection.children.link(self.bpy.data.collections[char_collection])
            else:
                print(f"Error: Could not find character collection in {char_file}")
                return False
            
            # Find armature in the collection
            armature = None
            print(f"Searching for armature in collection: {char_collection}")
            collection_objects = list(self.bpy.data.collections[char_collection].objects)
            print(f"Objects in collection: {[(obj.name, obj.type) for obj in collection_objects]}")
            
            for obj in collection_objects:
                if obj.type == 'ARMATURE':
                    armature = obj
                    print(f"Found armature: {armature.name}")
                    break
            
            if not armature:
                print(f"Error: No armature found in character collection '{char_collection}'")
                print(f"Available objects: {collection_objects}")
                return False
            
            # Set armature as active
            self.bpy.context.view_layer.objects.active = armature
            armature.select_set(True)
            
            # Load the action from the output blend file
            with self.bpy.data.libraries.load(self.config.form.blendFileToOutputAction, link=False) as (data_from, data_to):
                if action_name in data_from.actions:
                    data_to.actions.append(action_name)
            
            # Apply action to armature
            if action_name in self.bpy.data.actions:
                armature.animation_data_create()
                armature.animation_data.action = self.bpy.data.actions[action_name]
            else:
                print(f"Error: Action '{action_name}' not found")
                return False
            
            # Setup camera
            self.setup_camera()
            
            # Setup lighting
            self.setup_lighting()
            
            return True
            
        except Exception as e:
            print(f"Error setting up render scene: {e}")
            return False
    
    def setup_camera(self):
        """Setup a reasonable camera angle."""
        # Create camera if not exists
        if 'Camera' not in self.bpy.data.objects:
            cam_data = self.bpy.data.cameras.new('Camera')
            cam = self.bpy.data.objects.new('Camera', cam_data)
            self.bpy.context.scene.collection.objects.link(cam)
        else:
            cam = self.bpy.data.objects['Camera']
        
        # Position camera
        cam.location = (7, -7, 5)
        cam.rotation_euler = (1.1, 0, 0.785)  # ~63°, 0°, 45°
        
        # Set as active camera
        self.bpy.context.scene.camera = cam
    
    def setup_lighting(self):
        """Setup basic lighting for the scene."""
        # Create sun light
        if 'Sun' not in self.bpy.data.objects:
            light_data = self.bpy.data.lights.new('Sun', 'SUN')
            light_data.energy = 1.0
            light = self.bpy.data.objects.new('Sun', light_data)
            self.bpy.context.scene.collection.objects.link(light)
        else:
            light = self.bpy.data.objects['Sun']
        
        # Position light
        light.location = (5, 5, 10)
        light.rotation_euler = (0.6, 0.2, 0)
        
        # Add ambient light (world settings)
        if not self.bpy.context.scene.world:
            # Create a world if it doesn't exist
            world = self.bpy.data.worlds.new("World")
            self.bpy.context.scene.world = world
            world.use_nodes = True
        
        if self.bpy.context.scene.world and self.bpy.context.scene.world.node_tree:
            bg_node = self.bpy.context.scene.world.node_tree.nodes.get("Background")
            if bg_node:
                bg_node.inputs[0].default_value = (0.1, 0.1, 0.1, 1.0)
    
    def load_audio(self, audio_file: str):
        """Load audio file into the video sequence editor."""
        # Ensure sequence editor exists
        if not self.bpy.context.scene.sequence_editor:
            self.bpy.context.scene.sequence_editor_create()
        
        seq_editor = self.bpy.context.scene.sequence_editor
        
        # Clear existing strips
        for strip in seq_editor.sequences:
            seq_editor.sequences.remove(strip)
        
        # Add audio strip
        audio_strip = seq_editor.sequences.new_sound(
            name="Audio",
            filepath=audio_file,
            channel=1,
            frame_start=1
        )
        
        # Set scene end frame to match audio duration
        if audio_strip:
            self.bpy.context.scene.frame_end = int(audio_strip.frame_final_duration)
    
    def configure_render_settings(self, output_path: str):
        """Configure render settings for video output."""
        scene = self.bpy.context.scene
        
        # Resolution
        scene.render.resolution_x = RENDER_RESOLUTION_X
        scene.render.resolution_y = RENDER_RESOLUTION_Y
        scene.render.resolution_percentage = RENDER_RESOLUTION_PERCENTAGE
        
        # Frame rate
        scene.render.fps = DEFAULT_FPS
        
        # Output format
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = VIDEO_CONTAINER.upper()
        scene.render.ffmpeg.codec = VIDEO_CODEC.upper() if VIDEO_CODEC.upper() != 'H264' else 'H264'
        
        # Quality
        if VIDEO_QUALITY == 'HIGH':
            scene.render.ffmpeg.constant_rate_factor = 'HIGH'
            scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        elif VIDEO_QUALITY == 'LOW':
            scene.render.ffmpeg.constant_rate_factor = 'LOWEST'
            scene.render.ffmpeg.ffmpeg_preset = 'REALTIME'
        else:  # MEDIUM
            scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
            scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
        
        # Audio
        scene.render.ffmpeg.audio_codec = 'AAC'
        scene.render.ffmpeg.audio_bitrate = 192
        
        # Output path
        scene.render.filepath = output_path
    
    def render(self) -> Optional[str]:
        """Render the video with audio.
        
        Returns:
            Path to rendered video file, or None if failed
        """
        if not self.config.form.shouldCreateVideo:
            print("Video rendering not requested")
            return None
        
        if not self.config.form.charFile or not self.config.form.audioFile:
            print("Missing character file or audio file for video rendering")
            return None
        
        # Create temp blend file for rendering
        temp_blend = Path("temp_render.blend")
        
        # Setup render scene
        if not self.setup_render_scene(
            self.config.form.charFile, 
            self.config.form.actionNameToCreate
        ):
            print("Failed to setup render scene")
            return None
        
        # Load audio
        self.load_audio(self.config.form.audioFile)
        
        # Generate output filename
        char_name = Path(self.config.form.charFile).stem
        timestamp = datetime.now().strftime("%y-%m-%d-%H-%M-%S")
        output_filename = f"{timestamp}-{char_name}-{self.config.form.actionNameToCreate}.mp4"
        output_path = Path(self.config.form.renderDir) / output_filename
        
        # Configure render settings
        self.configure_render_settings(str(output_path))
        
        # Save temp blend file
        self.bpy.ops.wm.save_as_mainfile(filepath=str(temp_blend))
        
        # Render animation
        print(f"Rendering video to: {output_path}")
        try:
            self.bpy.ops.render.render(animation=True)
            print(f"Video rendered successfully: {output_path}")
            return str(output_path)
        except Exception as e:
            print(f"Render failed: {e}")
            return None
        finally:
            # Cleanup temp file
            if temp_blend.exists():
                temp_blend.unlink()