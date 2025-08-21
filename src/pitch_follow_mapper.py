"""
Pitch Follow Mapper for mapping MIDI tones to pose indices
"""
from typing import List, Optional, Tuple
try:
    from .tone import Tone
except ImportError:
    from tone import Tone

class PitchFollowMapper:
    """Maps MIDI tones to pose indices with bounce_out logic"""
    
    def __init__(self, lowest_tone: Tone, highest_tone: Tone):
        """Initialize with tone range
        
        Args:
            lowest_tone: Lowest tone in the MIDI data
            highest_tone: Highest tone in the MIDI data
        """
        if lowest_tone.value > highest_tone.value:
            raise ValueError(f"Lowest tone {lowest_tone} must be <= highest tone {highest_tone}")
        
        self.lowest_tone = lowest_tone
        self.highest_tone = highest_tone
        self.tone_range = highest_tone.value - lowest_tone.value
        self.last_pose_index: Optional[int] = None
    
    def map(self, tones: List[Tone], num_poses: int) -> List[int]:
        """Map tones to pose indices with bounce_out logic
        
        Args:
            tones: List of tones to map
            num_poses: Number of available poses
            
        Returns:
            List of pose indices (0-based)
            
        Raises:
            ValueError: If num_poses <= 1
        """
        if num_poses <= 1:
            raise ValueError(f"Need at least 2 poses for pitch follow, got {num_poses}")
        
        if not tones:
            return []
        
        result = []
        self.last_pose_index = None
        
        for tone in tones:
            # Calculate base pose index from pitch
            pose_index = self._calculate_pose_index(tone, num_poses)
            
            # Apply bounce_out if needed
            if self.last_pose_index is not None and pose_index == self.last_pose_index:
                pose_index = self._bounce_out(pose_index, num_poses)
            
            result.append(pose_index)
            self.last_pose_index = pose_index
        
        return result
    
    def _calculate_pose_index(self, tone: Tone, num_poses: int) -> int:
        """Calculate base pose index from tone pitch
        
        Maps tone linearly to pose range:
        - Lowest tone -> pose 0
        - Highest tone -> pose (num_poses - 1)
        """
        if self.tone_range == 0:
            # All tones are the same, use middle pose
            return num_poses // 2
        
        # Normalize tone to 0-1 range
        normalized = (tone.value - self.lowest_tone.value) / self.tone_range
        
        # Map to pose index
        pose_index = int(normalized * (num_poses - 1))
        
        # Clamp to valid range
        return max(0, min(pose_index, num_poses - 1))
    
    def _bounce_out(self, current_index: int, num_poses: int) -> int:
        """Bounce to nearest different pose
        
        Strategy:
        - If at lowest (0), bounce to 1
        - If at highest (num_poses-1), bounce to num_poses-2
        - Otherwise, bounce to closer edge (prefer up if equidistant)
        """
        if current_index == 0:
            # At lowest, bounce up
            return 1
        elif current_index == num_poses - 1:
            # At highest, bounce down
            return num_poses - 2
        else:
            # Middle pose - bounce to closer edge
            distance_to_low = current_index
            distance_to_high = (num_poses - 1) - current_index
            
            if distance_to_low < distance_to_high:
                # Closer to low, bounce down
                return current_index - 1
            else:
                # Closer to high or equidistant, bounce up
                return current_index + 1
    
    def get_tone_range_info(self) -> Tuple[str, str, int]:
        """Get information about the tone range
        
        Returns:
            Tuple of (lowest_name, highest_name, semitone_range)
        """
        return (
            self.lowest_tone.name,
            self.highest_tone.name,
            self.tone_range
        )