"""Tests for the track layout module."""

import pytest
from track import (
    RailwayNetwork, Track, Junction, Station,
    TrackType, JunctionType, create_simple_network
)


def test_create_network():
    """Test that a network can be created."""
    network = RailwayNetwork()
    assert len(network.tracks) == 0
    assert len(network.junctions) == 0
    assert len(network.stations) == 0


def test_add_junction():
    """Test adding a junction."""
    network = RailwayNetwork()
    j = network.add_junction("main")
    assert j.name == "main"
    assert len(network.junctions) == 1
    assert "main" in network._junction_ids


def test_add_station():
    """Test adding a station."""
    network = RailwayNetwork()
    s = network.add_station("central", platform_count=2, platform_length=300.0)
    assert s.name == "central"
    assert s.platform_count == 2
    assert s.platform_length_meters == 300.0
    assert len(network.stations) == 1


def test_add_track():
    """Test adding a track."""
    network = RailwayNetwork()
    t = network.add_track("track1", "start", "end", TrackType.SIDING, bidirectional=False)
    assert t.name == "track1"
    assert t.start == "start"
    assert t.end == "end"
    assert t.track_type == TrackType.SIDING
    assert t.is_bidirectional == False
    assert len(network.tracks) == 1


def test_duplicate_junction():
    """Test that adding a duplicate junction returns the existing one."""
    network = RailwayNetwork()
    j1 = network.add_junction("main")
    j2 = network.add_junction("main")
    assert j1 is j2


def test_duplicate_station():
    """Test that adding a duplicate station returns the existing one."""
    network = RailwayNetwork()
    s1 = network.add_station("central")
    s2 = network.add_station("central")
    assert s1 is s2


def test_duplicate_track():
    """Test that adding a duplicate track returns the existing one."""
    network = RailwayNetwork()
    t1 = network.add_track("t1", "a", "b")
    t2 = network.add_track("t1", "a", "b")
    assert t1 is t2


def test_get_adjacent_tracks():
    """Test getting tracks adjacent to a location."""
    network = RailwayNetwork()
    network.add_junction("A")
    network.add_junction("B")
    network.add_track("t1", "A", "B")
    
    tracks_at_a = network.get_adjacent_tracks("A")
    assert len(tracks_at_a) == 1
    assert tracks_at_a[0].name == "t1"


def test_find_path():
    """Test path finding."""
    network = RailwayNetwork()
    network.add_junction("A")
    network.add_junction("B")
    network.add_junction("C")
    network.add_track("t1", "A", "B")
    network.add_track("t2", "B", "C")
    
    path = network.find_path("A", "C")
    assert path == ["A", "B", "C"]


def test_find_path_no_route():
    """Test path finding when no route exists."""
    network = RailwayNetwork()
    network.add_junction("A")
    network.add_junction("B")
    network.add_track("t1", "A", "B")
    
    path = network.find_path("A", "C")
    assert path is None


def test_create_simple_network():
    """Test the simple network creation."""
    network = create_simple_network()
    assert len(network.stations) == 5
    assert len(network.junctions) == 4
    assert len(network.tracks) == 8
    
    # Test path from north to east
    path = network.find_path("north", "east")
    assert path is not None
    assert path[0] == "north"
    assert path[-1] == "east"


def test_track_equality():
    """Test track equality."""
    network = RailwayNetwork()
    t1 = network.add_track("t1", "A", "B")
    t2 = network.add_track("t1", "A", "B")
    assert t1 == t2


def test_station_equality():
    """Test station equality."""
    network = RailwayNetwork()
    s1 = network.add_station("S")
    s2 = network.add_station("S")
    assert s1 == s2


def test_junction_equality():
    """Test junction equality."""
    network = RailwayNetwork()
    j1 = network.add_junction("J")
    j2 = network.add_junction("J")
    assert j1 == j2


def test_station_arrive():
    """Test train arriving at a station."""
    network = RailwayNetwork()
    station = network.add_station("central", platform_count=2)

    # Station can accept a train
    assert station.can_arrive() is True

    # Train arrives on platform 1
    result = station.arrive("train1", platform=1)
    assert result is True
    assert station.platforms[1] == "train1"
    assert 1 in station.occupied_platforms

    # Station still has capacity
    assert station.can_arrive() is True

    # Another train arrives on platform 2
    result = station.arrive("train2", platform=2)
    assert result is True
    assert station.platforms[2] == "train2"
    assert len(station.occupied_platforms) == 2


def test_station_arrive_full():
    """Test train arriving at a full station."""
    network = RailwayNetwork()
    station = network.add_station("central", platform_count=1)

    # First train arrives
    station.arrive("train1", platform=1)

    # Station is now full
    assert station.can_arrive() is False

    # Second train cannot arrive
    result = station.arrive("train2", platform=1)
    assert result is False
    assert station.platforms[1] == "train1"


def test_station_depart():
    """Test train departing from a station."""
    network = RailwayNetwork()
    station = network.add_station("central", platform_count=2)

    # Train arrives
    station.arrive("train1", platform=1)
    station.arrive("train2", platform=2)

    # Train1 departs
    result = station.depart("train1")
    assert result is True
    assert station.platforms[1] is None
    assert 1 not in station.occupied_platforms

    # Station has capacity again
    assert station.can_arrive() is True


def test_station_depart_not_found():
    """Test departing a train that's not at the station."""
    network = RailwayNetwork()
    station = network.add_station("central", platform_count=1)

    # Train arrives
    station.arrive("train1", platform=1)

    # Try to depart a different train
    result = station.depart("train2")
    assert result is False
    assert station.platforms[1] == "train1"


def test_station_get_train_on_platform():
    """Test getting train name from platform."""
    network = RailwayNetwork()
    station = network.add_station("central", platform_count=2)

    assert station.get_train_on_platform(1) is None

    station.arrive("train1", platform=1)
    assert station.get_train_on_platform(1) == "train1"
    assert station.get_train_on_platform(2) is None


def test_station_repr():
    """Test station string representation."""
    network = RailwayNetwork()
    station = network.add_station("central", platform_count=2)

    repr_str = repr(station)
    assert "central" in repr_str
    assert "platforms=2" in repr_str


def test_station_auto_assign_platform():
    """Test automatic platform assignment."""
    network = RailwayNetwork()
    station = network.add_station("central", platform_count=3)

    # First train should get platform 1
    station.arrive("train1")
    assert station.platforms[1] == "train1"
    assert 1 in station.occupied_platforms

    # Second train should get platform 2
    station.arrive("train2")
    assert station.platforms[2] == "train2"
    assert 2 in station.occupied_platforms


def test_station_platform_out_of_range():
    """Test arriving at a non-existent platform."""
    network = RailwayNetwork()
    station = network.add_station("central", platform_count=1)

    # Arriving at platform 2 (doesn't exist) should fail
    result = station.arrive("train1", platform=2)
    assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
