import zmq
import time
import random
import sys

context = zmq.Context()

# Read number of servers
if len(sys.argv) < 2:
    print("Usage: python3 writer.py N")
    exit(-1)

N = int(sys.argv[1])

# Create dynamic DEALER sockets
sockets = []
poller = zmq.Poller()

base_port = 5556

for i in range(N):
    port = base_port + i
    sock = context.socket(zmq.DEALER)
    sock.connect(f"tcp://localhost:{port}")
    sock.RCVTIMEO = 11000
    sockets.append(sock)
    poller.register(sock, zmq.POLLIN)
    print(f"Writer connected to server at port {port}")

msg_id = 0
val = -1
ts = 0


def read():
    global msg_id, val, ts

    print("QUERY PHASE")
    msg_id += 1

    msg = [b"", b"query", str(msg_id).encode()]
    for sock in sockets:
        sock.send_multipart(msg)

    responses = 0
    majority = N // 2 + 1

    while responses < majority:
        socks = dict(poller.poll())

        for sock in sockets:
            if sock in socks:
                parts = sock.recv_multipart()
                message = parts[1]
                rcvd_msg_id = int(parts[2].decode())
                if message == b"query_ack" and rcvd_msg_id == msg_id:
                    rcv_val = parts[3]
                    rcv_ts = parts[4]
                    if int(rcv_ts.decode()) > ts:
                        val = int(rcv_val.decode())
                        ts = int(rcv_ts.decode())
                    print(f"Reader received QUERY ACK for {msg_id}")
                    responses += 1

    print("INFORM PHASE")
    msg_id += 1
    msg = [b"", b"inform", str(msg_id).encode(), str(val).encode(), str(ts).encode() ]
    for sock in sockets:
        sock.send_multipart(msg)

    responses = 0

    while responses < majority:
        socks = dict(poller.poll())

        for sock in sockets:
            if sock in socks:
                parts = sock.recv_multipart()
                message = parts[1]
                rcvd_msg_id = int(parts[2].decode())
                if message == b"inform_ack" and rcvd_msg_id == msg_id:
                    print(f"Reader received INFORM ACK for {msg_id}")
                    responses += 1

    print(f"Reader is reading {val}\n")

def main():
    for i in range(10):
        read()
        num = random.randint(1, 5)
        time.sleep(num)

if __name__ == "__main__":
    main()
