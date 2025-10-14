# LeLann Algorithm Implementation

As part of the lab exercise, we will implement the **LeLann algorithm** covered in class.  

## Requirements  
- The ring will contain **4 nodes**.  
- All nodes must run the **same code** (shared implementation).  
- Each node will be started with command-line parameters:  
  ```bash
  python node.py node_id receive_port send_port
  ```

## Token Passing  

Use **PAIR sockets** to implement the transfer of the token from one node to the next.  

- The node with **ID = 0** is responsible for creating the initial token.  
- The token will be represented as an **integer number**.  
- Each node, upon receiving the token, must:  
  1. Print its own ID.  
  2. Increment the token’s value.  
  3. Send the updated token to the next node in the ring.

## How to run:

1. Open 4 terminal windows (for each node)
2. In each terminal: 
   ```bash
   cd lelann_algorithm
   python3 -m venv venv
   source venv/bin/activate
   pip3 install pyzmq 
   ```
3. Start a node in each terminal:
   ```bash
   python3 node.py 0 5555 5556
   python3 node.py 1 5556 5557
   python3 node.py 2 5557 5558
   python3 node.py 3 5558 5555
   ```


