import zmq


def main():
    context = zmq.Context()

    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://*:5555")

    try:
        while True:
            message = rep_socket.recv()
            print(message)
            rep_socket.send_string("ACK")

    except KeyboardInterrupt:
        print("Monitor shutting down...")


if __name__ == "__main__":
    main()