import zmq
import time
import random

def main():
    context = zmq.Context()
    # Router socket for client
    router_socket = context.socket(zmq.ROUTER)
    router_socket.bind("tcp://*:5555")

    # Create dynamic DEALER sockets
    sockets = []
    poller = zmq.Poller()

    base_port = 5556
    num_participants = 3

    for i in range(num_participants):
        port = base_port + i
        sock = context.socket(zmq.DEALER)
        sock.connect(f"tcp://localhost:{port}")
        sockets.append(sock)
        poller.register(sock, zmq.POLLIN)
        print(f"Coordinator connected to participant at port {port}")
    poller.register(router_socket, zmq.POLLIN)

    print("Coordinator started, waiting for workers...")


    while True:
        print()
        # Wait for a "TRANSACTION" message from client
        client_id, _, message = router_socket.recv_multipart()
        if message == b"TRANSACTION":
            num = random.randint(1, 5)
            time.sleep(num)

            responses = 0

            for sock in sockets:
                sock.send_multipart([b"", b"PREPARE"])

            try:
                done = False
                while True:
                    socks = dict(poller.poll())

                    for sock in sockets:
                        if sock in socks:
                            _, message = sock.recv_multipart()

                            if message == b"PREPARED":
                                responses += 1
                                print("PREPARED")
                                if responses == num_participants:
                                    print("Broadcasting COMMIT.")
                                    for sock in sockets:
                                        sock.send_multipart([b"", b"COMMIT"])
                                    router_socket.send_multipart([client_id, b"", b"COMMIT"])
                                    done = True
                                    break

                            if message == b"ABORT":
                                print("Broadcasting ABORT.")
                                for sock in sockets:
                                    sock.send_multipart([b"", b"ABORT"])
                                router_socket.send_multipart([client_id, b"", b"ABORT"])
                                done = True
                                break
                    if done:
                        break

            except KeyboardInterrupt:
                print(f"Coordinator: shutting down...")
                router_socket.close(linger=0)
                context.term()

if __name__ == "__main__":
    main()
