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
    pub_port = sys.argv[6]

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
        pub_socket = context.socket(zmq.PUB)
        pub_socket.bind(f"tcp://*:{pub_port}")
        ports = 9000
        time.sleep(1)
        sub_socket = -1
    else:
        sub_socket = context.socket(zmq.SUB)
        sub_socket.connect(f"tcp://localhost:{pub_port}")
        sub_socket.setsockopt_string(zmq.SUBSCRIBE, f"Remove {node_id}")
        poller.register(sub_socket, zmq.POLLIN)
        
    try:
        while True:
            socks = dict(poller.poll())

            if receiver_forward in socks:
                message = receiver_forward.recv_string()
                words = message.split()
                print(message)

                if words[0] == "Token":
                    if node_id == "0":
                        node = int(input("Want to remove a node? "))
                        if node > 0:
                            print(f"Removing node {node}")
                            # Send Remove <new_listen> <new_connect>
                            pub_socket.send_string(f"Remove {node} {ports} {ports + 1} ")
                            ports += 2
                            time.sleep(5)

                    # Send message to next node
                    sender_forward.send_string(f"Token {node_id} {int(words[2]) + 1}")
                    print(f"Sent: Token {node_id} {int(words[2]) + 1}")

                elif words[0] == "Leaving":
                    new_listen = words[1]
                    new_connect = words[2]

                    poller.unregister(receiver_forward)
                    receiver_forward.close()
                    sender_reverse.close()

                    receiver_forward = context.socket(zmq.PAIR)
                    receiver_forward.bind(f"tcp://*:{new_listen}")  # BIND on new_listen
                    poller.register(receiver_forward, zmq.POLLIN)

                    sender_reverse = context.socket(zmq.PAIR)
                    sender_reverse.connect(f"tcp://localhost:{new_connect}")  # CONNECT on new_connect

            if receiver_reverse in socks:
                message = receiver_reverse.recv_string()
                print(message)
                words = message.split()

                new_listen = words[1]
                new_connect = words[2]

                poller.unregister(receiver_reverse)
                receiver_reverse.close()
                sender_forward.close()

                receiver_reverse = context.socket(zmq.PAIR)
                receiver_reverse.bind(f"tcp://*:{new_listen}")  # BIND on new_listen
                poller.register(receiver_reverse, zmq.POLLIN)

                sender_forward = context.socket(zmq.PAIR)
                sender_forward.connect(f"tcp://localhost:{new_connect}")  # CONNECT on new_connect


            if sub_socket in socks:  # Receive message from monitor
                print("Getting removed...")
                message = sub_socket.recv_string()
                words = message.split()

                new_listen = words[2]
                new_connect = words[3]

                sender_forward.send_string(f"Leaving {new_listen} {new_connect}")
                sender_reverse.send_string(f"Leaving {new_connect} {new_listen}")

                poller.unregister(receiver_forward)
                receiver_forward.close()
                poller.unregister(receiver_reverse)
                receiver_reverse.close()
                sender_forward.close()
                sender_reverse.close()

    except KeyboardInterrupt:
            print(f"Node {node_id}: shutting down...")

if __name__ == "__main__":
    main()
