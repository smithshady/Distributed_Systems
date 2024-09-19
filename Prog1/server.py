from socket import *
from collections import deque
import sys

# Check for arguments
num_args = len(sys.argv) - 1
if (num_args != 2):
    print(f"Gave {num_args} arguments, expected 2")
    print("Usage: python client.py <port> <'TCP'/'UDP'>")
    sys.exit(1)

# Set variables
serverPort = int(sys.argv[1])
protocol = sys.argv[2]
queue = deque()
err_msg = "no messages".encode()

# UDP
if (protocol == "UDP"):
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind(('', serverPort))
    print("The UDP server is ready to receive")

    while 1:
        message, clientAddress = serverSocket.recvfrom(4000)
        if (message.decode() == "receive"):

            if (len(queue) == 0):
                serverSocket.sendto(err_msg, clientAddress)
                print("No elements in queue, sending error message")

            else:
                send_msg = queue.popleft()
                serverSocket.sendto(send_msg, clientAddress)
                print("Sent message to client")
        else:
            queue.append(message)
            print("Added message to queue")

# TCP
elif (protocol == "TCP"):
    serverSocket = socket(AF_INET,SOCK_STREAM)
    serverSocket.bind(('',serverPort))
    serverSocket.listen(1) # does this need to go in the while loop?
    print("The TCP server is ready to receive") 

    while 1:
        connectionSocket, clientAddress = serverSocket.accept()
        message = connectionSocket.recv(4000)
        if (message.decode() == "receive"):

            if (len(queue) == 0):
                connectionSocket.send(err_msg)
                print("No elements in queue, sending error message")

            else:
                send_msg = queue.popleft()
                connectionSocket.send(send_msg)
                print("Sent message to client")
        else:
            queue.append(message)
            print("Added message to queue")

# Invalid protocol
else:
    print("protocol not correctly specified")
