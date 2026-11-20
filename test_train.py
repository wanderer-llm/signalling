"""Tests for train movement."""

import pytest
from train import Train, create_train
from signal import SignalLogic, SignalAspect
from track import RailwayNetwork, Junction, TrackType


def setup_network():
    """Create a simple test network with proper junctions."""
    network = RailwayNetwork()
    
    # Add junctions first
    network.add_junction("j1")
    network.add_junction("j2")
    network.add_junction("j3")
    
    # Add tracks
    network.add_track("t1", "j1", "j2")
    network.add_track("t2", "j2", "j3")
    
    return network


def test_train_creation():
    """Test creating a train."""
    network = RailwayNetwork()
    network.add_junction("j1")
    network.add_junction("j2")
    network.add_track("t1", "j1", "j2")
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    assert train.name == "train1"
    assert train.location is None
    assert train.on_track is None
    assert train.target is None
    assert train.path == []
    assert train.moving is False


def test_train_find_path():
    """Test path finding."""
    network = setup_network()
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location first
    train.location = "j1"
    
    # Find path to j3 (includes start, so path is ["j1", "j2", "j3"])
    path = train.find_path("j1", "j3")
    
    assert path == ["j1", "j2", "j3"]

def test_train_set_target():
    """Test setting a target location."""
    network = setup_network()
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location first
    train.location = "j1"
    
    # Set target
    train.set_target("j3")
    
    assert train.target == "j3"
    assert train.path == ["j2", "j3"]
    assert train.remaining_path == ["j2", "j3"]
    assert train.moving is True


def test_train_move():
    """Test moving a train along a path."""
    network = setup_network()
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location and target
    train.location = "j1"
    train.set_target("j3")
    
    # Move first step
    result = train.move()
    assert result is True
    assert train.location == "j2"
    assert train.on_track == "t1"
    assert train.moving is True
    
    # Move second step
    result = train.move()
    assert result is True
    assert train.location == "j3"
    assert train.on_track == "t2"
    assert train.moving is False  # Reached target


def test_train_move_stops_at_target():
    """Test that train stops when reaching target."""
    network = setup_network()
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location and target (same location - no move needed)
    train.location = "j1"
    train.set_target("j1")
    
    # Should not move
    result = train.move()
    assert result is False
    assert train.moving is False
    assert train.path == []


def test_train_move_blocked_by_signal():
    """Test that train cannot move if signal is red."""
    network = setup_network()
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location and target
    train.location = "j1"
    train.set_target("j2")
    
    # Occupy the track (simulating another train ahead)
    sl.occupy_track("t1", "train2")
    
    # Try to move - should fail
    result = train.move()
    assert result is False
    assert train.on_track is None


def test_train_move_blocked_by_signal_after_free():
    """Test that train can move after track is freed."""
    network = setup_network()
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location and target
    train.location = "j1"
    train.set_target("j2")
    
    # Occupy the track
    sl.occupy_track("t1", "train2")
    
    # Try to move - should fail
    result = train.move()
    assert result is False
    
    # Free the track
    sl.free_track("t1")
    
    # Try to move again - should succeed
    result = train.move()
    assert result is True
    assert train.location == "j2"


def test_train_move_nonexistent_target():
    """Test that train cannot set a target it cannot reach."""
    network = RailwayNetwork()
    network.add_junction("j1")
    network.add_track("t1", "j1", "j2")
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location
    train.location = "j1"
    
    # Try to set a target that doesn't exist
    with pytest.raises(ValueError, match="No path from j1 to nonexistent"):
        train.set_target("nonexistent")


def test_train_can_enter_track():
    """Test that train respects can_enter_track."""
    network = setup_network()
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location and target
    train.location = "j1"
    train.set_target("j2")
    
    # Track is free, should be able to enter
    assert sl.can_enter_track("t1") is True
    
    # Move onto track
    train.move()
    assert train.on_track == "t1"
    
    # Now the track is occupied by this train
    assert sl.can_enter_track("t1") is False


def test_train_repr():
    """Test train string representation."""
    network = setup_network()
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    train.location = "j1"
    train.set_target("j2")
    
    repr_str = repr(train)
    assert "train1" in repr_str
    # When target is set and path exists, train is in "moving" state
    assert "moving" in repr_str
    assert "target j2" in repr_str


def test_train_multiple_moves():
    """Test multiple consecutive moves."""
    network = RailwayNetwork()
    network.add_junction("j1")
    network.add_junction("j2")
    network.add_junction("j3")
    network.add_junction("j4")
    network.add_track("t1", "j1", "j2")
    network.add_track("t2", "j2", "j3")
    network.add_track("t3", "j3", "j4")
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Set location and target (3 steps away)
    train.location = "j1"
    train.set_target("j4")
    
    assert len(train.path) == 3  # j2, j3, j4
    
    # Move 3 times
    for i in range(3):
        result = train.move()
        assert result is True
    
    # Should be at target now
    assert train.location == "j4"
    assert train.moving is False
    assert len(train.path) == 0


def test_train_move_without_location():
    """Test that train cannot move without a location."""
    network = RailwayNetwork()
    network.add_junction("j1")
    network.add_junction("j2")
    network.add_track("t1", "j1", "j2")
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    
    # Try to set target without location
    with pytest.raises(ValueError, match="Train must be at a location"):
        train.set_target("j2")
