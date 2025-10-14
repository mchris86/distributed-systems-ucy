import zmq


def main():
    context = zmq.Context()

    rep_socket = context.socket(zmq.REP)
    rep_socket.bind("tcp://*:5555")

    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind("tcp://*:5556")

    try:
        while True:
            message = rep_socket.recv_string()  # Receive message with REQ/REP
            rep_socket.send_string("ACK")  # Send acknowledgment to client
            pub_socket.send_string(message)  # Publish message to subscribers

    except KeyboardInterrupt:
        print("Monitor shutting down...")


if __name__ == "__main__":
    main()