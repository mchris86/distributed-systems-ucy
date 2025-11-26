import zmq
import time
import random
import signal
import sys


class ChandyProcess:

    def __init__(self, process_id, num_processes, process_port, request_rate=0.01,
                 cs_duration_range=(0.1, 0.5), network_latency=0.5, log_interval=0.1):
        self.process_id = process_id
        self.num_processes = num_processes
        self.process_port = process_port

        # Algorithm variables
        self.lc = 1 if process_id == 0 else 0
        self.queue = []
        self.token = [0] * num_processes if process_id == 0 else None
        self.in_cs = False

        # Experiment parameters
        self.request_rate = request_rate  # λ (requests/second)
        self.cs_duration_range = cs_duration_range  # (min, max) for CS duration
        self.network_latency = network_latency  # Latency in seconds
        self.log_interval = log_interval  # How often to log queue size

        # Logging
        self.log_file = open(f"process_{process_id}_log.txt", "w")
        self.log_file.write("timestamp, queue_size\n")

        # Timers
        self.start_time = time.time()
        self.last_log_time = 0
        self.next_request_time = self.start_time + self.generate_next_request_time()

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


        self.sigint_received = False
        signal.signal(signal.SIGINT, self.handle_sigint)

        print(f"Process {process_id} initialized. Has token: {bool(self.token)}")
        print(self.token)

        # Process 0 enters CS immediately
        if self.process_id == 0:
            self.critical_section()

    def generate_next_request_time(self):
        """Generate next request time using exponential distribution"""
        if self.request_rate <= 0:
            return float('inf')  # Never auto-generate

        # Exponential distribution: -ln(U) / λ
        return random.expovariate(self.request_rate)

    def should_generate_request(self):
        """Check if it's time to generate a request"""
        if self.request_rate <= 0:
            return False

        current_time = time.time()
        if current_time >= self.next_request_time:
            # Schedule next request
            self.next_request_time = current_time + self.generate_next_request_time()
            return True
        return False

    def log_queue_size(self):
        """Log current queue size with timestamp"""
        current_time = time.time() - self.start_time

        # Log periodically (every log_interval seconds)
        if current_time - self.last_log_time >= self.log_interval:
            queue_size = len(self.queue)
            self.log_file.write(f"{current_time:.3f},{queue_size}\n")
            self.log_file.flush()  # Make sure it's written immediately
            self.last_log_time = current_time

    def handle_sigint(self, signum, frame):
        if not self.in_cs:
            print(f"\n[Process {self.process_id}] SIGINT - requesting CS")
            self.sigint_received = True

    def critical_section(self):
        """Enter critical section, do work, exit"""
        self.in_cs = True

        # Update token
        self.token[self.process_id] = self.lc

        print(f"\n{'=' * 60}")
        print(f"[Process {self.process_id}] *** ENTERING CS ***")
        print(f"{'=' * 60}\n")

        # Work in CS
        cs_duration = random.uniform(*self.cs_duration_range)
        time.sleep(cs_duration)

        print(f"\n{'=' * 60}")
        print(f"[Process {self.process_id}] *** LEAVING CS *** (after {cs_duration:.2f}s)")
        print(f"{'=' * 60}\n")

        # Exit CS
        self.in_cs = False

        # Process queue and send token
        while self.queue:
            req_process, req_lc = self.queue.pop(0)

            if req_lc > self.token[req_process]:
                # Send token
                print(f"[Process {self.process_id}] Sending token to process {req_process}")
                print(f"[Process {self.process_id}] Token state: {self.token}")

                token_str = ','.join(str(x) for x in self.token)
                time.sleep(self.network_latency)  # Simulate network latency
                self.dealer_sockets[req_process].send_multipart([b"", b"TOKEN", token_str.encode()])
                self.token = None
                return
            else:
                print(f"[Process {self.process_id}] Ignoring outdated request from {req_process}")

        print(f"[Process {self.process_id}] No pending requests. Keeping token: {self.token}.")

    def run(self, experiment_duration=120):
        """Main event loop"""
        print(f"\n[Process {self.process_id}] Starting experiment...")
        print(f"  Request rate: {self.request_rate} requests/sec")
        print(f"  Duration: {experiment_duration} seconds")
        print(f"  Network latency: {self.network_latency}s\n")

        experiment_end_time = self.start_time + experiment_duration

        try:
            while time.time() < experiment_end_time:
                # Log queue size periodically
                self.log_queue_size()

                # AUTO-GENERATE REQUEST based on rate
                if self.should_generate_request() and not self.in_cs:
                    if self.token is None:
                        # Request token
                        self.lc += 1

                        print(f"[Process {self.process_id}] Broadcasting request ({self.process_id}, {self.lc})")

                        pid_bytes = str(self.process_id).encode()
                        lc_bytes = str(self.lc).encode()

                        # Dealer broadcasts request to all nodes
                        msg = [b"", b"REQUEST", pid_bytes, lc_bytes]
                        time.sleep(self.network_latency)  # Simulate network latency
                        for sock in self.dealer_sockets.values():
                            sock.send_multipart(msg)

                        print(f"[Process {self.process_id}] Waiting for token...")
                    else:
                        # Already have token
                        self.lc += 1
                        self.critical_section()

                # Check for messages
                socks = dict(self.poller.poll(50))  # Timeout at 50ms so that we check for sigint flag

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
                            time.sleep(self.network_latency)  # Simulate network latency
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

            print(f"\n[Process {self.process_id}] Experiment completed!")

        except KeyboardInterrupt:
            print(f"\n[Process {self.process_id}] Shutting down...")
        finally:
            self.print_results()
            self.log_file.close()
            self.router_socket.close()
            for sock in self.dealer_sockets.values():
                sock.close()
            self.context.term()

    def print_results(self):
        self.log_file.close()
        print("Printing results...")

        # Read log file to calculate stats
        with open(f"process_{self.process_id}_log.txt", "r") as f:
            lines = f.readlines()[1:]  # Skip header
            if lines:
                queue_sizes = [int(line.split(',')[1]) for line in lines]
                avg_queue = sum(queue_sizes) / len(queue_sizes)
                max_queue = max(queue_sizes)

                print(f"\n[Process {self.process_id}] Statistics:")
                print(f"  Average queue size: {avg_queue:.2f}")
                print(f"  Maximum queue size: {max_queue}")


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

    if len(sys.argv) == 3:
        process = ChandyProcess(process_id, num_processes, process_port, request_rate=1)
        process.run() # Default experiment duration = 120 seconds
    elif len(sys.argv) == 4:
        if process_id % 3 == 0:
            print(f"Process {process_id} running with request rate = 0.01 ")
            process = ChandyProcess(process_id, num_processes, process_port, request_rate=0.01)
        elif process_id % 3 == 1:
            print(f"Process {process_id} running with request rate = 0.1 ")
            process = ChandyProcess(process_id, num_processes, process_port, request_rate=0.1)
        else:
            print(f"Process {process_id} running with request rate = 1 ")
            process = ChandyProcess(process_id, num_processes, process_port, request_rate=1)
        process.run()  # Default experiment duration = 120 seconds


if __name__ == '__main__':
    main()