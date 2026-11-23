"""
Terminal visualization for the railway signalling system.
Displays the network state using ASCII art.
"""

from typing import Dict, List, Optional, Set, Tuple
from track import RailwayNetwork, Track, Junction, Station, TrackType
from signal import SignalLogic, SignalAspect
from train import Train


class Visualizer:
    """Visualizes the railway network in ASCII art."""
    
    def __init__(self, network: RailwayNetwork):
        self.network = network
    
    def render(self, trains: List[Train], signal_logic: SignalLogic) -> str:
        """Render the network state as ASCII art."""
        lines = []
        
        # Get all locations with coordinates
        locations = self._get_all_locations_with_coords()
        
        if not locations:
            return "No railway network to display."
        
        # Calculate grid bounds
        min_x, max_x, min_y, max_y = self._calculate_bounds(locations)
        
        # Add padding
        padding = 2
        width = max(1, int(max_x - min_x) + 2 * padding)
        height = max(1, int(max_y - min_y) + 2 * padding)
        
        # Create grid
        grid = [[" " for _ in range(width)] for _ in range(height)]
        
        # Place all elements
        self._place_junctions(grid, locations, min_x, min_y)
        self._place_stations(grid, locations, min_x, min_y)
        self._draw_tracks(grid, locations, min_x, min_y)
        self._add_signals(grid, signal_logic, locations, min_x, min_y)
        self._add_trains(grid, trains, locations, min_x, min_y, max_x, max_y)
        # Add header and footer
        lines.insert(0, "Railway Network State")
        lines.insert(1, "=" * 50)
        
        for row in grid:
            lines.append("".join(row))
        
        lines.append("=" * 50)
        
        return "\n".join(lines)
    
    def _get_all_locations_with_coords(self) -> List[Tuple[str, str, Tuple[float, float]]]:
        """Get all locations (junctions and stations) with their coordinates."""
        locations = []
        
        # Add junctions
        for name, junction in self.network.junctions.items():
            coords = getattr(junction, 'coordinates', (0.0, 0.0))
            locations.append(("junction", name, coords))
        
        # Add stations
        for name, station in self.network.stations.items():
            coords = getattr(station, 'coordinates', (0.0, 0.0))
            locations.append(("station", name, coords))
        
        return locations
    
    def _calculate_bounds(self, locations: List[Tuple[str, str, Tuple[float, float]]]) -> Tuple[float, float, float, float]:
        """Calculate the bounding box of all locations."""
        if not locations:
            return (0.0, 0.0, 0.0, 0.0)
        
        min_x = min(loc[2][0] for loc in locations)
        max_x = max(loc[2][0] for loc in locations)
        min_y = min(loc[2][1] for loc in locations)
        max_y = max(loc[2][1] for loc in locations)
        
        return (min_x, max_x, min_y, max_y)

    def _find_coords(self, locations: List[Tuple[str, str, Tuple[float, float]]], location_name: str):
        """Find the coordinates for a location by name."""
        for loc_type, name, coords in locations:
            if name == location_name:
                return coords
        return None
    def _place_junctions(self, grid: List[List[str]], locations: List[Tuple[str, str, Tuple[float, float]]], 
                         min_x: float, min_y: float):
        """Place junctions on the grid."""
        # Calculate coordinate ranges
        max_x = max(loc[2][0] for loc in locations)
        max_y = max(loc[2][1] for loc in locations)
        
        for loc_type, name, coords in locations:
            if loc_type == "junction":
                # Normalize coordinates to grid position
                x = int((coords[0] - min_x) / (max_x - min_x + 1e-9) * len(grid[0]))
                y = int((coords[1] - min_y) / (max_y - min_y + 1e-9) * len(grid))
                
                # Clamp to grid bounds
                x = max(0, min(x, len(grid[0]) - 1))
                y = max(0, min(y, len(grid) - 1))
                
                # Mark junction with "J"
                grid[y][x] = "J"

    def _place_stations(self, grid: List[List[str]], locations: List[Tuple[str, str, Tuple[float, float]]], 
                        min_x: float, min_y: float):
        """Place stations on the grid."""
        # Calculate coordinate ranges
        max_x = max(loc[2][0] for loc in locations)
        max_y = max(loc[2][1] for loc in locations)
        
        for loc_type, name, coords in locations:
            if loc_type == "station":
                # Normalize coordinates to grid position
                x = int((coords[0] - min_x) / (max_x - min_x + 1e-9) * len(grid[0]))
                y = int((coords[1] - min_y) / (max_y - min_y + 1e-9) * len(grid))
                
                # Clamp to grid bounds
                x = max(0, min(x, len(grid[0]) - 1))
                y = max(0, min(y, len(grid) - 1))
                
                # Mark station with "S"
                grid[y][x] = "S"

    def _draw_tracks(self, grid: List[List[str]], locations: List[Tuple[str, str, Tuple[float, float]]], 
                     min_x: float, min_y: float):
        """Draw all tracks on the grid."""
        from track import Track
        
        for track in self.network.tracks.values():
            # Get coordinates for both ends of the track
            start_coords = self._find_coords(locations, track.start)
            end_coords = self._find_coords(locations, track.end)
            
            if start_coords and end_coords:
                # Draw the track line
                self._draw_line(grid, min_x, min_y, start_coords, end_coords)
    def _draw_line(self, grid: List[List[str]], min_x: float, min_y: float, 
                   start: Tuple[float, float], end: Tuple[float, float]):
        """Draw a line between two points on the grid."""
        # Calculate coordinate ranges from all locations
        locations = self._get_all_locations_with_coords()
        max_x = max(loc[2][0] for loc in locations)
        max_y = max(loc[2][1] for loc in locations)
        
        # Convert to grid coordinates with normalization
        x0 = int((start[0] - min_x) / (max_x - min_x + 1e-9) * len(grid[0]))
        y0 = int((start[1] - min_y) / (max_y - min_y + 1e-9) * len(grid))
        x1 = int((end[0] - min_x) / (max_x - min_x + 1e-9) * len(grid[0]))
        y1 = int((end[1] - min_y) / (max_y - min_y + 1e-9) * len(grid))
        
        # Clamp to grid bounds
        x0 = max(0, min(x0, len(grid[0]) - 1))
        y0 = max(0, min(y0, len(grid) - 1))
        x1 = max(0, min(x1, len(grid[0]) - 1))
        y1 = max(0, min(y1, len(grid) - 1))
        
        # Draw line using simple Bresenham's algorithm
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        
        while True:
            # Clamp to grid bounds
            x0 = max(0, min(x0, len(grid[0]) - 1))
            y0 = max(0, min(y0, len(grid) - 1))
            
            # Mark track with "-" or "|"
            if grid[y0][x0] in ("J", "S", "C", "!", "X"):
                pass  # Don't overwrite junctions/stations/signals
            else:
                grid[y0][x0] = "-"
            
            if x0 == x1 and y0 == y1:
                break
            
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy
    def _add_signals(self, grid: List[List[str]], signal_logic: SignalLogic, 
                     locations: List[Tuple[str, str, Tuple[float, float]]],
                     min_x: float, min_y: float):
        """Add signal indicators to the grid."""
        from signal import SignalAspect
        
        # For each track, add a signal at its start location
        for track_name, track_state in signal_logic.track_states.items():
            track = signal_logic.network.tracks.get(track_name)
            if not track:
                continue
            
            signal_name = f"sig_{track_name}"
            signal = signal_logic.signals.get(signal_name)
            if not signal:
                continue
            
            # Get signal aspect
            aspect = signal.aspect
            
            # Find coords for signal location (track start)
            signal_coords = signal_logic.network.junctions.get(signal.location)
            if not signal_coords or not signal_coords.coordinates:
                continue
            
            signal_x, signal_y = signal_coords.coordinates
            
            # Calculate max coordinates from all locations
            locations = self._get_all_locations_with_coords()
            max_x = max(loc[2][0] for loc in locations)
            max_y = max(loc[2][1] for loc in locations)
            
            # Convert to grid position with normalization
            x = int((signal_x - min_x) / (max_x - min_x + 1e-9) * len(grid[0]))
            y = int((signal_y - min_y) / (max_y - min_y + 1e-9) * len(grid))
            
            x = max(0, min(x, len(grid[0]) - 1))
            y = max(0, min(y, len(grid) - 1))
            
            # Mark signal with appropriate symbol
            # Signals can be at junctions/stations, so overwrite if needed
            if aspect == SignalAspect.CLEAR:
                grid[y][x] = "C"
            elif aspect == SignalAspect.CAUTION:
                grid[y][x] = "!"
            else:  # STOP
                grid[y][x] = "X"
    def _add_trains(self, grid: List[List[str]], trains: List[Train], 
                    locations: List[Tuple[str, str, Tuple[float, float]]],
                    min_x: float, min_y: float, max_x: float, max_y: float):
        """Add train indicators to the grid."""
        for train in trains:
            if train.on_track:
                # Train is on a track - show it on the track
                track = self.network.tracks.get(train.on_track)
                if track:
                    # Get coordinates for both ends of the track
                    start_coords = self._find_coords(locations, track.start)
                    end_coords = self._find_coords(locations, track.end)

                    if start_coords and end_coords:
                        # Determine where to place the train on the track
                        # For simplicity, place it at the current location's position
                        train_loc = train.location
                        if train_loc in (track.start, track.end):
                            # Train is at one end of the track
                            if train_loc == track.start:
                                coords = start_coords
                            else:
                                coords = end_coords
                        else:
                            # Train is somewhere in the middle - estimate position
                            # Use location as best estimate
                            if train_loc in locations:
                                coords = self._find_coords(locations, train_loc)
                            else:
                                # Fallback to midpoint
                                mid_x = (start_coords[0] + end_coords[0]) / 2
                                mid_y = (start_coords[1] + end_coords[1]) / 2
                                coords = (mid_x, mid_y)

                        if coords:
                            # Normalize coordinates to grid position
                            x = int((coords[0] - min_x) / (max_x - min_x + 1e-9) * len(grid[0]))
                            y = int((coords[1] - min_y) / (max_y - min_y + 1e-9) * len(grid))

                            x = max(0, min(x, len(grid[0]) - 1))
                            y = max(0, min(y, len(grid) - 1))

                            # Mark train with "T" (can overwrite junctions/stations if train is there)
                            grid[y][x] = "T"
            elif train.location:
                # Train is at a location (not on a track)
                train_coords = self._find_coords(locations, train.location)
                if train_coords:
                    # Normalize coordinates to grid position
                    x = int((train_coords[0] - min_x) / (max_x - min_x + 1e-9) * len(grid[0]))
                    y = int((train_coords[1] - min_y) / (max_y - min_y + 1e-9) * len(grid))

                    x = max(0, min(x, len(grid[0]) - 1))
                    y = max(0, min(y, len(grid) - 1))

                    # If location is a junction/station/signal, place train nearby
                    if grid[y][x] in ("J", "S", "C", "!", "X"):
                        # Place train to the right of the junction/station/signal
                        if x + 1 < len(grid[0]):
                            grid[y][x + 1] = "T"
                    else:
                        # Location is empty space, place train there
                        grid[y][x] = "T"

def create_simple_visualization() -> str:
    """Create a simple visualization for demonstration."""
    from track import RailwayNetwork, JunctionType, TrackType
    from signal import SignalLogic
    
    network = RailwayNetwork()
    network.add_junction("A", coordinates=(0.0, 0.0))
    network.add_junction("B", coordinates=(1.0, 0.0))
    network.add_junction("C", coordinates=(2.0, 0.0))
    network.add_track("t1", "A", "B")
    network.add_track("t2", "B", "C")
    
    sl = SignalLogic(network)
    
    # Create a simple visual representation
    return """
    Railway Network Visualization
    ==============================
    
    This is a placeholder visualization.
    A full implementation would show:
    - Stations as [S]
    - Junctions as (+) or (X)
    - Tracks as lines connecting them
    - Signals at track ends
    - Trains as (T) on tracks
    """


if __name__ == "__main__":
    # Test the visualization
    print(create_simple_visualization())
