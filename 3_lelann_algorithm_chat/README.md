# LeLann Algorithm - Chat Implementation (PUB-SUB Extension) - Homework 3

This exercise extends the previous LeLann Token Ring Algorithm by modifying the **monitor node** to act as a **message broadcaster** instead of a simple display.
The monitor now uses **PUB/SUB sockets** to forward messages from any ring node **to all nodes** in the system.

## Description  
- The system consists of 4 ring nodes and 1 monitor node. 
- All ring nodes communicate with each other using PAIR sockets (token passing).
- Each ring node connects to the monitor using:
  - A **REQ socket** to send user messages.
  - A **SUB socket** to receive messages published by the monitor.
- The monitor node:
  - Receives messages from nodes using a **REP socket**.
  - Broadcasts them to all nodes using a **PUB socket**.

## Ring Node Behavior
Each ring node:
1. Waits to receive the token from the previous node
2. When it receives the token:
   - Asks the user for input.
   - If the input is **empty**, it forwards the token to the next node.
   - If the input is **non-empty**, it sends the message to the **monitor node** with REQ socket, waits for an acknowledgment, and then forwards the token to the next node.
3. Listens for broadcasted messages from the monitor using a SUB socket.
   - When a message is received, it prints it to the console.

## Monitor Node Behavior
The monitor node:
1. Uses a **REP socket** to receive messages from ring nodes.
2. For each received message:
  - Sends back an ACK to the sender.
  - Broadcasts the message to all nodes using a PUB socket.
3. All ring nodes subscribed to the PUB socket receive and display the message.

## How to run:
1. Start the monitor node:
    ```bash
   cd 3_lelann_algorithm_chat
   python3 -m venv venv
   source venv/bin/activate
   pip3 install pyzmq
   python3 monitor.py 
   ```
2. Open 4 separate terminals (for each node)
3. In each terminal: 
   ```bash
   cd 3_lelann_algorithm_chat
   python3 -m venv venv
   source venv/bin/activate
   pip3 install pyzmq 
   ```
4. Start a node in each terminal:
   ```bash
   python3 node.py 0 5557 5558
   python3 node.py 1 5558 5559
   python3 node.py 2 5559 5560
   python3 node.py 3 5560 5557
   ```


