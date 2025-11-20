import zmq
import time
import random

context = zmq.Context()

# Dealer socket for servers
dealer_socket_s1 = context.socket(zmq.DEALER)
dealer_socket_s1.connect("tcp://localhost:5556")
dealer_socket_s1.RCVTIMEO = 11000

dealer_socket_s2 = context.socket(zmq.DEALER)
dealer_socket_s2.connect("tcp://localhost:5557")
dealer_socket_s2.RCVTIMEO = 11000

dealer_socket_s3 = context.socket(zmq.DEALER)
dealer_socket_s3.connect("tcp://localhost:5558")
dealer_socket_s3.RCVTIMEO = 11000

msg_id = 0
val = -1
ts = 0

poller = zmq.Poller()
poller.register(dealer_socket_s1, zmq.POLLIN)
poller.register(dealer_socket_s2, zmq.POLLIN)
poller.register(dealer_socket_s3, zmq.POLLIN)

def read():
    global msg_id, val, ts
    print("QUERY PHASE")
    msg_id += 1
    msg = [b"", b"query", str(msg_id).encode()]
    dealer_socket_s1.send_multipart(msg)
    dealer_socket_s2.send_multipart(msg)
    dealer_socket_s3.send_multipart(msg)

    responses = 0

    while True:
        socks = dict(poller.poll())
        if dealer_socket_s1 in socks:
            # _, message, rcvd_msg_id, rcv_val, rcv_ts = dealer_socket_s1.recv_multipart()
            parts = dealer_socket_s1.recv_multipart()
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

        if dealer_socket_s2 in socks:
            parts = dealer_socket_s2.recv_multipart()
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

        if dealer_socket_s3 in socks:
            parts = dealer_socket_s3.recv_multipart()
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

        if responses >= 2:
            break

    print("INFORM PHASE")
    msg_id += 1
    msg = [b"", b"inform", str(msg_id).encode(), str(val).encode(), str(ts).encode() ]
    dealer_socket_s1.send_multipart(msg)
    dealer_socket_s2.send_multipart(msg)
    dealer_socket_s3.send_multipart(msg)

    responses = 0


    while True:
        socks = dict(poller.poll())
        if dealer_socket_s1 in socks:
            parts = dealer_socket_s1.recv_multipart()
            message = parts[1]
            rcvd_msg_id = int(parts[2].decode())
            if message == b"inform_ack" and rcvd_msg_id == msg_id:
                print(f"Reader received INFORM ACK for {msg_id}")
                responses += 1

        if dealer_socket_s2 in socks:
            parts = dealer_socket_s2.recv_multipart()
            message = parts[1]
            rcvd_msg_id = int(parts[2].decode())
            if message == b"inform_ack" and rcvd_msg_id == msg_id:
                print(f"Reader received INFORM ACK for {msg_id}")
                responses += 1

        if dealer_socket_s3 in socks:
            parts = dealer_socket_s3.recv_multipart()
            message = parts[1]
            rcvd_msg_id = int(parts[2].decode())
            if message == b"inform_ack" and rcvd_msg_id == msg_id:
                print(f"Reader received INFORM ACK for {msg_id}")
                responses += 1

        if responses >= 2:
            break

    print(f"Reader is reading {val}\n")

def main():
    for i in range(10):
        read()
        num = random.randint(1, 5)
        time.sleep(num)

if __name__ == "__main__":
    main()
