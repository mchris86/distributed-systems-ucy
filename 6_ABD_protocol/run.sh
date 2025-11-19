#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip3 install pyzmq

gnome-terminal -- bash -c "python3 writer.py; exec bash"
gnome-terminal -- bash -c "python3 server.py 5556; exec bash"
gnome-terminal -- bash -c "python3 server.py 5557; exec bash"
gnome-terminal -- bash -c "python3 server.py 5558; exec bash"
gnome-terminal -- bash -c "python3 reader.py; exec bash"