from socket import *
import threading
import time
import math
from enum import Enum

from vector_clocks import VectorClockNode

# Maekawa algorithm node 
class MaekawaNode(VectorClockNode):

    def __init__(self, node_id, nodes, set):
        super().__init__(node_id, nodes)
        self.set = set
        self.request_queue = []  # Queue of requests
        self.locked = False  # Lock status (in critical section or not)
        self.voted_for = None  # Node this process has voted for
        self.grant_count = 0
    
    def MLockMutex(self):
        self.send_multicast("REQUEST")

    def MReleaseMutex(self):
        if self.locked == True:
            self.locked = False
            self.send_multicast("RELEASE")
            self.grant_count = 0
        else:
            print(f"P{self.node_id} cannot release a mutex it doesn't have")

    # TODO: check timing?
    def handle_request(self, node_id, received_vc):
        if self.locked:
            print(f"P{self.node_id} added P{node_id} to request queue because currently in CS")
            self.request_queue.append(node_id)
        elif self.voted_for != None:
            print(f"P{self.node_id} added P{node_id} to request queue because vote is given to P{self.voted_for}")
            self.request_queue.append(node_id)
        else:
            self.voted_for = node_id
            self.send_message("GRANT", node_id)

    def handle_grant(self):
        self.grant_count += 1
        if self.grant_count == len(self.set):
            self.locked = True
            print(f"P{self.node_id} enters the critical section.")

    def handle_release(self):
        if self.request_queue:
            next_request = self.request_queue.pop(0)
            self.voted_for = next_request
            self.send_message("GRANT", next_request)
        else:
            self.voted_for = None

    # Override multicast to only send messages to nodes in the set
    def send_multicast(self, message):
        for i in self.set:
            if i != self.node_id:
                self.send_message(message, i)

    # Overriding run_node method to handle Maekawa-specific messages
    def run_node(self):
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.bind(self.get_socket(self.node_id))
            while True:
                data, addr = s.recvfrom(1024)
                node_id, message, received_vc = data.decode().split(';')
                received_vc = list(map(int, received_vc.strip('[]').split(',')))
                print(f"P{self.node_id} received message from P{node_id}: '{message}'")
                self.update_vector_clock(received_vc)

                # Process incoming messages
                if message == "REQUEST":
                    self.handle_request(node_id, received_vc)
                elif message == "GRANT":
                    self.handle_grant()
                elif message == "RELEASE":
                    self.handle_release()

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
            set = list(map(int, socket_info[2].split(",")))
            sets.append(set)
    print(network)
    print(sets)
    return network, sets

# Create a node array for simulation
def create_nodes(network_file):
    network, sets = read_network_file(network_file)
    nodes = [None] * len(network)
    for i in range(len(network)):
        nodes[i] = MaekawaNode(i, network, sets[i])
    return nodes

# Simulating 3 nodes on different ports
if __name__ == "__main__":

    # Create node array
    nodes = create_nodes("node_addresses.txt")
    
    # Run each node
    for node in nodes:
        node.run()

    nodes[0].MLockMutex()  # P0 requests the critical section
    time.sleep(1)

    nodes[1].MLockMutex()  # P1 requests the critical section
    time.sleep(1)

    nodes[2].MLockMutex()  # P2 requests the critical section
    time.sleep(1)

    nodes[0].MReleaseMutex()  # P0 releases the critical section
    time.sleep(1)

    nodes[1].MReleaseMutex()  # P1 releases the critical section
    time.sleep(1)

    nodes[2].MReleaseMutex()  # P2 releases the critical section
    time.sleep(1)