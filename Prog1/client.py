from socket import *
import sys

# Check for arguments
num_args = len(sys.argv) - 1
if (num_args != 4 and num_args != 5):
    print(f"Error: Gave {num_args} arguments, expected 4 or 5")
    print("Usage: python client.py <hostname/IP> <port> <'TCP'/'UDP'> <'send'/'receive'> <filename>")
    sys.exit(1)

# Set variables
serverName = sys.argv[1]
serverPort = int(sys.argv[2])
protocol = sys.argv[3]
mode = sys.argv[4]
req_msg = mode.encode()

# Read file if given 
if (mode == "send"):
    if (num_args == 5):
        filename = sys.argv[5]
        try:
            with open(filename, 'r') as file:
                filebytes = file.read().encode()
        except:
            print("Error: Could not find specified file")
            sys.exit(1)
    else:
        print("Error: No filename given")
        sys.exit(1)

# UDP
if (protocol == "UDP"):
    clientSocket = socket(AF_INET, SOCK_DGRAM)

    if (mode == "send"):
        clientSocket.sendto(filebytes,(serverName, serverPort))
        print(f"{filename} contents sent to {serverName}:{serverPort} over UDP")

    elif (mode == "receive"):
        clientSocket.sendto(req_msg,(serverName, serverPort))
        recv_msg, serverAddress = clientSocket.recvfrom(4000)
        recv_msg = recv_msg.decode()
        if (recv_msg == "no messages"):
            print("Error: No messages")
        else:
            print("Message received:")
            print(recv_msg)

    else:
        print("mode not correctly specified")
    clientSocket.close()

# TCP
elif (protocol == "TCP"):
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName,serverPort))

    if (mode == "send"):
        clientSocket.send(filebytes)
        print(f"{filename} contents sent to {serverName}:{serverPort} over TCP")

    elif (mode == "receive"):
        clientSocket.send(req_msg)
        recv_msg = clientSocket.recv(4000).decode()
        if (recv_msg == "no messages"):
            print("Error: No messages")
        else:
            print("Message received:")
            print(recv_msg)

    else:
        print("mode not correctly specified")
    clientSocket.close()

# Invalid protocol
else:
    print("protocol not correctly specified")
