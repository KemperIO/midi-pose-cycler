#!/usr/bin/env python3
"""Minimal rendering test with just a cube to isolate rendering issues."""

import sys
from pathlib import Path

def main():
    """Test minimal rendering with cube."""
    try:
        import bpy
    except ImportError:
        print("Error: Must run within Blender")
        return False
    
    print("\n" + "="*60)
    print("MINIMAL RENDER TEST - ISOLATING RENDERING ISSUES")
    print("="*60)
    
    # Step 1: Clear scene and create minimal test
    print("\n1. Creating minimal test scene...")
    
    # Clear all objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Add a simple cube
    bpy.ops.mesh.primitive_cube_add(location=(0, 0, 0))
    cube = bpy.context.object
    print(f"   Created cube: {cube.name}")
    
    # Add simple animation
    cube.location = (0, 0, 0)
    cube.keyframe_insert(data_path="location", frame=1)
    
    cube.location = (5, 0, 0)
    cube.keyframe_insert(data_path="location", frame=24)
    
    cube.location = (0, 0, 0)
    cube.keyframe_insert(data_path="location", frame=48)
    
    print("   Added simple animation (48 frames)")
    
    # Step 2: Add camera if missing
    camera = None
    for obj in bpy.data.objects:
        if obj.type == 'CAMERA':
            camera = obj
            break
    
    if not camera:
        bpy.ops.object.camera_add(location=(7, -7, 5))
        camera = bpy.context.object
        camera.rotation_euler = (1.1, 0, 0.785)
        print(f"   Added camera: {camera.name}")
    
    bpy.context.scene.camera = camera
    
    # Step 3: Add light
    bpy.ops.object.light_add(type='SUN', location=(5, 5, 10))
    light = bpy.context.object
    print(f"   Added light: {light.name}")
    
    # Step 4: Configure minimal render settings
    print("\n2. Configuring render settings...")
    scene = bpy.context.scene
    
    # Use EEVEE for speed
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
    
    # Reduce samples for faster rendering
    scene.eevee.taa_render_samples = 1  # Minimum samples
    scene.eevee.taa_samples = 1  # Viewport samples
    
    # Very small resolution for testing
    scene.render.resolution_x = 320
    scene.render.resolution_y = 240
    scene.render.resolution_percentage = 100
    
    # Frame range - just 10 frames for quick test
    scene.frame_start = 1
    scene.frame_end = 10
    
    # Output format - try PNG sequence first
    scene.render.image_settings.file_format = 'PNG'
    
    # Output path
    output_dir = Path("headless_test") / "minimal_render"
    output_dir.mkdir(exist_ok=True, parents=True)
    scene.render.filepath = str(output_dir / "frame_")
    
    print(f"   Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
    print(f"   Frames: {scene.frame_start} to {scene.frame_end}")
    print(f"   Samples: {scene.eevee.taa_render_samples}")
    print(f"   Output: {scene.render.filepath}####.png")
    
    # Step 5: Test single frame render first
    print("\n3. Testing single frame render...")
    scene.frame_set(24)
    single_frame = output_dir / "test_single.png"
    scene.render.filepath = str(single_frame)
    
    try:
        bpy.ops.render.render(write_still=True)
        
        if single_frame.exists():
            size_kb = single_frame.stat().st_size / 1024
            print(f"   ✓ Single frame rendered: {size_kb:.1f} KB")
            
            if size_kb < 1:
                print("   WARNING: Frame file is too small")
        else:
            print("   ✗ Single frame file not created")
    except Exception as e:
        print(f"   ✗ Single frame render failed: {e}")
        return False
    
    # Step 6: Try animation render with PNG sequence
    print("\n4. Testing animation render (PNG sequence)...")
    scene.render.filepath = str(output_dir / "anim_")
    
    try:
        # Render animation
        bpy.ops.render.render(animation=True)
        
        # Check for output files
        png_files = list(output_dir.glob("anim_*.png"))
        if png_files:
            print(f"   ✓ Created {len(png_files)} PNG frames")
            
            # Check first frame size
            first_frame = png_files[0]
            size_kb = first_frame.stat().st_size / 1024
            print(f"   First frame size: {size_kb:.1f} KB")
            
            if size_kb < 1:
                print("   WARNING: Frames are too small")
                return False
        else:
            print("   ✗ No PNG frames created")
            return False
            
    except Exception as e:
        print(f"   ✗ Animation render failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 7: Now try video format
    print("\n5. Testing video render (MP4)...")
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    
    video_file = output_dir / "test_minimal.mp4"
    scene.render.filepath = str(video_file)
    
    try:
        bpy.ops.render.render(animation=True)
        
        if video_file.exists():
            size_kb = video_file.stat().st_size / 1024
            print(f"   ✓ Video created: {size_kb:.1f} KB")
            
            if size_kb < 10:
                print("   WARNING: Video file is suspiciously small")
                
                # Try OpenGL render as alternative
                print("\n6. Trying OpenGL viewport render...")
                opengl_file = output_dir / "test_opengl.mp4"
                scene.render.filepath = str(opengl_file)
                
                # Get 3D viewport
                for area in bpy.context.screen.areas:
                    if area.type == 'VIEW_3D':
                        # Override context for viewport render
                        override = {'area': area}
                        with bpy.context.temp_override(**override):
                            bpy.ops.render.opengl(animation=True, write_still=False)
                        break
                
                if opengl_file.exists():
                    size_kb = opengl_file.stat().st_size / 1024
                    print(f"   ✓ OpenGL video: {size_kb:.1f} KB")
                else:
                    print("   ✗ OpenGL render didn't create file")
                    
                return False
            else:
                print("   ✓ Video has reasonable size!")
                return True
        else:
            print("   ✗ Video file not created")
            return False
            
    except Exception as e:
        print(f"   ✗ Video render failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Step 8: Save test blend for inspection
    blend_file = output_dir / "minimal_test.blend"
    bpy.ops.wm.save_as_mainfile(filepath=str(blend_file))
    print(f"\n7. Saved test file: {blend_file}")
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)