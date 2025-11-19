import zmq
import time
import random

def main():
    context = zmq.Context()
    # Router socket for client
    router_socket = context.socket(zmq.ROUTER)
    router_socket.bind("tcp://*:5555")

    # Dealer socket for participants
    dealer_socket_p1 = context.socket(zmq.DEALER)
    dealer_socket_p1.connect("tcp://localhost:5556")

    dealer_socket_p2 = context.socket(zmq.DEALER)
    dealer_socket_p2.connect("tcp://localhost:5557")

    dealer_socket_p3 = context.socket(zmq.DEALER)
    dealer_socket_p3.connect("tcp://localhost:5558")

    poller = zmq.Poller()
    poller.register(dealer_socket_p1, zmq.POLLIN)
    poller.register(dealer_socket_p2, zmq.POLLIN)
    poller.register(dealer_socket_p3, zmq.POLLIN)
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
            dealer_socket_p1.send_multipart([b"", b"PREPARE"])
            dealer_socket_p2.send_multipart([b"", b"PREPARE"])
            dealer_socket_p3.send_multipart([b"", b"PREPARE"])

            try:
                while True:
                    socks = dict(poller.poll())

                    if dealer_socket_p1 in socks:
                        _, message = dealer_socket_p1.recv_multipart()
                        if message == b"PREPARED":
                            responses += 1
                            print("PREPARED")
                            if responses == 3:
                                print("Broadcasting COMMIT.")
                                dealer_socket_p1.send_multipart([b"", b"COMMIT"])
                                dealer_socket_p2.send_multipart([b"", b"COMMIT"])
                                dealer_socket_p3.send_multipart([b"", b"COMMIT"])
                                router_socket.send_multipart([client_id, b"", b"COMMIT"])
                                break
                        if message == b"ABORT":
                            print("Broadcasting ABORT.")
                            dealer_socket_p1.send_multipart([b"", b"ABORT"])
                            dealer_socket_p2.send_multipart([b"", b"ABORT"])
                            dealer_socket_p3.send_multipart([b"", b"ABORT"])
                            router_socket.send_multipart([client_id, b"", b"ABORT"])
                            break

                    if dealer_socket_p2 in socks:
                        _, message = dealer_socket_p2.recv_multipart()
                        if message == b"PREPARED":
                            responses += 1
                            print("PREPARED")
                            if responses == 3:
                                print("Broadcasting COMMIT.")
                                dealer_socket_p1.send_multipart([b"", b"COMMIT"])
                                dealer_socket_p2.send_multipart([b"", b"COMMIT"])
                                dealer_socket_p3.send_multipart([b"", b"COMMIT"])
                                router_socket.send_multipart([client_id, b"", b"COMMIT"])
                                break
                        if message == b"ABORT":
                            print("Broadcasting ABORT.")
                            dealer_socket_p1.send_multipart([b"", b"ABORT"])
                            dealer_socket_p2.send_multipart([b"", b"ABORT"])
                            dealer_socket_p3.send_multipart([b"", b"ABORT"])
                            router_socket.send_multipart([client_id, b"", b"ABORT"])
                            break

                    if dealer_socket_p3 in socks:
                        _, message = dealer_socket_p3.recv_multipart()
                        if message == b"PREPARED":
                            responses += 1
                            print("PREPARED")
                            if responses == 3:
                                print("Broadcasting COMMIT.")
                                dealer_socket_p1.send_multipart([b"", b"COMMIT"])
                                dealer_socket_p2.send_multipart([b"", b"COMMIT"])
                                dealer_socket_p3.send_multipart([b"", b"COMMIT"])
                                router_socket.send_multipart([client_id, b"", b"COMMIT"])
                                break
                        if message == b"ABORT":
                            print("Broadcasting ABORT.")
                            dealer_socket_p1.send_multipart([b"", b"ABORT"])
                            dealer_socket_p2.send_multipart([b"", b"ABORT"])
                            dealer_socket_p3.send_multipart([b"", b"ABORT"])
                            router_socket.send_multipart([client_id, b"", b"ABORT"])
                            break

            except KeyboardInterrupt:
                print(f"Coordinator: shutting down...")
                router_socket.close(linger=0)
                context.term()



if __name__ == "__main__":
    main()
