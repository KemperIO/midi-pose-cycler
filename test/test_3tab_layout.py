"""
Test 3-tab N-pane layout functionality
Verifies all tabs and panels are registered correctly
"""

import bpy
import sys

def main():
    """Test the 3-tab layout structure"""
    print("\n" + "="*60)
    print("Testing 3-Tab N-Pane Layout")
    print("="*60)
    
    # Register addon
    addon_name = "midi-pose-cycler"
    try:
        bpy.ops.preferences.addon_enable(module=addon_name)
        print(f"✓ Addon '{addon_name}' enabled")
    except Exception as e:
        print(f"✗ Failed to enable addon: {e}")
        return False
    
    # Test MPC-Run tab panels
    print("\n--- MPC-Run Tab ---")
    run_panels = [
        'MIDIPOSE_PT_run_main',
        'MIDIPOSE_PT_run_action',
        'MIDIPOSE_PT_run_timing',
        'MIDIPOSE_PT_run_preview',
        'MIDIPOSE_PT_run_config'
    ]
    
    for panel_id in run_panels:
        if hasattr(bpy.types, panel_id):
            panel = getattr(bpy.types, panel_id)
            if hasattr(panel, 'bl_category'):
                print(f"✓ {panel_id} (Tab: {panel.bl_category})")
            else:
                print(f"✗ {panel_id} missing bl_category")
                return False
        else:
            print(f"✗ Panel missing: {panel_id}")
            return False
    
    # Test MPC-Pose tab panels
    print("\n--- MPC-Pose Tab ---")
    pose_panels = [
        'MIDIPOSE_PT_pose_selection',
        'MIDIPOSE_PT_pose_order',
        'MIDIPOSE_PT_pose_cycle'
    ]
    
    for panel_id in pose_panels:
        if hasattr(bpy.types, panel_id):
            panel = getattr(bpy.types, panel_id)
            print(f"✓ {panel_id} (Tab: {panel.bl_category})")
        else:
            print(f"✗ Panel missing: {panel_id}")
            return False
    
    # Test MPC-MIDI tab panels
    print("\n--- MPC-MIDI Tab ---")
    midi_panels = [
        'MIDIPOSE_PT_midi_file',
        'MIDIPOSE_PT_midi_tracks',
        'MIDIPOSE_PT_midi_notes'
    ]
    
    for panel_id in midi_panels:
        if hasattr(bpy.types, panel_id):
            panel = getattr(bpy.types, panel_id)
            print(f"✓ {panel_id} (Tab: {panel.bl_category})")
        else:
            print(f"✗ Panel missing: {panel_id}")
            return False
    
    print("\n" + "="*60)
    print("✓ All 3 tabs and panels registered correctly!")
    print("="*60)
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)