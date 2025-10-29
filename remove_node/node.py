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

    sender_forward = context.socket(zmq.PAIR)
    sender_forward.bind(f"tcp://*:{send_port_forward}")
    receiver_forward = context.socket(zmq.PAIR)
    receiver_forward.connect(f"tcp://localhost:{receive_port_forward}")

    sender_reverse = context.socket(zmq.PAIR)
    sender_reverse.bind(f"tcp://*:{send_port_reverse}")
    receiver_reverse= context.socket(zmq.PAIR)
    receiver_reverse.connect(f"tcp://localhost:{receive_port_reverse}")

    poller = zmq.Poller()
    poller.register(receiver_reverse, zmq.POLLIN)
    poller.register(receiver_forward, zmq.POLLIN)
    ports = 9000

    if node_id == "0":
        print(f"Node {node_id} creating token")
        sender_forward.send_string("Token 0 0")
        publisher = context.socket(zmq.PUB)
        publisher.bind(f"tcp://*:{pub_port}")
        subscriber = -1
    else:
        subscriber = context.socket(zmq.SUB)
        subscriber.connect(f"tcp://localhost:{pub_port}")
        subscriber.setsockopt_string(zmq.SUBSCRIBE, f"Remove {node_id}")
        poller.register(subscriber, zmq.POLLIN)

    try:
        while True:
            socks = dict(poller.poll())

            if receiver_forward in socks:

                message = receiver_forward.recv_string()
                words = message.split()
                print(message)

                if words[0] == "Token":
                    if node_id == "0":
                        node = int(input("Which node to remove? "))
                        if node and node > 0:
                            publisher.send_string(f"Remove {node} {ports} {ports + 1}")
                            ports += 2
                            time.sleep(5)
                    sender_forward.send_string(f"Token {node_id} {int(words[2]) + 1}")

                if words[0] == "Leaving":
                    new_listen = words[1]
                    new_connect = words[2]

                    poller.unregister(receiver_forward)
                    receiver_forward.close()
                    sender_reverse.close()

                    sender_reverse = context.socket(zmq.PAIR)
                    sender_reverse.bind(f"tcp://*:{new_listen}")

                    receiver_forward = context.socket(zmq.PAIR)
                    receiver_forward.connect(f"tcp://localhost:{new_connect}")
                    poller.register(receiver_forward, zmq.POLLIN)

            if receiver_reverse in socks:
                message = receiver_reverse.recv_string()
                words = message.split()
                print(message)

                new_listen = words[1]
                new_connect = words[2]

                poller.unregister(receiver_reverse)
                receiver_reverse.close()
                sender_forward.close()

                sender_forward = context.socket(zmq.PAIR)
                sender_forward.bind(f"tcp://*:{new_listen}")

                receiver_reverse = context.socket(zmq.PAIR)
                receiver_reverse.connect(f"tcp://localhost:{new_connect}")
                poller.register(receiver_reverse, zmq.POLLIN)


            if subscriber in socks:
                print("Getting removed...")
                message = subscriber.recv_string()
                words = message.split()
                new_listen = words[2]
                new_connect = words[3]
                sender_forward.send_string(f"Leaving {new_connect} {new_listen}")
                sender_reverse.send_string(f"Leaving {new_listen} {new_connect}")
                poller.unregister(subscriber)
                subscriber.close()
                poller.unregister(receiver_reverse)
                receiver_reverse.close()
                poller.unregister(receiver_forward)
                receiver_forward.close()
                sender_forward.close()
                sender_reverse.close()
                return

    except KeyboardInterrupt:
        print(f"Node {node_id}: shutting down...")


if __name__ == "__main__":
    main()