#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip3 install pyzmq

gnome-terminal -- bash -c "python3 client.py; exec bash"
gnome-terminal -- bash -c "python3 coordinator.py; exec bash"
gnome-terminal -- bash -c "python3 participant.py 5556; exec bash"
gnome-terminal -- bash -c "python3 participant.py 5557; exec bash"
gnome-terminal -- bash -c "python3 participant.py 5558; exec bash"