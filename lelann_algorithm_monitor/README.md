# LeLann Algorithm Implementation with monitor - Homework 2

This exercise extends the previous **LeLann Token Ring Algorithm** by introducing a **monitor node** that acts as a **display screen**. The monitor receives and prints messages sent by the ring nodes using **REQ/REP** sockets.

## Description  
- The system consists of 4 ring nodes and 1 monitor node. 
- All ring nodes communicate with each other using PAIR sockets (token passing).
- Each ring node also connects to the monitor using REQ/REP sockets to send user messages.

## Ring Node Behavior

Each ring node:
1. Waits to receive the token from the previous node
2. When it receives the token:
   - Asks the user for input.
   - If the input is **empty**, it forwards the token to the next node.
   - If the input is **non-empty**, it sends the message to the **monitor node** with REQ socket, waits for an acknowledgment, and then forwards the token to the next node.

## Monitor Node Behavior

The monitor node:
1. Uses a **REP socket**.
2. Waits for messages from any of the ring nodes.
3. When it receives a message, it **prints it on the screen** and sends back an ACK to the sender.

## How to run:
1. Start the monitor node:
    ```bash
   cd lelann_algorithm_monitor
   python3 -m venv venv
   source venv/bin/activate
   pip3 install pyzmq
   python3 monitor.py 
   ```
2. Open 4 separate terminals (for each node)
3. In each terminal: 
   ```bash
   cd lelann_algorithm_monitor
   python3 -m venv venv
   source venv/bin/activate
   pip3 install pyzmq 
   ```
4. Start a node in each terminal:
   ```bash
   python node.py 0 5556 5557
   python node.py 1 5557 5558
   python node.py 2 5558 5559
   python node.py 3 5559 5556
   ```


