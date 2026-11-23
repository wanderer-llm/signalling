#!/usr/bin/env python3
"""Demo script for the railway signaling system."""

from track import create_simple_network
from signal import SignalLogic
from train import create_train
from visualization import Visualizer


def main():
    network = create_simple_network()
    sl = SignalLogic(network)
    visualizer = Visualizer(network)

    # Create and move a train from north to central
    train = create_train('express_1', network, sl)
    train.location = 'north'
    train.set_target('central')

    print('=' * 50)
    print('RAILWAY SIGNALING SYSTEM - DEMO')
    print('=' * 50)
    print()
    print('Network state:')
    print(visualizer.render([train], sl))
    print()
    print(f'Train {train.name} is at location {train.location}')
    print(f'Path: {train.path}')


if __name__ == '__main__':
    main()
