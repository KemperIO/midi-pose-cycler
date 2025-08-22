"""Pose catalog finder for Blender pose libraries."""

from pathlib import Path
from typing import List, Optional, Dict, Set


class PoseCatalogFinder:
    """Find and manage pose catalogs in Blender files."""
    
    @staticmethod
    def find_catalog_in_library(pose_lib, catalog_name: str) -> Optional[List[str]]:
        """Find a pose catalog (folder) within a pose library and return its poses.
        
        Args:
            pose_lib: The Blender Action containing poses
            catalog_name: Name of the catalog/folder to find
            
        Returns:
            List of pose names in the catalog, or None if not found
        """
        if not pose_lib or not pose_lib.pose_markers:
            return None
        
        # Get all pose markers
        markers = pose_lib.pose_markers
        catalog_poses = []
        
        # Check if catalog_name matches any pose library asset catalog
        for marker in markers:
            # In Blender 4.5, pose catalogs are managed differently
            # We'll look for poses that might be prefixed with the catalog name
            # or check asset catalogs if available
            if catalog_name.lower() in marker.name.lower():
                catalog_poses.append(marker.name)
        
        if catalog_poses:
            # Sort alphabetically as specified
            catalog_poses.sort()
            return catalog_poses
        
        return None
    
    @staticmethod
    def find_all_catalogs_in_file(blend_file_path: str) -> Dict[str, List[str]]:
        """Find all pose catalogs in a blend file.
        
        Args:
            blend_file_path: Path to the blend file
            
        Returns:
            Dictionary mapping catalog names to lists of poses
        """
        catalogs = {}
        
        # This needs to be run within Blender context
        # We'll handle the actual loading in the main script
        # For now, return structure
        return catalogs
    
    @staticmethod  
    def find_catalog_recursive(root_action, catalog_name: str) -> Optional[str]:
        """Find a catalog name recursively in pose library structure.
        
        Args:
            root_action: Root action/pose library
            catalog_name: Name to search for
            
        Returns:
            Full path to catalog if found, None otherwise
        """
        # In Blender 4.5, asset catalogs are organized differently
        # This would need to interface with the asset browser system
        # For simplicity, we'll use a name-based approach
        
        if not root_action:
            return None
            
        # Check direct match
        if catalog_name in root_action.name:
            return root_action.name
            
        # Check pose markers for catalog-like naming
        for marker in root_action.pose_markers:
            parts = marker.name.split('/')
            if catalog_name in parts or catalog_name in marker.name:
                return marker.name
        
        return None
    
    @staticmethod
    def get_poses_from_catalog(blend_file: str, catalog_path: str) -> List[str]:
        """Get all poses from a specific catalog.
        
        Args:
            blend_file: Path to blend file
            catalog_path: Path/name of the catalog
            
        Returns:
            List of pose names, sorted alphabetically
        """
        poses = []
        
        # This will be implemented in the Blender context
        # For now return empty list
        return poses
    
    @staticmethod
    def validate_no_bone_conflicts(catalogs: Dict[str, List[str]], 
                                  blend_file: str) -> Optional[str]:
        """Check if different catalogs use overlapping bones.
        
        Args:
            catalogs: Dict of catalog names to pose lists
            blend_file: Path to blend file to check bones
            
        Returns:
            Error message if conflicts found, None if all good
        """
        # This needs to be checked within Blender context
        # by examining the actual pose data
        # For now, return None (no conflicts)
        return None
    
    @staticmethod
    def get_bone_names_for_pose(action, pose_name: str) -> Set[str]:
        """Get all bone names affected by a pose.
        
        Args:
            action: The action containing the pose
            pose_name: Name of the pose
            
        Returns:
            Set of bone names
        """
        bones = set()
        
        # Find the pose marker
        marker = None
        for m in action.pose_markers:
            if m.name == pose_name:
                marker = m
                break
        
        if not marker:
            return bones
        
        # Get frame of the pose
        frame = marker.frame
        
        # Check all FCurves at this frame
        for fcurve in action.fcurves:
            # FCurve data paths are like: pose.bones["BoneName"].location
            if 'pose.bones[' in fcurve.data_path:
                # Extract bone name
                start = fcurve.data_path.find('["') + 2
                end = fcurve.data_path.find('"]', start)
                if start > 1 and end > start:
                    bone_name = fcurve.data_path[start:end]
                    
                    # Check if this fcurve has a keyframe at the pose frame
                    for keyframe in fcurve.keyframe_points:
                        if abs(keyframe.co[0] - frame) < 0.01:  # Frame match
                            bones.add(bone_name)
                            break
        
        return bones