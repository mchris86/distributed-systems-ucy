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

msg_id = ts = 0

poller = zmq.Poller()
poller.register(dealer_socket_s1, zmq.POLLIN)
poller.register(dealer_socket_s2, zmq.POLLIN)
poller.register(dealer_socket_s3, zmq.POLLIN)

def write(new_val):
    global msg_id, ts

    ts += 1
    msg_id += 1
    msg = [b"", b"write", str(msg_id).encode(), str(new_val).encode(), str(ts).encode()]
    dealer_socket_s1.send_multipart(msg)
    dealer_socket_s2.send_multipart(msg)
    dealer_socket_s3.send_multipart(msg)
    print(f"Writer sent WRITE message with id {msg_id}")

    responses = 0

    while True:
        socks = dict(poller.poll())
        if dealer_socket_s1 in socks:
            _, message, rcvd_msg_id = dealer_socket_s1.recv_multipart()
            if message == b"write_ack" and int(rcvd_msg_id.decode()) == msg_id:
                print(f"Writer received WRITE ACK for {msg_id}")
                responses += 1

        if dealer_socket_s2 in socks:
            _, message, rcvd_msg_id = dealer_socket_s2.recv_multipart()
            if message == b"write_ack" and int(rcvd_msg_id.decode()) == msg_id:
                print(f"Writer received WRITE ACK for {msg_id}")
                responses += 1

        if dealer_socket_s3 in socks:
            _, message, rcvd_msg_id = dealer_socket_s3.recv_multipart()
            if message == b"write_ack" and int(rcvd_msg_id.decode()) == msg_id:
                print(f"Writer received WRITE ACK for {msg_id}")
                responses += 1

        if responses >= 2:
            break

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
