from socket import *
import threading
import time
import math
from enum import Enum

from vector_clocks import VectorClockNode

# Maekawa algorithm node 
class MaekawaNode(VectorClockNode):

    def __init__(self, node_id, nodes, sets):
        super().__init__(node_id, nodes)
        self.sets = sets
        self.request_queue = []  # Queue of requests
        self.locked = False  # Lock status (in critical section or not)
        self.voted_for = None  # Node this process has voted for

    # Override to only send messages to nodes in the set
    def send_multicast(self, message):
        for i in range(len(self.sets[i])):
            if i != self.node_id:
                self.send_message(message, i)
    
    def MLockMutex(self):
        self.send_multicast("REQUEST")

    def MReleaseMutex(self):
        self.locked = False
        self.voted_for = None
        self.send_multicast("RELEASE")

    def handle_request(self, sender_id, received_vc):
        self.update_vector_clock(received_vc)
        # If this process hasn't voted yet, or the request is higher priority
        if self.voted_for is None:
            self.voted_for = sender_id
            self.send_message("GRANT", sender_id)
        else:
            self.request_queue.append(sender_id)

    def handle_grant(self):
        # When a node receives grants from all quorum members, it enters critical section
        if len(self.request_queue) == len(self.sets) - 1:
            self.locked = True
            print(f"Process {self.node_id} enters the critical section.")

    def handle_release(self):
        if self.request_queue:
            # Dequeue the next request and grant permission
            next_request = self.request_queue.pop(0)
            self.voted_for = next_request
            self.send_message("GRANT", next_request)

    # Overriding run_node method to handle Maekawa-specific messages
    def run_node(self):
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.bind(self.get_socket(self.node_id))
            while True:
                data, addr = s.recvfrom(1024)
                message, received_vc = data.decode().split(';')
                received_vc = list(map(int, received_vc.strip('[]').split(',')))

                # Process incoming messages
                if message == "REQUEST":
                    sender_id = int(addr[1])  # Assuming port represents node ID
                    self.handle_request(sender_id, received_vc)
                elif message == "GRANT":
                    self.handle_grant()
                elif message == "RELEASE":
                    self.handle_release()
                else:
                    # Handle vector clock updates and comparison
                    self.update_vector_clock(received_vc)
                    self.compare_vector_clocks(received_vc)

    def run(self):
        threading.Thread(target=self.run_node).start()

# Read the network configuration file
def read_network_file(network_file):
    network = []
    sets = []
    with open(network_file, 'r') as file:
        for line in file:
            socket_info = line.strip().split()
            address, port = socket_info[1].split(":")
            network.append([address, int(port)])
            set = socket_info[2].split(",")
            sets.append(set)
    print(network)
    print(sets)
    return network, sets

# Create a node array for simulation
def create_nodes(network_file):
    network, sets = read_network_file(network_file)
    nodes = [None] * len(network)
    for i in range(len(network)):
        nodes[i] = MaekawaNode(i, network, sets)
    return nodes

# Simulating 3 nodes on different ports
if __name__ == "__main__":

    # Create node array
    nodes = create_nodes("node_addresses.txt")
    
    # Run each node
    for node in nodes:
        node.run()