import zmq
import time
import random
import signal
import sys


class ChandyProcess:

    def __init__(self, process_id, num_processes, process_port):
        self.process_id = process_id
        self.num_processes = num_processes
        self.process_port = process_port

        # Algorithm variables
        self.lc = 1 if process_id == 0 else 0
        self.queue = []
        self.token = [0] * num_processes if process_id == 0 else None
        self.in_cs = False

        # ZeroMQ setup
        self.context = zmq.Context()
        self.poller = zmq.Poller()

        # ROUTER for receiving
        self.router_socket = self.context.socket(zmq.ROUTER)
        self.router_socket.bind(f"tcp://*:{process_port}")
        self.poller.register(self.router_socket, zmq.POLLIN)

        self.dealer_sockets = {}
        for i in range(self.num_processes):
            if i != process_id:
                sock = self.context.socket(zmq.DEALER)
                sock.connect(f"tcp://localhost:{5555 + i}")
                self.dealer_sockets[i] = sock
                print(f"Process {process_id} connected to dealer_socket at port {5555 + i}")

        time.sleep(0.5)

        self.sigint_received = False
        signal.signal(signal.SIGINT, self.handle_sigint)

        print(f"Process {process_id} initialized. Has token: {bool(self.token)}")
        print(self.token)

        # Process 0 enters CS immediately
        if self.process_id == 0:
            self.critical_section()

    def handle_sigint(self, signum, frame):
        if not self.in_cs:
            print(f"\n[Process {self.process_id}] SIGINT - requesting CS")
            self.sigint_received = True

    def critical_section(self):
        """Enter critical section, do work, exit"""
        self.in_cs = True

        self.token[self.process_id] = self.lc

        print(f"\n{'=' * 60}")
        print(f"[Process {self.process_id}] *** ENTERING CS ***")
        print(f"{'=' * 60}\n")

        # Work in CS
        num = random.randint(1, 6)
        time.sleep(num)

        print(f"\n{'=' * 60}")
        print(f"[Process {self.process_id}] *** LEAVING CS *** (after {10:.2f}s)")
        print(f"{'=' * 60}\n")

        # Exit CS
        self.in_cs = False

        # Process queue and send token
        self.token[self.process_id] = self.lc

        while self.queue:
            req_process, req_lc = self.queue.pop(0)

            if req_lc > self.token[req_process]:
                # Send token
                print(f"[Process {self.process_id}] Sending token to process {req_process}")
                print(f"[Process {self.process_id}] Token state: {self.token}")

                token_str = ','.join(str(x) for x in self.token)
                self.dealer_sockets[req_process].send_multipart([b"", b"TOKEN", token_str.encode()])
                self.token = None
                return
            else:
                print(f"[Process {self.process_id}] Ignoring outdated request from {req_process}")

        print(f"[Process {self.process_id}] No pending requests. Keeping token: {self.token}.")

    def run(self):
        """Main event loop"""
        print(f"\n[Process {self.process_id}] Starting main loop...")
        print(f"[Process {self.process_id}] Press Ctrl-C to request CS\n")

        try:
            while True:
                # Handle SIGINT
                if self.sigint_received:
                    self.sigint_received = False

                    if self.token is None:
                        # Request token
                        self.lc += 1

                        print(f"[Process {self.process_id}] Broadcasting request ({self.process_id}, {self.lc})")

                        pid_bytes = str(self.process_id).encode()
                        lc_bytes = str(self.lc).encode()

                        # Dealer broadcasts request to all nodes
                        msg = [b"", b"REQUEST", pid_bytes, lc_bytes]
                        for sock in self.dealer_sockets.values():
                            sock.send_multipart(msg)

                        print(f"[Process {self.process_id}] Waiting for token...")
                    else:
                        # Already have token
                        self.lc += 1
                        self.critical_section()

                # Check for messages
                socks = dict(self.poller.poll(200))  # Timeout at 200ms so that we check for sigint flag

                if self.router_socket in socks:
                    parts = self.router_socket.recv_multipart()

                    if parts[2] == b'REQUEST':
                        # Handle REQUEST
                        sender_id = int(parts[3].decode())
                        sender_lc = int(parts[4].decode())

                        print(f"[Process {self.process_id}] Received REQUEST from process {sender_id} with lc={sender_lc}")

                        if self.token and not self.in_cs and not self.queue:
                            # Send token immediately
                            print(f"[Process {self.process_id}] Sending token to process {sender_id}")

                            token_str = ','.join(str(x) for x in self.token)
                            self.dealer_sockets[sender_id].send_multipart([b"", b'TOKEN', token_str.encode()])

                            self.token = None
                        else:
                            # Add to queue
                            self.queue.append((sender_id, sender_lc))
                            print(f"[Process {self.process_id}] Added to queue. Queue size: {len(self.queue)}")

                    elif parts[2] == b'TOKEN':
                        # Handle TOKEN
                        token_str = parts[3].decode()
                        token = [int(x) for x in token_str.split(',')]

                        print(f"[Process {self.process_id}] Received TOKEN: {token}")
                        self.token = token
                        self.critical_section()

                time.sleep(0.01)

        except KeyboardInterrupt:
            print(f"\n[Process {self.process_id}] Shutting down...")
        finally:
            self.router_socket.close()
            for sock in self.dealer_sockets.values():
                sock.close()
            self.context.term()


def main():
    if len(sys.argv) < 3:
        print("Usage: python3 node.py <num_processes> <port>")
        sys.exit(1)

    base_port = 5555
    num_processes = int(sys.argv[1])
    process_port = int(sys.argv[2])
    process_id = process_port - base_port
    print(f"Process {process_id} starting at port {process_port}.")

    if process_id < 0 or process_id >= num_processes:
        print(f"Error: process_id must be between 0 and {num_processes - 1}")
        sys.exit(1)

    process = ChandyProcess(process_id, num_processes, process_port)
    process.run()


if __name__ == '__main__':
    main()