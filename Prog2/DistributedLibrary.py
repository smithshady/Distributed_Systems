import math
from socket import *
import threading

class VectorClock():
    def __init__(self, hostCount, hostIndex, hostInfo):
        self.clocks = [0] * hostCount
        self.hostIndex = hostIndex
        self.hostInfo = hostInfo
    
    def increment_clock(self):
        self.clocks[self.hostIndex] += 1

        printMessage = self.hostInfo[0] + ":("
        for clock in self.clocks:
            printMessage += str(clock) + ","
        printMessage = printMessage[0: len(printMessage) - 1] + ")"

        print(printMessage)
    
    def update_clocks(self, otherClocks):
        for index, value in enumerate(otherClocks):
            self.clocks[index] = max(self.clocks[index], otherClocks[index])
    
    def get_clocks(self):
        clockMessage = ""
        for clock in self.clocks:
            clockMessage += str(clock) + ","
        clockMessage = clockMessage[0: len(clockMessage) - 1]

        return clockMessage
        

class CDistributedMutex():
    def __init__(self):
        pass

    def receiveMessages(self):
        while (self.running == True):
            try:
                message, clientInfo = self.receivingSocket.recvfrom(3000)
                splitMessage = message.split("\n")

                self.vector_clocks.update_clocks(list(map(int, splitMessage[2].split(","))))
                self.vector_clocks.increment_clock()

                if (splitMessage[0] == "REQUEST"):
                    print("REQUEST message sent from %s" % splitMessage[1])
                
                if (splitMessage[0] == "RELEASE"):
                    print("RELEASE message sent from %s" % splitMessage[1])
            except timeout:
                continue
            except:
                print("Something unexpected happened.")
                break



    def GlobalInitialize(self, thisHost, hosts):
        self.thisHost = thisHost
        self.hosts = hosts
        self.hostsLen = len(hosts)

        self.vector_clocks = VectorClock(self.hostsLen, self.thisHost, self.hosts[self.thisHost])

        self.receivingSocket = socket(AF_INET, SOCK_DGRAM)
        self.receivingSocket.bind(hosts[thisHost])
        self.receivingSocket.settimeout(5)

        self.running = True
        self.thread1 = threading.Thread(target = self.receiveMessages, args = ())
        self.thread1.start()
        

    def QuitAndCleanUp(self):
        self.running = False
        self.thread1.join()
        self.receivingSocket.close()

    def MInitialize(self):
        # self.votingGroupHosts = [0, 1, 2, 3, 4]

        k = -1
        cleanKValue = False
        for i in range(1, self.hostsLen):
            if ((i * (i - 1) + 1) == self.hostsLen):
                k = i
                cleanKValue = True
                break

            if ((i * (i - 1) + 1) > self.hostsLen):
                break
        
        if (k == -1):
            k = int(math.ceil(math.sqrt(self.hostsLen)))
        
        if (cleanKValue == True):
            pass
            # Do simple method
        else:
            pass
            # Do degenerative method

        # Use Sieve of Eratosthenes to calculate all primes up to N
        # primeChecker = [True] * (self.hostsLen + 1)
        # primes = []
        # p = 2
        # while (p * p <= self.hostsLen):
        #     if (primeChecker[p] == True):
        #         i = p * p
        #         while (i <= self.hostsLen):
        #             primeChecker[i] = False
        #             i += p
        #     p += 1
        
        # i = 2   # TODO: Reconsider having 1 as a "prime"
        # while (i <= self.hostsLen):
        #     if (primeChecker[i] == True):
        #         primes.append(i)
        #     i += 1
        
        # print(primes)

        # # Check if (k - 1) is a power of a prime
        # k = int(math.ceil(math.sqrt(self.hostsLen)))
        # print(k)
        # isPower = False
        # for p in primes:
        #     for i in range(1, self.hostsLen):
        #         num = int(math.pow(p, i))
        #         if (num == k - 1):
        #             isPower = True
        #             break
        #         elif (num > k - 1):
        #             break
        #     if (isPower == True):
        #         break
        
        # print(isPower)


        self.sendingSocket = socket(AF_INET, SOCK_DGRAM)
        

    def MLockMutex(self):
        self.vector_clocks.increment_clock()
        for hostIndex in self.votingGroupHosts:
            message = "REQUEST\n" + str(self.thisHost) + "\n" + self.vector_clocks.get_clocks()
            self.sendingSocket.sendto(message, self.hosts[hostIndex])

    def MReleaseMutex(self):
        self.vector_clocks.increment_clock()
        for hostIndex in self.votingGroupHosts:
            message = "RELEASE\n" + str(self.thisHost) + "\n" +self.vector_clocks.get_clocks()
            self.sendingSocket.sendto(message, self.hosts[hostIndex])

    def MCleanup(self):
        self.sendingSocket.close()
















# from socket import *
# import threading
# import time
# import math
# from enum import Enum

# from vector_clocks import VectorClockNode

# # Maekawa algorithm node 
# class MaekawaNode(VectorClockNode):

#     def __init__(self, node_id, nodes, set):
#         super().__init__(node_id, nodes)
#         self.set = set
#         self.request_queue = []  # Queue of requests
#         self.locked = False  # Lock status (in critical section or not)
#         self.voted_for = None  # Node this process has voted for
#         self.grant_count = 0
    
#     def MLockMutex(self):
#         self.send_multicast("REQUEST")

#     def MReleaseMutex(self):
#         if self.locked == True:
#             self.locked = False
#             self.send_multicast("RELEASE")
#             self.grant_count = 0
#         else:
#             print(f"P{self.node_id} cannot release a mutex it doesn't have")

#     # TODO: check timing?
#     def handle_request(self, node_id, received_vc):
#         if self.locked:
#             print(f"P{self.node_id} added P{node_id} to request queue because currently in CS")
#             self.request_queue.append(node_id)
#         elif self.voted_for != None:
#             print(f"P{self.node_id} added P{node_id} to request queue because vote is given to P{self.voted_for}")
#             self.request_queue.append(node_id)
#         else:
#             self.voted_for = node_id
#             self.send_message("GRANT", node_id)

#     def handle_grant(self):
#         self.grant_count += 1
#         if self.grant_count == len(self.set):
#             self.locked = True
#             print(f"P{self.node_id} enters the critical section.")

#     def handle_release(self):
#         if self.request_queue:
#             next_request = self.request_queue.pop(0)
#             self.voted_for = next_request
#             self.send_message("GRANT", next_request)
#         else:
#             self.voted_for = None

#     # Override multicast to only send messages to nodes in the set
#     def send_multicast(self, message):
#         for i in self.set:
#             if i != self.node_id:
#                 self.send_message(message, i)

#     # Overriding run_node method to handle Maekawa-specific messages
#     def run_node(self):
#         with socket(AF_INET, SOCK_DGRAM) as s:
#             s.bind(self.get_socket(self.node_id))
#             while True:
#                 data, addr = s.recvfrom(1024)
#                 node_id, message, received_vc = data.decode().split(';')
#                 received_vc = list(map(int, received_vc.strip('[]').split(',')))
#                 print(f"P{self.node_id} received message from P{node_id}: '{message}'")
#                 self.update_vector_clock(received_vc)

#                 # Process incoming messages
#                 if message == "REQUEST":
#                     self.handle_request(node_id, received_vc)
#                 elif message == "GRANT":
#                     self.handle_grant()
#                 elif message == "RELEASE":
#                     self.handle_release()

#     def run(self):
#         threading.Thread(target=self.run_node).start()