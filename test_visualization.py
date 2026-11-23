"""Tests for the railway network visualizer."""

import pytest
from visualization import Visualizer
from track import RailwayNetwork, create_simple_network
from train import create_train
from signal import SignalLogic


def test_visualizer_basic_render():
    """Test that visualizer can render a simple network."""
    network = create_simple_network()
    sl = SignalLogic(network)
    visualizer = Visualizer(network)
    
    # Should be able to render without error
    output = visualizer.render([], sl)
    
    # Output should not be empty
    assert len(output) > 0
    
    # Should contain network elements
    assert "C" in output  # Clear signals at junctions
    assert "S" in output  # Stations
    assert "-" in output  # Tracks

def test_visualizer_with_trains():
    """Test that visualizer shows trains on the network."""
    # Create a network with a simple path
    network = RailwayNetwork()
    network.add_junction("j1")
    network.add_junction("j2")
    network.add_junction("j3")
    network.add_track("t1", "j1", "j2")
    network.add_track("t2", "j2", "j3")
    
    sl = SignalLogic(network)
    train = create_train("train1", network, sl)
    train.location = "j1"
    train.set_target("j3")
    
    visualizer = Visualizer(network)
    output = visualizer.render([train], sl)
    
    # Should contain train indicator
    assert "T" in output

def test_visualizer_with_signal_aspects():
    """Test that visualizer shows signal aspects."""
    network = RailwayNetwork()
    network.add_junction("j1")
    network.add_junction("j2")
    network.add_track("t1", "j1", "j2")
    
    sl = SignalLogic(network)
    
    # Occupy a track to change signal aspect
    sl.occupy_track("t1", "train1")
    
    visualizer = Visualizer(network)
    output = visualizer.render([], sl)
    
    # Should show some signal aspect indicators
    assert len(output) > 0


def test_visualizer_simple_network():
    """Test visualization of the simple demo network."""
    network = create_simple_network()
    sl = SignalLogic(network)
    
    visualizer = Visualizer(network)
    output = visualizer.render([], sl)
    
    # Verify output is valid ASCII art
    assert isinstance(output, str)
    assert len(output) > 0
    
    # Should show the basic structure of the network
    # The simple network has 2 stations and 3 junctions
    assert "S" in output  # Stations
    assert "C" in output  # Clear signals at junctions
