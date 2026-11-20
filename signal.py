"""
Railway signal logic - aspects and control.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum
from track import Track, RailwayNetwork


class SignalAspect(Enum):
    """Signal aspects."""
    CLEAR = "clear"      # Green - proceed
    CAUTION = "caution"  # Yellow - prepare to stop
    STOP = "stop"        # Red - stop


@dataclass
class Signal:
    """A railway signal at the entrance of a track section."""
    name: str
    track_name: str  # The track section this signal protects
    location: str    # The junction/station where the signal is located
    aspect: SignalAspect = SignalAspect.STOP
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, Signal):
            return False
        return self.name == other.name


class TrackState:
    """The state of a track section."""
    
    def __init__(self, track: Track, network: RailwayNetwork):
        self.track = track
        self.network = network
        self.occupied: bool = False
        self.occupant: Optional[str] = None
    
    @property
    def is_free(self) -> bool:
        return not self.occupied
    
    @property
    def is_occupied(self) -> bool:
        return self.occupied
    
    def set_occupied(self, occupant: str):
        self.occupied = True
        self.occupant = occupant
    
    def set_free(self):
        self.occupied = False
        self.occupant = None


class SignalLogic:
    """Logic for determining signal aspects."""
    
    def __init__(self, network: RailwayNetwork):
        self.network = network
        self.signals: Dict[str, Signal] = {}
        self.track_states: Dict[str, TrackState] = {}
        self._create_signals()
        self.update_signals()  # Initialize aspects based on initial track states
    
    def _create_signals(self):
        """Create signals at the entrance of each track."""
        for track in self.network.tracks.values():
            signal_name = f"sig_{track.name}"
            signal = Signal(
                name=signal_name,
                track_name=track.name,
                location=track.start
            )
            self.signals[signal_name] = signal
    
    def get_track_state(self, track_name: str) -> Optional[TrackState]:
        """Get or create the track state for a track."""
        if track_name not in self.track_states:
            track = self.network.tracks.get(track_name)
            if track is None:
                return None
            self.track_states[track_name] = TrackState(track, self.network)
        return self.track_states[track_name]
    
    def get_signal(self, signal_name: str) -> Optional[Signal]:
        """Get a signal by name."""
        return self.signals.get(signal_name)
    
    def get_signal_at(self, location: str) -> List[Signal]:
        """Get signals at a location."""
        adjacent_tracks = self.network.get_adjacent_tracks(location)
        signals = []
        for track in adjacent_tracks:
            signal_name = f"sig_{track.name}"
            if signal_name in self.signals:
                if self.signals[signal_name].location == location:
                    signals.append(self.signals[signal_name])
        return signals
    
    def update_signals(self):
        """Update all signal aspects based on current track states."""
        for signal_name, signal in self.signals.items():
            self._update_signal(signal)
    
    def _update_signal(self, signal: Signal):
        """Update a single signal's aspect."""
        track_state = self.get_track_state(signal.track_name)
        if track_state is None:
            signal.aspect = SignalAspect.STOP
            return
        if track_state.occupied:
            signal.aspect = SignalAspect.STOP
        else:
            signal.aspect = SignalAspect.CLEAR
    
    def get_signal_aspect(self, signal_name: str) -> SignalAspect:
        """Get the current aspect of a signal."""
        signal = self.get_signal(signal_name)
        if signal is None:
            return SignalAspect.STOP
        return signal.aspect
    
    def can_enter_track(self, track_name: str) -> bool:
        """Check if a train can enter a track section."""
        track_state = self.get_track_state(track_name)
        if track_state is None:
            return False
        return track_state.is_free
    
    def occupy_track(self, track_name: str, occupant: str):
        """Mark a track as occupied by an occupant."""
        track_state = self.get_track_state(track_name)
        if track_state is None:
            raise ValueError(f"No track state for {track_name}")
        track_state.set_occupied(occupant)
        self.update_signals()  # Update aspects after state change
    
    def free_track(self, track_name: str):
        """Mark a track as free."""
        track_state = self.get_track_state(track_name)
        if track_state is None:
            raise ValueError(f"No track state for {track_name}")
        track_state.set_free()
        self.update_signals()  # Update aspects after state change
    
    def __repr__(self):
        return f"SignalLogic({len(self.signals)} signals, {len(self.track_states)} tracks)"


def create_signal_logic(network: RailwayNetwork) -> SignalLogic:
    """Create signal logic for a network."""
    return SignalLogic(network)


if __name__ == "__main__":
    from track import create_simple_network
    
    network = create_simple_network()
    print("Network:", network)
    
    signal_logic = create_signal_logic(network)
    print("SignalLogic:", signal_logic)
    
    # Check initial aspects - all should be CLEAR
    for sig_name, signal in signal_logic.signals.items():
        print(f"  {sig_name}: {signal.aspect}")
    
    # Occupy a track
    signal_logic.occupy_track("n-central", "train1")
    print("\nAfter occupying n-central:")
    
    for sig_name, signal in signal_logic.signals.items():
        if signal.track_name == "n-central":
            print(f"  {sig_name}: {signal.aspect} (should be STOP)")
        else:
            print(f"  {sig_name}: {signal.aspect}")
    
    print("\ncan_enter_track('n-central'):", signal_logic.can_enter_track("n-central"))
    
    # Free the track
    signal_logic.free_track("n-central")
    print("\nAfter freeing n-central:")
    print("can_enter_track('n-central'):", signal_logic.can_enter_track("n-central"))
