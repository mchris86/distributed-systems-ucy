import zmq


def main():
    context = zmq.Context()

    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://*:7000")

    publisher = context.socket(zmq.PUB)
    publisher.bind("tcp://*:5555")

    try:
        while True:
            message = rep_socket.recv_string()
            rep_socket.send_string("ACK")

            publisher.send_string(message)

    except KeyboardInterrupt:
        print(f"Monitor shutting down...")


if __name__ == "__main__":
    main()

