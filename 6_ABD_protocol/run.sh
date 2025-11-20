#!/bin/bash

python3 -m venv .venv
source .venv/bin/activate

pip3 install pyzmq

export N="3"

# Writer
gnome-terminal -- bash -c "python3 writer.py $N; exec bash"

# Servers
BASE_PORT=5556
for ((i=0; i<N; i++)); do
    PORT=$((BASE_PORT + i))
    echo "Starting server on port $PORT"
    gnome-terminal -- bash -c "python3 server.py $PORT; exec bash"
done

# Readers
gnome-terminal -- bash -c "python3 reader.py $N; exec bash"
gnome-terminal -- bash -c "python3 reader.py $N; exec bash"