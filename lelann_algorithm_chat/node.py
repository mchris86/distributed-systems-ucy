import zmq
import sys


def main():
    context = zmq.Context()

    node_id = sys.argv[1]
    receive_port = sys.argv[2]
    send_port = sys.argv[3]

    sender = context.socket(zmq.PAIR)
    sender.bind(f"tcp://localhost:{send_port}")

    receiver = context.socket(zmq.PAIR)
    receiver.connect(f"tcp://localhost:{receive_port}")

    # Socket to talk to monitor
    req_socket = context.socket(zmq.REQ)
    req_socket.connect("tcp://localhost:5555")

    sub_socket = context.socket(zmq.SUB)
    sub_socket.connect("tcp://localhost:5556")
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    poller = zmq.Poller()
    poller.register(receiver, zmq.POLLIN)
    poller.register(sub_socket, zmq.POLLIN)


    if node_id == "0":
        print(f"Node {node_id} creating token")
        sender.send_string("1")

    try:
        while True:
            socks = dict(poller.poll())

            if sub_socket in socks:  # Receive message from monitor
                message = sub_socket.recv()
                print(message)

            if receiver in socks:  # Receive token
                message = receiver.recv()
                # print(f"Node {node_id} received token: {message}")

                node_input = input("Enter your message:")
                if node_input:
                    req_socket.send_string(f"{node_id}: {node_input}")
                    req_socket.recv_string()  # wait for reply from monitor

                # Send token to next node
                sender.send_string(str(int(message) + 1))

    except KeyboardInterrupt:
        print(f"Node {node_id}: shutting down...")


if __name__ == "__main__":
    main()