"""
Train movement and path finding.
"""

from typing import Dict, List, Optional, Tuple
from track import Track, Junction, RailwayNetwork
from signal import SignalLogic, SignalAspect


class Train:
    """A train moving through the railway network."""
    
    def __init__(self, name: str, network: RailwayNetwork, signal_logic: SignalLogic):
        self.name = name
        self.network = network
        self.signal_logic = signal_logic
        self.location: Optional[str] = None  # Current location (junction/station)
        self.on_track: Optional[str] = None  # Current track section (if on one)
        self.target: Optional[str] = None  # Target location
        self.path: List[str] = []  # Planned path of locations
        self._current_path_index: int = 0  # Which path segment to move to next
        self.moving: bool = False  # Whether train is currently moving
    
    @property
    def current_location(self) -> Optional[str]:
        """Get current location."""
        return self.location
    
    @property
    def current_track(self) -> Optional[str]:
        """Get current track section (if on one)."""
        return self.on_track
    
    @property
    def remaining_path(self) -> List[str]:
        """Get remaining path segments."""
        if self._current_path_index >= len(self.path):
            return []
        return self.path[self._current_path_index:]
    
    def find_path(self, start: str, end: str) -> List[str]:
        """Find a path from start to end through the network."""
        return self.network.find_path(start, end)
    
    def set_target(self, target: str):
        """Set a target location and compute path."""
        if self.location is None:
            raise ValueError("Train must be at a location before setting target")
        
        self.target = target
        
        # Find path from current location to target
        path = self.find_path(self.location, target)
        if path is None:
            raise ValueError(f"No path from {self.location} to {target}")
        
        # Remove start from path (it's already the current location)
        if len(path) > 1:
            self.path = path[1:]
        else:
            self.path = []
            self.moving = False  # Already at target
        
        self._current_path_index = 0
        if self.path:
            self.moving = True
    def move(self) -> bool:
        """Move the train to the next location in its path. Returns True if successful."""
        if not self.moving or not self.path:
            return False
        
        next_location = self.path[self._current_path_index]
        
        # Find a track from current location to next location
        adjacent_tracks = self.network.get_adjacent_tracks(self.location)
        found_track = None
        
        for track in adjacent_tracks:
            # Check if this track goes to the next location
            if track.end == next_location or track.start == next_location:
                # Check if the train can enter this track
                if self.signal_logic.can_enter_track(track.name):
                    found_track = track
                    break
        
        if found_track is None:
            return False  # No valid track found
        
        # Move onto the track
        self.signal_logic.occupy_track(found_track.name, self.name)
        self.on_track = found_track.name
        
        # Advance location
        if next_location == found_track.end:
            self.location = next_location
        else:
            self.location = found_track.start
        
        # Check if we've reached the target
        if self.location == self.target:
            self.moving = False
            self.path = []
        else:
            # Train is still moving, free the track it just left
            self.signal_logic.free_track(found_track.name)
        
        # Move to next path segment
        self._current_path_index += 1
        
        return True  # Move was successful
    
    def __repr__(self):
        status = "idle"
        if self.moving:
            status = "moving"
        elif self.location:
            status = f"at {self.location}"
        if self.on_track:
            status += f", on {self.on_track}"
        if self.target:
            status += f", target {self.target}"
        return f"Train({self.name}, {status})"


def create_train(name: str, network: RailwayNetwork, signal_logic: SignalLogic) -> Train:
    """Create a new train."""
    return Train(name, network, signal_logic)
