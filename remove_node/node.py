import time
import zmq
import sys

def main():
    context = zmq.Context()

    node_id = sys.argv[1]
    receive_port_forward = sys.argv[2]
    send_port_forward = sys.argv[3]
    receive_port_reverse = sys.argv[4]
    send_port_reverse = sys.argv[5]

    # Forward
    sender_forward = context.socket(zmq.PAIR)
    sender_forward.bind("tcp://*:%s" % send_port_forward)
    receiver_forward = context.socket(zmq.PAIR)
    receiver_forward.connect("tcp://localhost:%s" % receive_port_forward)

    # Reverse
    sender_reverse = context.socket(zmq.PAIR)
    sender_reverse.bind("tcp://*:%s" % send_port_reverse)
    receiver_reverse = context.socket(zmq.PAIR)
    receiver_reverse.connect("tcp://localhost:%s" % receive_port_reverse)

    # Poller
    poller = zmq.Poller()
    poller.register(receiver_reverse)
    poller.register(receiver_forward)


    if node_id == "0":
        print(f"Node {node_id} creating token")
        sender_forward.send_string(f"Token 0 0")
        sender_reverse.send_string(f"Reverse 0 0")
        pub_socket = context.socket(zmq.PUB)
        pub_socket.bind("tcp://*:7000")
        ports = 9000
    else:
        sub_socket = context.socket(zmq.SUB)
        sub_socket.connect(f"tcp://localhost:{7000+int(node_id)}")
        sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        
    try:
        while True:
            socks = dict(poller.poll())

            if receiver_forward in socks:

                if node_id == "0":
                    node = int(input("Want to remove a node?"))
                    if node > 0:
                        pub_socket.send_string(f"Remove {node} {ports} {ports+1} ")
                        ports += 2
                    
                message = receiver_forward.recv_string()
                print(message)
                time.sleep(1)
                words = message.split()
                # Send message to next node
                sender_forward.send_string(f"Token {node_id} {int(words[2]) + 1}")

            if receiver_reverse in socks:
                pass
                # message = receiver_reverse.recv_string()
                # print(message)
                # time.sleep(1)
                # words = message.split()
                # # Send message to next node
                # sender_reverse.send_string(f"Reverse {node_id} {int(words[2]) + 1}")

            if sub_socket in socks:  # Receive message from monitor
                message = sub_socket.recv()
                node = message.split()[1]
                new_listening_port = message.split()[2]
                new_connecting_port = message.split()[3]
                if node == node_id:
                    sender_reverse.send_string(f"Leaving {new_listening_port} {new_connecting_port}")
                    sender_forward.send_string(f"Leaving {new_connecting_port} {new_listening_port}")



    except KeyboardInterrupt:
            print(f"Node {node_id}: shutting down...")

if __name__ == "__main__":
    main()
