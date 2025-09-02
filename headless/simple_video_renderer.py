"""Simplified video renderer for proof of concept."""

from pathlib import Path
from datetime import datetime
from typing import Optional
import shutil


class SimpleVideoRenderer:
    """Simplified video renderer that works directly in character file."""
    
    def __init__(self, config):
        self.config = config
        
        # Import bpy only when in Blender context
        try:
            import bpy
            self.bpy = bpy
        except ImportError:
            self.bpy = None
    
    def render(self) -> Optional[str]:
        """Render video using simplified approach."""
        if not self.bpy or not self.config.form.shouldCreateVideo:
            return None
        
        print("\n" + "=" * 60)
        print("SIMPLE VIDEO RENDERER - PROOF OF CONCEPT")
        print("=" * 60)
        
        # Step 1: Copy character file to work with
        char_file = Path(self.config.form.charFile)
        timestamp = datetime.now().strftime("%H%M%S")
        work_file = Path("headless_test") / f"render_{timestamp}.blend"
        work_file.parent.mkdir(exist_ok=True)
        
        print(f"\n1. Creating working copy:")
        print(f"   From: {char_file}")
        print(f"   To: {work_file}")
        shutil.copy2(char_file, work_file)
        
        # Step 2: Open the working file
        print(f"\n2. Opening working file...")
        self.bpy.ops.wm.open_mainfile(filepath=str(work_file))
        
        # Step 3: Load the generated action
        action_file = Path(self.config.form.blendFileToOutputAction)
        action_name = self.config.form.actionNameToCreate
        
        print(f"\n3. Loading action '{action_name}' from {action_file}")
        
        # Check if action file exists
        if not action_file.exists():
            print(f"   ERROR: Action file not found: {action_file}")
            return None
        
        with self.bpy.data.libraries.load(str(action_file), link=False) as (data_from, data_to):
            if action_name in data_from.actions:
                data_to.actions.append(action_name)
                print(f"   ✓ Action loaded")
            else:
                print(f"   ERROR: Action '{action_name}' not found")
                print(f"   Available: {list(data_from.actions)[:5]}")
                return None
        
        # Step 4: Find armature and apply action
        print(f"\n4. Finding armature and applying action...")
        armature = None
        for obj in self.bpy.data.objects:
            if obj.type == 'ARMATURE':
                armature = obj
                print(f"   Found armature: {obj.name}")
                break
        
        if not armature:
            print("   ERROR: No armature found")
            return None
        
        # Apply the action
        if action_name not in self.bpy.data.actions:
            print(f"   ERROR: Action '{action_name}' not in data after loading")
            return None
        
        action = self.bpy.data.actions[action_name]
        
        # Create animation data if needed
        if not armature.animation_data:
            armature.animation_data_create()
        
        # Assign the action
        armature.animation_data.action = action
        print(f"   ✓ Action applied to {armature.name}")
        
        # Step 5: Set frame range
        print(f"\n5. Setting frame range...")
        
        # Calculate frame range from action's fcurves
        frame_min = float('inf')
        frame_max = float('-inf')
        
        for fcurve in action.fcurves:
            for keyframe in fcurve.keyframe_points:
                frame_min = min(frame_min, keyframe.co[0])
                frame_max = max(frame_max, keyframe.co[0])
        
        if frame_min != float('inf'):
            # For POC, limit frames but show what full duration would be
            actual_start = int(frame_min)
            actual_end = int(frame_max)
            
            # POC limit
            poc_limit = 48  # 2 seconds at 24fps
            limited_end = min(actual_end, actual_start + poc_limit - 1)
            
            self.bpy.context.scene.frame_start = actual_start
            self.bpy.context.scene.frame_end = limited_end
            
            print(f"   Action frame range: {actual_start} - {actual_end}")
            print(f"   Action duration: {(actual_end - actual_start + 1) / 24:.2f} seconds at 24fps")
            print(f"   POC render range: {actual_start} - {limited_end}")
            print(f"   POC duration: {(limited_end - actual_start + 1) / 24:.2f} seconds")
            
            if actual_end > limited_end:
                print(f"   (Limited to {poc_limit} frames for POC testing)")
        else:
            # Default to 24 frames if no keyframes found
            self.bpy.context.scene.frame_start = 1
            self.bpy.context.scene.frame_end = 24
            print(f"   Using default: 1 - 24")
        
        # Step 6: Load audio (if provided)
        if self.config.form.audioFile:
            print(f"\n6. Loading audio: {self.config.form.audioFile}")
            
            if not self.bpy.context.scene.sequence_editor:
                self.bpy.context.scene.sequence_editor_create()
            
            seq = self.bpy.context.scene.sequence_editor
            
            # Clear existing audio strips
            for strip in list(seq.sequences):
                if strip.type == 'SOUND':
                    seq.sequences.remove(strip)
            
            # Add new audio
            audio_strip = seq.sequences.new_sound(
                name="Audio",
                filepath=self.config.form.audioFile,
                channel=1,
                frame_start=1
            )
            
            if audio_strip:
                # Don't override frame range for testing
                # self.bpy.context.scene.frame_end = int(audio_strip.frame_final_duration)
                print(f"   ✓ Audio loaded (but keeping limited frame range for testing)")
        
        # Step 7: Setup basic render settings
        print(f"\n7. Configuring render settings...")
        scene = self.bpy.context.scene
        
        # Set render engine to EEVEE for faster rendering
        scene.render.engine = 'BLENDER_EEVEE_NEXT'
        
        # Reduce samples to minimum for speed
        scene.eevee.taa_render_samples = 1  # Minimum samples
        scene.eevee.taa_samples = 1  # Viewport samples
        
        # Resolution - very low for testing
        scene.render.resolution_x = 320
        scene.render.resolution_y = 240
        scene.render.resolution_percentage = 100
        
        # Output format
        scene.render.image_settings.file_format = 'FFMPEG'
        scene.render.ffmpeg.format = 'MPEG4'
        scene.render.ffmpeg.codec = 'H264'
        scene.render.ffmpeg.audio_codec = 'AAC'
        
        # Output path
        timestamp = datetime.now().strftime("%y%m%d_%H%M%S")
        output_file = Path(self.config.form.renderDir) / f"test_{timestamp}.mp4"
        output_file.parent.mkdir(exist_ok=True)
        scene.render.filepath = str(output_file)
        
        print(f"   Resolution: {scene.render.resolution_x}x{scene.render.resolution_y} @ {scene.render.resolution_percentage}%")
        print(f"   Output: {output_file}")
        
        # Step 8: Save the working file for inspection
        save_path = work_file.with_suffix('.ready.blend')
        self.bpy.ops.wm.save_as_mainfile(filepath=str(save_path))
        print(f"\n8. Saved working file: {save_path}")
        
        # Step 9: Render
        print(f"\n9. Starting render...")
        print("   This may take a while...")
        
        try:
            self.bpy.ops.render.render(animation=True)
            print(f"   ✓ Render complete!")
            
            # Check if file was created
            if output_file.exists():
                size_mb = output_file.stat().st_size / (1024 * 1024)
                print(f"   ✓ Video file created: {output_file}")
                print(f"   Size: {size_mb:.2f} MB")
                return str(output_file)
            else:
                print(f"   ERROR: Video file not created")
                return None
                
        except Exception as e:
            print(f"   ERROR during render: {e}")
            import traceback
            traceback.print_exc()
            return None