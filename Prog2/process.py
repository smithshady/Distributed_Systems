import random
import sys
import time
from DistributedLibrary import CDistributedMutex

hosts = []
networkFile = open("networkInfo.txt", "r")
for line in networkFile:
    hostInfo = line.strip().split(",")
    host = (hostInfo[0], int(hostInfo[1]))
    hosts.append(host)

mutex = CDistributedMutex()
mutex.GlobalInitialize(int(sys.argv[1]), hosts)
mutex.MInitialize()

time.sleep(int(sys.argv[2]))
for i in range(int(sys.argv[3])):
    time.sleep(random.randint(1, 15))

    mutex.MLockMutex()
    print("Process %d reached CS on loop %d." % (int(sys.argv[1]), i + 1))
    time.sleep(3)
    mutex.MReleaseMutex()

mutex.MCleanup()
mutex.QuitAndCleanUp()
