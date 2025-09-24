import time
import zmq
import sys


def main():
    context = zmq.Context()

    node_id = sys.argv[1]
    receive_port = sys.argv[2]
    send_port = sys.argv[3]

    sender = context.socket(zmq.PAIR)
    sender.bind("tcp://*:%s" % send_port)

    receiver = context.socket(zmq.PAIR)
    receiver.connect("tcp://localhost:%s" % receive_port)

    if node_id == "0":
        print(f"Node {node_id} creating token")
        sender.send_string("1")

    try:
        while True:
            print(f"Node {node_id} in while")
            # Wait for message from previous node
            message = receiver.recv_string()
            print(f"Node {node_id} received token: {message}")
            time.sleep(1)
            # Send message to next node
            sender.send_string(str(int(message) + 1))
    except KeyboardInterrupt:
        print(f"Node {node_id}: shutting down...")


if __name__ == "__main__":
    main()