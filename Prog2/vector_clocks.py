from socket import *
import threading
import time

# Vector clock node class
class VectorClockNode:

    def __init__(self, node_id, nodes):
        self.node_id = node_id
        self.nodes = nodes
        self.total_nodes = len(self.nodes)
        self.vc = [0] * self.total_nodes

    # Helper socket parse function
    def get_socket(self, node_id):
        return (self.nodes[node_id][0], self.nodes[node_id][1])
    
    # Helper vc print function
    def print_vc(self):
        print(f"P{self.node_id}: {self.vc}")

    # Helper clock increment function
    def increment_clock(self):
        self.vc[self.node_id] += 1
        self.print_vc()

    # Simulate a local event
    def local_event(self):
        self.increment_clock()

    # update vector clock
    def update_vector_clock(self, received_vc):
        for i in range(self.total_nodes):
            self.vc[i] = max(self.vc[i], received_vc[i])
        self.increment_clock()

    # compare vector clocks
    def compare_vector_clocks(self, received_vc):

        # Check if self vc is less than received vc
        cond_one = True
        cond_two = False
        for i in range(self.total_nodes):
            if self.vc[i] > received_vc[i]:
                cond_one = False
            if self.vc[i] < received_vc[i]:
                cond_two = True

        # Check if received vc is less than this vc
        cond_one_2 = True
        cond_two_2 = False
        for i in range(self.total_nodes):
            if received_vc[i] > self.vc[i]:
                cond_one_2 = False
            if received_vc[i] < self.vc[i]:
                cond_two_2 = True

        # Print result
        if cond_one and cond_two:
            print(f"This VC happened before received VC --> {self.vc} < {received_vc}")
        elif cond_one_2 and cond_two_2:
            print(f"Received VC happened before this VC --> {received_vc} < {self.vc}")
        else:
            print(f"These events might be concurrent --> {received_vc} = {self.vc}")

    # Send message to a certain node
    def send_message(self, message, node_id):
        self.increment_clock()
        message_vc = f"{message};{self.vc}"
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.sendto(message_vc.encode(), self.get_socket(node_id))

    # Send message to the whole network
    def send_multicast(self, message):
        for i in range(self.total_nodes):
            if i != self.node_id:
                self.send_message(message, i)
    
    # Node receive loop
    def run_node(self):
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.bind(self.get_socket(self.node_id))
            while True:
                data, addr = s.recvfrom(1024)
                message, received_vc = data.decode().split(';')
                received_vc = list(map(int, received_vc.strip('[]').split(',')))
                self.update_vector_clock(received_vc)
                self.compare_vector_clocks(received_vc)
                # print(f"P{self.node_id} received message: '{message}'")

    def run(self):
        threading.Thread(target=self.run_node).start()

# Read the network configuration file
def read_network_file(network_file):
    network = []
    with open(network_file, 'r') as file:
        for line in file:
            socket_info = line.strip().split()
            address, port = socket_info[1].split(":")
            network.append([address, int(port)])
    print(network)
    return network

# Create a node array for simulation
def create_nodes(network_file):
    network = read_network_file(network_file)
    nodes = [None] * len(network)
    for i in range(len(network)):
        nodes[i] = VectorClockNode(i, network)
    return nodes

# Simulating 3 nodes on different ports
if __name__ == "__main__":

    # Create node array
    nodes = create_nodes("node_addresses.txt")
    
    # Run each node
    for node in nodes:
        node.run()

    # Example 1 from slides (chapter6-time)
    # time.sleep(1)
    # nodes[0].local_event()
    # time.sleep(1)
    # nodes[2].local_event()
    # time.sleep(1)
    # nodes[0].send_message("", 1)
    # time.sleep(1)
    # nodes[2].local_event()
    # time.sleep(1)
    # nodes[1].send_message("", 2)
    # time.sleep(1)

    # Example 2 from slides (chapter6-time)
    nodes[1].send_message("", 0)
    time.sleep(1)
    nodes[2].local_event()
    time.sleep(1)
    nodes[2].local_event()
    time.sleep(1)
    nodes[0].send_message("", 2)
    time.sleep(1)
    nodes[2].send_message("", 1)
    time.sleep(1)
    nodes[2].send_multicast("")
    time.sleep(1)
