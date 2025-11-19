import zmq
import sys
import random


def main():
    context = zmq.Context()

    participant_port = sys.argv[1]
    router_socket = context.socket(zmq.ROUTER)
    router_socket.bind(f"tcp://*:{participant_port}")
    print(f"Participant {participant_port} is running...")

    while True:
        print()
        coordinator_id, _, message = router_socket.recv_multipart()
        if message == b"PREPARE":
            print(f"Participant {participant_port} received PREPARE message")
            rand_num = random.randint(0, 2)
            if rand_num % 2 == 0:
                router_socket.send_multipart([coordinator_id, b"", b"PREPARED"])
                print(f"Participant {participant_port} sent PREPARED message")
            else:
                router_socket.send_multipart([coordinator_id, b"", b"ABORT"])
                print(f"Participant {participant_port} sent ABORT message")

            _, _, message = router_socket.recv_multipart()
            if message == b"COMMIT":
                router_socket.send_multipart([coordinator_id, b"", b"ACK"])
                print(f"Participant {participant_port} sent ACK message")
            elif message == b"ABORT":
                router_socket.send_multipart([coordinator_id, b"", b"ACK"])
                print(f"Participant {participant_port} sent ACK message")
            else:
                exit(-1)

if __name__ == "__main__":
    main()



