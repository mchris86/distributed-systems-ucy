#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip3 install pyzmq

export N="5"

# Servers
BASE_PORT=5555
for ((i=0; i<N; i++)); do
    PORT=$((BASE_PORT + i))
    echo "Starting node on port $PORT"
    gnome-terminal -- bash -c "python3 node.py $N $PORT; exec bash"
done
