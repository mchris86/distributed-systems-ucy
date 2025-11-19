import zmq

def main():
    client_id = "1"

    context = zmq.Context()
    dealer_socket = context.socket(zmq.DEALER)
    dealer_socket.identity = client_id.encode()  # Client identity
    dealer_socket.connect("tcp://localhost:5555")
    dealer_socket.RCVTIMEO = 11000

    print(f"Client {client_id} is running.")

    while True:
        print()
        # Notify the coordinator that this client wants to do a transaction
        dealer_socket.send_multipart([b"", b"TRANSACTION"])
        print("Client sent TRANSACTION request to coordinator.")

        # Wait for coordinator response
        parts = dealer_socket.recv_multipart()
        if len(parts) >= 2:
            response = parts[1].decode()
            print(f"Client received response: {response}")
        else:
            print("Client received no response.")
            break

    dealer_socket.close()
    context.term()
    print("Client closed.")

if __name__ == "__main__":
    main()
