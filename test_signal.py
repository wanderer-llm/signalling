"""Tests for signal logic."""

import pytest
from signal import (
    SignalAspect, Signal, TrackState, SignalLogic,
    create_signal_logic
)
from track import RailwayNetwork, Junction


def test_signal_aspects():
    """Test that SignalAspect enum has all expected values."""
    assert SignalAspect.CLEAR.value == "clear"
    assert SignalAspect.CAUTION.value == "caution"
    assert SignalAspect.STOP.value == "stop"


def test_signal_equality():
    """Test signal equality and hashing."""
    sig1 = Signal(name="sig1", track_name="t1", location="loc1")
    sig2 = Signal(name="sig1", track_name="t1", location="loc1")
    sig3 = Signal(name="sig2", track_name="t2", location="loc2")
    
    assert sig1 == sig2
    assert sig1 != sig3
    assert hash(sig1) == hash(sig2)


def test_track_state():
    """Test track state operations."""
    network = RailwayNetwork()
    network.add_track("t1", "j1", "j2")
    
    ts = TrackState(network.tracks["t1"], network)
    
    # Initial state should be free
    assert ts.is_free is True
    assert ts.is_occupied is False
    assert ts.occupant is None
    
    # Set occupied
    ts.set_occupied("train1")
    assert ts.is_free is False
    assert ts.is_occupied is True
    assert ts.occupant == "train1"
    
    # Set free
    ts.set_free()
    assert ts.is_free is True
    assert ts.is_occupied is False
    assert ts.occupant is None


def test_signal_logic_creation():
    """Test that SignalLogic creates signals for all tracks."""
    network = RailwayNetwork()
    network.add_track("t1", "j1", "j2")
    network.add_track("t2", "j1", "j3")
    
    sl = SignalLogic(network)
    
    assert len(sl.signals) == 2
    assert "sig_t1" in sl.signals
    assert "sig_t2" in sl.signals
    
    # Check signal properties
    sig_t1 = sl.get_signal("sig_t1")
    assert sig_t1 is not None
    assert sig_t1.track_name == "t1"
    assert sig_t1.location == "j1"


def test_initial_signal_aspects():
    """Test that signals start with CLEAR aspect when tracks are free."""
    network = RailwayNetwork()
    network.add_track("t1", "j1", "j2")
    
    sl = SignalLogic(network)
    
    # Initial aspect should be CLEAR
    assert sl.get_signal_aspect("sig_t1") == SignalAspect.CLEAR


def test_signal_update_on_occupy():
    """Test that signal aspect updates to STOP when track is occupied."""
    network = RailwayNetwork()
    network.add_track("t1", "j1", "j2")
    
    sl = SignalLogic(network)
    
    # Initially CLEAR
    assert sl.get_signal_aspect("sig_t1") == SignalAspect.CLEAR
    
    # Occupy the track
    sl.occupy_track("t1", "train1")
    
    # Should now be STOP
    assert sl.get_signal_aspect("sig_t1") == SignalAspect.STOP


def test_signal_update_on_free():
    """Test that signal aspect updates to CLEAR when track is freed."""
    network = RailwayNetwork()
    network.add_track("t1", "j1", "j2")
    
    sl = SignalLogic(network)
    
    # Occupy then free
    sl.occupy_track("t1", "train1")
    assert sl.get_signal_aspect("sig_t1") == SignalAspect.STOP
    
    sl.free_track("t1")
    # Should now be CLEAR
    assert sl.get_signal_aspect("sig_t1") == SignalAspect.CLEAR


def test_can_enter_track():
    """Test can_enter_track method."""
    network = RailwayNetwork()
    network.add_track("t1", "j1", "j2")
    
    sl = SignalLogic(network)
    
    # Should be able to enter free track
    assert sl.can_enter_track("t1") is True
    
    # Cannot enter occupied track
    sl.occupy_track("t1", "train1")
    assert sl.can_enter_track("t1") is False
    
    # Can enter again after freeing
    sl.free_track("t1")
    assert sl.can_enter_track("t1") is True


def test_can_enter_nonexistent_track():
    """Test can_enter_track with a non-existent track."""
    network = RailwayNetwork()
    sl = SignalLogic(network)
    
    # Should return False for non-existent track
    assert sl.can_enter_track("nonexistent") is False


def test_occupy_nonexistent_track():
    """Test that occupying a non-existent track raises an error."""
    network = RailwayNetwork()
    sl = SignalLogic(network)
    
    with pytest.raises(ValueError, match="No track state for nonexistent"):
        sl.occupy_track("nonexistent", "train1")


def test_free_nonexistent_track():
    """Test that freeing a non-existent track raises an error."""
    network = RailwayNetwork()
    sl = SignalLogic(network)
    
    with pytest.raises(ValueError, match="No track state for nonexistent"):
        sl.free_track("nonexistent")


def test_get_signal_at_location():
    """Test getting signals at a specific location."""
    network = RailwayNetwork()
    
    # Create a Y junction
    network.add_track("t1", "j1", "j2")
    network.add_track("t2", "j1", "j2")
    network.add_track("t3", "j3", "j2")
    
    sl = SignalLogic(network)
    
    # Get signals at j1 (where t1 and t2 start)
    signals = sl.get_signal_at("j1")
    
    # Should have 2 signals (one for each track starting at j1)
    assert len(signals) == 2
    
    # Check all are at j1
    for sig in signals:
        assert sig.location == "j1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
