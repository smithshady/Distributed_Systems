import math
from queue import PriorityQueue
from socket import *
import threading
import time

class VectorClock():
    def __init__(self, hostCount, hostIndex, hostInfo):
        self.clocks = [0] * hostCount
        self.hostIndex = hostIndex
        self.hostInfo = hostInfo
    
    # Increments the clock for this host by one and prints out new clock values
    def increment_clock(self):
        self.clocks[self.hostIndex] += 1

        printMessage = self.hostInfo[0] + ":("
        for clock in self.clocks:
            printMessage += str(clock) + ","
        printMessage = printMessage[0: len(printMessage) - 1] + ")"

        #print(printMessage)    TODO: Uncomment
    
    # Compares local clock values with other clock values, selects maximums, and prints out new clock values
    def update_clocks(self, otherClocks):
        for index, value in enumerate(otherClocks):
            self.clocks[index] = max(self.clocks[index], otherClocks[index])
    
    # A helper function for nicely formatting clock values when sending them to other processes
    def get_clocks(self):
        clockMessage = ""
        for clock in self.clocks:
            clockMessage += str(clock) + ","
        clockMessage = clockMessage[0: len(clockMessage) - 1]

        return clockMessage
        

class CDistributedMutex():
    def __init__(self):
        pass

    # Handles all incoming messages when running the processes with Maekawa's algorithm
    def receiveMessages(self):
        while (self.running == True):
            try:
                message, clientInfo = self.receivingSocket.recvfrom(3000)
                message = message.decode()

                # Split apart the message into three components: type, process information, and process vector clocks
                splitMessage = message.split("\n")
                requestorSplit = splitMessage[1].split(",")
                requestor = (float(requestorSplit[0]), int(requestorSplit[1]))

                # Don't change clock values when message comes from itself or is not a part of Maekawa's algorithm
                if ((requestor[1] != self.thisHost) and (splitMessage[0] != "EXIT")):
                    self.vector_clocks.update_clocks(list(map(int, splitMessage[2].split(","))))
                    self.vector_clocks.increment_clock()

                # Handle a REQUEST for CS according to Maekawa's algorithm
                if (splitMessage[0] == "REQUEST"):
                    self.requestQueue.put(requestor)
                    if ((self.committed == False) and (self.inCS == False)):
                        timeStamp = time.time() - self.startTime
                        returnMessage = "ACK\n" + str(timeStamp) + "," + str(self.thisHost) + "\n" + self.vector_clocks.get_clocks()
                        self.sendingSocket.sendto(returnMessage.encode(), self.hosts[requestor[1]])

                        self.committed = True
                
                # Handle an ACK for CS according to Maekawa's algorithm
                if (splitMessage[0] == "ACK"):
                    self.receivedACKs += 1
                
                # Handle a RELEASE for CS according to Maekawa's algorithm
                if (splitMessage[0] == "RELEASE"):
                    self.requestQueue.get()
                    self.committed = False
                    if (self.requestQueue.empty() == False):
                        timeStamp = time.time() - self.startTime
                        returnMessage = "ACK\n" + str(timeStamp) + "," + str(self.thisHost) + "\n" + self.vector_clocks.get_clocks()
                        tempElementCopy = self.requestQueue.get()
                        self.sendingSocket.sendto(returnMessage.encode(), self.hosts[tempElementCopy[1]])
                        self.requestQueue.put(tempElementCopy)
                        
                        self.committed = True
                
                # This is a special message type that alerts this process that another process is ready to finish up
                    # This is NOT a part of Maekawa's algorithm and simply ensures that no process "closes shop" too early
                if (splitMessage[0] == "EXIT"):
                    self.readyToExit[requestor[1]] = True
            
            # A timeout is necessary to cleanly exit this thread
                # If timeout and process is no longer running, exit thread
                # Else continue to listen on receiving socket
            except timeout:
                continue

            # This should never be reached!
            except Exception as e:
                print(e)
                break

    # This function sets up most of the necessary things needed for Maekawa's algorithm and the simulation of processes
    def GlobalInitialize(self, thisHost, hosts):
        # Keep track of connection information to all processes
        self.thisHost = thisHost
        self.hosts = hosts
        self.hostsLen = len(hosts)

        # Make local vector clocks and a starting timestamp
        self.vector_clocks = VectorClock(self.hostsLen, self.thisHost, self.hosts[self.thisHost])
        self.startTime = -1

        # Variables and data structures necessary for Maekawa's algorithm
        self.votingGroupHosts = []
        self.receivedACKs = 0
        self.inCS = False
        self.committed = False
        self.requestQueue = PriorityQueue()

        # This socket will spend all its time receiving messages from other processes
        self.receivingSocket = socket(AF_INET, SOCK_DGRAM)
        self.receivingSocket.bind(hosts[thisHost])

        # If this process is the last one we need, create a universal starting timestamp and send it to other processes
        # Else wait for the universal timestamp before beginning to run
        if (self.thisHost == self.hostsLen - 1):
            self.startTime = time.time()
            tempSocket = socket(AF_INET, SOCK_DGRAM)
            for host in self.hosts[0: len(self.hosts) - 1]:
                tempSocket.sendto(str(self.startTime).encode(), host)
        else:
            while(self.startTime == -1):
                message, clientInfo = self.receivingSocket.recvfrom(3000)
                message = message.decode()
                self.startTime = float(message)

        # Variables and data structures necessary to cleanly end the simulation
        self.running = True
        self.readyToExit = [False] * self.hostsLen

        # We need to listen for messages on the receiving port at all times, so create a seperate thread to handle this
        self.receivingSocket.settimeout(5)  # Without this timeout, the recvfrom blocks forever at the end, making the thread hang
        self.thread1 = threading.Thread(target = self.receiveMessages, args = ())
        self.thread1.start()
        
    # Perform the last of the clean up steps for this process
    def QuitAndCleanUp(self):
        self.running = False
        self.thread1.join()
        self.receivingSocket.close()

    # Create voting group subsets and make a socket for sending messages
    def MInitialize(self):
        if (self.thisHost == 0):
            self.votingGroupHosts = [0, 1, 2]
        if (self.thisHost == 1):
            self.votingGroupHosts = [1, 3, 5]
        if (self.thisHost == 2):
            self.votingGroupHosts = [2, 4, 5]
        if (self.thisHost == 3):
            self.votingGroupHosts = [0, 3, 4]
        if (self.thisHost == 4):
            self.votingGroupHosts = [1, 4, 6]
        if (self.thisHost == 5):
            self.votingGroupHosts = [0, 5, 6]
        if (self.thisHost == 6):
            self.votingGroupHosts = [2, 3, 6]

        # k = -1
        # cleanKValue = False
        # for i in range(1, self.hostsLen):
        #     if ((i * (i - 1) + 1) == self.hostsLen):
        #         k = i
        #         cleanKValue = True
        #         break

        #     if ((i * (i - 1) + 1) > self.hostsLen):
        #         break
        
        # if (k == -1):
        #     k = int(math.ceil(math.sqrt(self.hostsLen)))
        
        # if (cleanKValue == True):
        #     pass
        #     # Do simple method
        # else:
        #     pass
        #     # Do degenerative method

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
        
    # This process is now ready to enter CS, follow Maekawa's algorithm
    def MLockMutex(self):
        self.vector_clocks.increment_clock()
        timeStamp = time.time() - self.startTime
        for hostIndex in self.votingGroupHosts:
            message = "REQUEST\n" + str(timeStamp) + "," + str(self.thisHost) + "\n" + self.vector_clocks.get_clocks()
            self.sendingSocket.sendto(message.encode(), self.hosts[hostIndex])
        
        while (self.receivedACKs != len(self.votingGroupHosts)):
            continue
        
        self.inCS = True
        print("PROCESS %s ENTERED CS AT %s." % (self.thisHost, str(time.time() - self.startTime)))

    # This process is now ready to leave CS, follow Maekawa's algorithm
    def MReleaseMutex(self):
        self.vector_clocks.increment_clock()
        timeStamp = time.time() - self.startTime
        for hostIndex in self.votingGroupHosts:
            message = "RELEASE\n" + str(timeStamp) + "," + str(self.thisHost) + "\n" +self.vector_clocks.get_clocks()
            self.sendingSocket.sendto(message.encode(), self.hosts[hostIndex])
        
        self.receivedACKs = 0
        self.inCS = False
        print("PROCESS %s LEFT CS AT %s." % (self.thisHost, str(time.time() - self.startTime)))

    # Let other processes know this one is ready to terminate
        # Do NOT terminate process until all of them are done, otherwise the algorithm breaks!
    def MCleanup(self):
        for host in self.hosts:
            timeStamp = time.time() - self.startTime
            message = "EXIT\n" + str(timeStamp) + "," + str(self.thisHost) + "\n" + self.vector_clocks.get_clocks()
            self.sendingSocket.sendto(message.encode(), host)
        
        while (False in self.readyToExit):
            continue

        self.sendingSocket.close()
