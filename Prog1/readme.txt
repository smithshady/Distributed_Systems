Shay Smith
CWID: 10876746

I have provided a python program for the client and server. The server should be run before any clients. Clients terminate immediately after sending and/or receiving a message from the server. The server does not terminate until killed.

The design for both programs is quite straightforward and the logic is the same for both TCP and UDP.
On a client send, file contents are converted to an encoded string before being sent to the server. The client program then closes the socket and is terminated. On a client receive, a request message is sent to the server, and then a response is received almost immediately with the first message from the server's queue. If the server's queue is empty, a message is sent to the client to notify there are no messages to receive.  

The client's input parameters and output format match the instructions.
The server has some additional debug information printed to the console.

To run the client:
python client.py <hostname/IP> <port> <'TCP'/'UDP'> <'send'/'receive'> <filename>

To run the sever:
python client.py <port> <'TCP'/'UDP'>
