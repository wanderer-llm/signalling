"""
Railway track layout - the foundation of the signalling system.
"""

from dataclasses import dataclass
from typing import Dict, List, Set, Optional
from enum import Enum


class TrackType(Enum):
    STANDARD = "standard"
    PASSING_LOOPSIDE = "passing_loopside"
    PASSING_MAINLINE = "passing_mainline"
    SIDING = "siding"
    SHUNT = "shunt"


class JunctionType(Enum):
    CROSSING = "crossing"
    DIVERGENCE = "divergence"
    CONVERGENCE = "convergence"
    INTERSECTION = "intersection"


@dataclass
class Track:
    """A track section between two junctions/stations."""
    name: str
    start: str
    end: str
    track_type: TrackType = TrackType.STANDARD
    is_bidirectional: bool = True
    length_meters: float = 100.0
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, Track):
            return False
        return self.name == other.name


@dataclass
class Junction:
    """A point where tracks meet."""
    name: str
    junction_type: JunctionType = JunctionType.CROSSING
    coordinates: tuple = (0.0, 0.0)
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, Junction):
            return False
        return self.name == other.name


@dataclass
class Station:
    """A station with platforms."""
    name: str
    platform_count: int = 1
    platform_length_meters: float = 200.0
    coordinates: tuple = (0.0, 0.0)
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, Station):
            return False
        return self.name == other.name


class RailwayNetwork:
    """A railway network consisting of tracks, junctions, and stations."""
    
    def __init__(self):
        self.tracks: Dict[str, Track] = {}
        self.junctions: Dict[str, Junction] = {}
        self.stations: Dict[str, Station] = {}
        self._junction_ids: Set[str] = set()
        self._station_names: Set[str] = set()
    
    def add_junction(self, name: str, junction_type: JunctionType = JunctionType.CROSSING) -> Junction:
        """Add a junction to the network."""
        if name in self.junctions:
            return self.junctions[name]
        
        junction = Junction(name=name, junction_type=junction_type)
        self.junctions[name] = junction
        self._junction_ids.add(name)
        return junction
    
    def add_station(self, name: str, platform_count: int = 1, 
                    platform_length: float = 200.0) -> Station:
        """Add a station to the network."""
        if name in self.stations or name in self._station_names:
            return self.stations[name]
        
        station = Station(name=name, platform_count=platform_count,
                         platform_length_meters=platform_length)
        self.stations[name] = station
        self._station_names.add(name)
        return station
    
    def add_track(self, name: str, start: str, end: str,
                  track_type: TrackType = TrackType.STANDARD,
                  bidirectional: bool = True,
                  length_meters: float = 100.0) -> Track:
        """Add a track section between two junctions/stations."""
        if name in self.tracks:
            return self.tracks[name]
        
        track = Track(name=name, start=start, end=end,
                      track_type=track_type, is_bidirectional=bidirectional,
                      length_meters=length_meters)
        self.tracks[name] = track
        return track
    
    def get_adjacent_tracks(self, location: str) -> List[Track]:
        """Get all tracks connected to a junction or station."""
        adjacent = []
        for track in self.tracks.values():
            if track.start == location or track.end == location:
                adjacent.append(track)
        return adjacent
    
    def get_tracks_at(self, location: str) -> List[Track]:
        """Get tracks where the location is either start or end."""
        return self.get_adjacent_tracks(location)
    
    def find_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find a path between two locations (BFS)."""
        if start not in self._junction_ids and start not in self._station_names:
            return None
        
        if end not in self._junction_ids and end not in self._station_names:
            return None
        
        visited: Set[str] = set()
        queue: List[List[str]] = [[start]]
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            if current == end:
                return path
            
            if current in visited:
                continue
            visited.add(current)
            
            for track in self.get_adjacent_tracks(current):
                neighbor = track.end if track.start == current else track.start
                if neighbor not in visited:
                    new_path = path + [neighbor]
                    queue.append(new_path)
        
        return None
    
    def __repr__(self):
        return f"RailwayNetwork({len(self.tracks)} tracks, {len(self.junctions)} junctions, {len(self.stations)} stations)"


def create_simple_network() -> RailwayNetwork:
    """Create a simple railway network for testing."""
    network = RailwayNetwork()
    
    network.add_station("central", platform_count=2, platform_length=300.0)
    network.add_station("north", platform_count=1, platform_length=200.0)
    network.add_station("south", platform_count=1, platform_length=200.0)
    network.add_station("east", platform_count=1, platform_length=200.0)
    network.add_station("west", platform_count=1, platform_length=200.0)
    
    network.add_junction("central_north")
    network.add_junction("central_south")
    network.add_junction("central_east")
    network.add_junction("central_west")
    
    network.add_track("n-central", "north", "central_north", TrackType.STANDARD)
    network.add_track("s-central", "south", "central_south", TrackType.STANDARD)
    network.add_track("e-central", "east", "central_east", TrackType.STANDARD)
    network.add_track("w-central", "west", "central_west", TrackType.STANDARD)
    
    network.add_track("c-n", "central_north", "central", TrackType.STANDARD)
    network.add_track("c-s", "central_south", "central", TrackType.STANDARD)
    network.add_track("c-e", "central_east", "central", TrackType.STANDARD)
    network.add_track("c-w", "central_west", "central", TrackType.STANDARD)
    
    return network


if __name__ == "__main__":
    # Test the simple network
    network = create_simple_network()
    print(network)
    print("\nStations:", list(network.stations.keys()))
    print("Junctions:", list(network.junctions.keys()))
    print("Tracks:", list(network.tracks.keys()))
    
    # Test path finding
    path = network.find_path("north", "east")
    print(f"\nPath from north to east: {path}")
