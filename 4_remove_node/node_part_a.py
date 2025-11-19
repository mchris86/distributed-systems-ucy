import time
import zmq
import sys


def main():
    context = zmq.Context()

    node_id = sys.argv[1]
    receive_port_forward = sys.argv[2]
    send_port_forward = sys.argv[3]
    receive_port_reverse = sys.argv[4]
    send_port_reverse = sys.argv[5]

    # Forward
    receiver_forward = context.socket(zmq.PAIR)
    receiver_forward.bind(f"tcp://*:{receive_port_forward}")
    sender_forward = context.socket(zmq.PAIR)
    sender_forward.connect(f"tcp://localhost:{send_port_forward}")

    # Reverse
    receiver_reverse = context.socket(zmq.PAIR)
    receiver_reverse.bind(f"tcp://*:{receive_port_reverse}")
    sender_reverse = context.socket(zmq.PAIR)
    sender_reverse.connect(f"tcp://localhost:{send_port_reverse}")

    # Poller
    poller = zmq.Poller()
    poller.register(receiver_reverse, zmq.POLLIN)
    poller.register(receiver_forward, zmq.POLLIN)

    if node_id == "0":
        print(f"Node {node_id} creating token")
        sender_forward.send_string(f"Token 0 0")
        sender_reverse.send_string(f"Reverse 0 0")

    try:
        while True:
            socks = dict(poller.poll())

            if receiver_forward in socks:
                message = receiver_forward.recv_string()
                print(message)
                time.sleep(1)
                words = message.split()
                # Send message to next node
                sender_forward.send_string(f"Token {node_id} {int(words[2]) + 1}")

            if receiver_reverse in socks:
                message = receiver_reverse.recv_string()
                print(message)
                time.sleep(1)
                words = message.split()
                # Send message to next node
                sender_reverse.send_string(f"Reverse {node_id} {int(words[2]) + 1}")

    except KeyboardInterrupt:
        print(f"Node {node_id}: shutting down...")


if __name__ == "__main__":
    main()
