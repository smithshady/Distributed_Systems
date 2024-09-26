from socket import *
import threading

class VectorClockNode:

    def __init__(self, node_id, network):
        self.node_id = int(node_id)
        self.network = network
        self.this_address = network[node_id][0]
        self.total_nodes = len(self.network)
        self.vc = [0] * self.total_nodes

    def increment_clock(self):
        self.vc[self.node_id] += 1
        print(f"{self.this_address} (P{self.node_id}): {self.vc}")

    def update_vector_clock(self, received_vc):
        for i in range(self.total_nodes):
            self.vc[i] = max(self.vc[i], received_vc[i])
        self.increment_clock()

    def send_message(self, message, node_id):
        # print(f"P{self.node_id} sending message to P{node_id}: '{message}'")
        self.increment_clock()
        message_vc = f"{self.node_id};{message};{self.vc}"
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.sendto(message_vc.encode(), self.network[int(node_id)])

    def send_multicast(self, message, nodes):
        for i in nodes:
            self.send_message(message, i)

class CDistributedMutex(VectorClockNode):

    def __init__(self):
        pass

    def GlobalInitialize(self, thisHost, network):
        super().__init__(thisHost, network)
        # start message handling thread
        self.thread = threading.Thread(target=self.run_message_handler).start()
        # create quorums | TODO: write algorithm
        self.quorums = [
            [0,1],
            [1,2],
            [2,0]
        ]
        self.quorum = self.quorums[self.node_id] # TODO: do I need to pass this into MInitialize? 

    def MInitialize(self):
        self.request_queue = []
        self.locked = False
        self.voted_for = None
        self.grant_count = 0
        self.lock_event = threading.Event()

    def MCleanup(self):
        pass # TODO: should I wait to ensure that this node quitting doesn't deadlock the other processes?

    def MQuitAndCleanup(self):
        self.MCleanup()
        self.send_message("QUIT", int(self.node_id))
    
    def MLockMutex(self):
        self.lock_event.clear()
        self.send_multicast("REQUEST", self.quorum)
        self.lock_event.wait()

    def MReleaseMutex(self):
        if self.locked == True:
            self.locked = False
            self.grant_count = 0
            self.send_multicast("RELEASE", self.quorum)
        else:
            print(f"ERROR: cannot release a mutex it doesn't have")

    def handle_request(self, node_id, received_vc):
        if self.locked:
            # print(f"Added P{node_id} to request queue because currently in CS")
            self.request_queue.append(node_id)
        elif self.voted_for != None:
            # print(f"Added P{node_id} to request queue because vote is given to P{self.voted_for}")
            self.request_queue.append(node_id)
        else:
            self.voted_for = node_id
            self.send_message("GRANT", node_id)

    def handle_grant(self):
        self.grant_count += 1
        # print(f"Received {self.grant_count}/{len(self.quorum)} grants")
        if self.grant_count == len(self.quorum):
            self.locked = True
            self.lock_event.set() 

    def handle_release(self):
        if self.request_queue:
            next_request = self.request_queue.pop(0)
            self.voted_for = next_request
            # print(f"Voting for P{next_request}")
            self.send_message("GRANT", int(next_request))
        else:
            # print(f"Nobody to vote for, vote is free")
            self.voted_for = None

    def run_message_handler(self):
        print("Process initialized, ready to receive messages...")
        with socket(AF_INET, SOCK_DGRAM) as s:
            s.bind(self.network[self.node_id])
            while True:
                data, addr = s.recvfrom(1024)
                node_id, message, received_vc = data.decode().split(';')
                received_vc = list(map(int, received_vc.strip('[]').split(',')))
                # print(f"P{self.node_id} received message from P{node_id}: '{message}'")
                self.update_vector_clock(received_vc)
                # Process incoming messages
                if message == "REQUEST":
                    self.handle_request(int(node_id), received_vc)
                elif message == "GRANT":
                    self.handle_grant()
                elif message == "RELEASE":
                    self.handle_release()
                elif message == "QUIT":
                    break
        # Quit
        if self.thread is not None:
            self.thread.join()
        print(f"Process cleaned up.")