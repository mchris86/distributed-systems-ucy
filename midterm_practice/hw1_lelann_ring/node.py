import zmq
import sys
import time


def main():
    node_id = sys.argv[1]
    rcv_port = sys.argv[2]
    snd_port = sys.argv[3]

    context = zmq.Context()

    sender = context.socket(zmq.PAIR)
    sender.bind(f"tcp://*:{snd_port}")

    receiver = context.socket(zmq.PAIR)
    receiver.connect(f"tcp://localhost:{rcv_port}")

    if node_id == "0":
        print("Node 0 creating token")
        sender.send_string("1")

    try:
        while True:
            rcv_msg = receiver.recv_string()
            print(rcv_msg)
            time.sleep(1)
            sender.send_string(str(int(rcv_msg)+1))

    except KeyboardInterrupt:
        print(f"Node {node_id} exiting...")


if __name__ == "__main__":
    main()

