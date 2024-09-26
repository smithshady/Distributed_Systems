import sys
import random
import time

from CDistributedMutex import CDistributedMutex

# Usage: python node.py <node_id>
if len(sys.argv) != 2:
    print(f"Expected 1 arguments, but {len(sys.argv) - 1} were given.") 

# Configure network
network = [
    ("127.0.0.1", int(5111)),
    ("127.0.0.1", int(5112)),
    ("127.0.0.1", int(5113)),
]

# Initialize process
m = CDistributedMutex()
m.GlobalInitialize(int(sys.argv[1]), network)
m.MInitialize()
time.sleep(5) # allow time for all processes to be setup

# Enter the critical section 3x
for i in range(3):
    m.MLockMutex()
    print("Entering the critical section")
    time.sleep(3)
    m.MReleaseMutex()
    print("Left the critical section")

# Cleanup
m.MQuitAndCleanup()

