"""
ABOUT THE SOLUTION
------------------
1. The server supports an arbitrary amount of clients.
2. Chat is live i.e. you don't have to wait for a response from the server to send a message.
3. Messages are relayed to all connections i.e. it is a chat room.
4. I've repeated some code from the server file in client / vice versa.
   I thought it wouldn't make sense for someone to have to download the server to use the client etc.

ATTRIBUTION
-----------
All code is my own except:
1. The code used to erase user input from terminal to format it.
   Borrowed from: https://stackoverflow.com/a/43374104
2. The foundations of the SendThread class (most of the code to make it work was written by me).
   Borrowed from: https://stackoverflow.com/a/57387909
"""

# from the socket module import all
from socket import *
import threading

# Borrowed from: https://stackoverflow.com/a/43374104
erase = "\x1b[1A\x1b[2K"


# Foundations of this class were borrowed from: https://stackoverflow.com/a/57387909
# Most of the code to make the threading work was written by me.
class SendThread(threading.Thread):

    """
    Create a class SendThread that inherits threading.Thread.
    An instance of this class will be created on start for the server to listen to messages from the socket.
    """

    def __init__(self, callback, sock):
        # The callback is the function we want to run in a non-blocking manner.
        self._callback = callback
        # Call the threading.Thread constructor.
        super().__init__()
        # Once this class has been initialised, start the thread - which will call run.
        self.start()

    # Overrides run from the super class.
    # This is the activity of the function inside the thread.
    def run(self):

        # Continuously ask for user input.
        while True:
            self._callback(sock, input())


# Create a TCP server socket
# (AF_INET is used for IPv4 protocols)
# (SOCK_STREAM is used for TCP)
sock = socket(AF_INET, SOCK_STREAM)

# Get the host name of this machine.
host_name = gethostname()

# Get the ip_address associated with this host name.
ip_address = gethostbyname(host_name)

# set values for host - meaning this machine and port number 10000
# the machine address and port number have to be the same as the server is using.
server_address = (host_name, 10000)

# output to terminal some info on the address details
print('connecting to server at %s port %s' % server_address)
# Connect the socket to the host and port
sock.connect(server_address)

# This is the delimiter used to indicate the end of a message being sent over the socket.
# This in theory limits the messages users can send because any sequence of "|`END`|" will be removed.
# Unlikely to impact UX however as it is extremely unlikely that a user will need to send this exact sequence of characters.
delimiter = "|`END`|"

# Print a message explaining how to use the chat.
print("The chat is live. Just type and press enter to send a message.")


def send(sock, message):
    """
    Function to send a message to the server.
    """
    try:

        # Delete the input from the terminal and reprint it with "You: " prepended.abs(
        # LINE BELOW IS NOT MY CODE - see attribution.
        print(erase + "You: " + message)

        # Send data

        # Data is transmitted to the server with sendall()
        # encode() function returns bytes object
        sock.sendall((message + delimiter).encode())

    # If there is an exception then we should close the socket.
    except:
        print('closing socket')
        sock.close()
        return


# Spin up a thread for the client to send messages in a non-blocking manner.
SendThread(send, sock)

# Initialize the acknowledgement variable i.e. messages received from the server.
# Messages received from the server can be messages from other clients relayed by the server.
ack = ""

# Send the name of the client to the server.
sock.send(host_name.encode())

# We want the client to run all the time, so set up a forever true while loop.
while True:

    # Read data from the socket.
    data = sock.recv(16).decode()

    # If there's data then add it to the acknowledgement.
    if data:
        ack += data

    # If the delimiter is at the end of the acknowledgement, then run this code block.
    if ack[-7::] == delimiter:
        # Remove the delimiter from the acknowledgement.
        ack = ack.replace(delimiter, '')
        # The end of the message has been read, break out of the loop.
        # Print the message from the server.
        print(ack)
        ack = ""

# Close the socket.
sock.close()
