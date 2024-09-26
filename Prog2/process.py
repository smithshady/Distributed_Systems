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

for i in range(int(sys.argv[2])):
    time.sleep(random.randint(1, 15))

    mutex.MLockMutex()
    time.sleep(3)
    mutex.MReleaseMutex()

print("Process %s finished %s CS loops." % (sys.argv[1], sys.argv[2]))

mutex.MCleanup()
mutex.QuitAndCleanUp()
