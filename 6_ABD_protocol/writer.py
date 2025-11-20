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

msg_id = ts = 0


def write(new_val):
    global msg_id, ts

    ts += 1
    msg_id += 1

    msg = [b"", b"write", str(msg_id).encode(), str(new_val).encode(), str(ts).encode()]
    for sock in sockets:
        sock.send_multipart(msg)

    print(f"Writer sent WRITE message with id {msg_id}")

    responses = 0
    majority = N // 2 + 1

    while responses < majority:
        socks = dict(poller.poll())

        for sock in sockets:
            if sock in socks:
                _, message, rcvd_msg_id = sock.recv_multipart()
                if message == b"write_ack" and int(rcvd_msg_id.decode()) == msg_id:
                    print(f"Writer received WRITE ACK for {msg_id}")
                    responses += 1

    print()

def main():
    print("Writer starting..")
    for i in range(10):
        num = random.randint(1, 100)
        print(f"Writer is writing {num}")
        write(num)
        time.sleep(4)

if __name__ == "__main__":
    main()
