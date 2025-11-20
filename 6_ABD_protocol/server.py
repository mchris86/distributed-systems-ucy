import zmq
import sys
import random
import time



def main():
    context = zmq.Context()

    server_port = sys.argv[1]
    router_socket = context.socket(zmq.ROUTER)
    router_socket.bind(f"tcp://*:{server_port}")
    print(f"Server {server_port} is running...")

    val = ts = 0

    while True:
        print()
        # client_id, _, message = router_socket.recv_multipart()
        parts = router_socket.recv_multipart()
        if parts[2] == b"write":
            print(f"Server {server_port} received WRITE message")
            writer_id = parts[0]
            msg_id = parts[3]
            val = parts[4].decode()
            max_ts = int(parts[5].decode())
            ts = max_ts + 1

            num = random.randint(1, 5)
            time.sleep(num)

            router_socket.send_multipart([writer_id, b"", b"write_ack", msg_id])
            print(f"Server {server_port} sent WRITE_ACK message")

        if parts[2] == b"query":
            print(f"Server {server_port} received QUERY message")
            num = random.randint(1, 5)
            time.sleep(num)
            reader_id = parts[0]
            msg_id = parts[3]

            router_socket.send_multipart([reader_id, b"", b"query_ack", msg_id, str(val).encode(), str(ts).encode()])
            print(f"Server {server_port} sent QUERY_ACK message")

        if parts[2] == b"inform":
            print(f"Server {server_port} received INFORM message")
            reader_id = parts[0]
            msg_id = parts[3]
            inform_val = parts[4].decode()
            max_ts = int(parts[5].decode())

            if max_ts > ts:
                ts = max_ts
                val = inform_val

            num = random.randint(1, 5)
            time.sleep(num)

            router_socket.send_multipart([reader_id, b"", b"inform_ack", msg_id])
            print(f"Server {server_port} sent INFORM ACK message")


if __name__ == "__main__":
    main()
