Shay Smith
CWID: 10876746

The library implementation of Maekawa's algorithm is in CDistributedMutex.py. An example program to run a process is in node.py
I first designed a VectorClockNode class that handles message sending and the vector clock functions. The vector clock works as described in lecture.
I then designed the CDistributedMutex class to inherit VectorClockNode, such that the functions in CDistributedMutex only need to handle Maekawa's algorithm.
My implementation of Maekawa's algorithm generally follows the outline given in the project description.
MLockMutex() calls are blocking, which is made possible by having a message handler thread running in the background.
It assumes that an application will never generate more than one request for a critical section at a time and will also not try to release a mutex that it has not previously requested.

The quorum creation algorithm is not implemented at this time. They must be hardcoded in CDistributedMutex.py, GlobalInitialize().

Note: quorums are created in MGlobalInitialize(), thus do not need to be passed into MInitialize().

How to run the provided example program:

- Review or update the network array in the node.py file with your desired network configuration
- Review or hardcode the associated quorums in CDistributedMutex.py, GlobalInitialize().
- Run each node/process (on separate machines or terminals) with: $ python node.py <node_id> <startup_delay>
- Set startup delay to an adequate time such that all the processes initialize before sending the first message