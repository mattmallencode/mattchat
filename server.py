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

# Import datetime for logging
from datetime import datetime

# Import threading
import threading

# Borrowed from: https://stackoverflow.com/a/43374104
erase = "\x1b[1A\x1b[2K"

# Create a TCP server socket
# (AF_INET is used for IPv4 protocols)
# (SOCK_STREAM is used for TCP)
sock = socket(AF_INET, SOCK_STREAM)

# Delete this after testing
sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

# if we did not import everything from socket, then we would have to write the previous line as:
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Get the host name of this machine.
host_name = gethostname()

# Get the ip_address associated with this host name.
ip_address = gethostbyname(host_name)

# set values for host 'localhost' - meaning this machine and port number 10000
server_address = (ip_address, 10000)

# output to terminal some info on the address details
print(f"Server domain name: {host_name}")
print(f"Server ip address: {ip_address}")
print('*** Server is starting up on %s port %s ***' % server_address)

# Bind the socket to the host and port
sock.bind(server_address)

# This is the delimiter used to indicate the end of a message being sent over the socket.
# This in theory limits the messages users can send because any sequence of "|`END`|" will be removed.
# Unlikely to impact UX however as it is extremely unlikely that a user will need to send this exact sequence of characters.
delimiter = "|`END`|"


# Array holding all of the currently connected clients.
connections = []


# Foundations of this class were borrowed from: https://stackoverflow.com/a/57387909
# Most of the code to make the threading work was written by me.
class SendThread(threading.Thread):

    """
    Create a class SendThread that inherits threading.Thread.
    An instance of this class will be created on start for the server to listen to messages from the socket.
    """

    def __init__(self, callback):
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
            # By default the sender is None and the client_name is "Server".
            self._callback(input(), None, "Server")


def send(message, sender, client_name):
    """
    Function to relay a message to all clients.
    "sender" is the address of the author of the message.
    "client_name" is the domain name of the author of the message.
    """
    try:

        # If this message was sent by the server then send this code block.
        if sender == None or client_name == "Server":

            # Delete the input from the terminal and reprint it with "You: " prepended.abs(
            # LINE BELOW IS NOT MY CODE - see attribution.
            print(erase + "You: " + message)

            # Open a connection to the log file in append mode.
            log = open("log.txt", "a")

            # Set the time_received equal to the current date and time.
            time_received = datetime.now()

            # Write the message and the time received to the log.
            log.write(
                f"{client_name}: {message} [{time_received}]\n")

            # Save the changes to the file.
            log.flush()

            # Close the connection to the log file.
            log.close()

        # For all the clients connected to the server.
        for connection in connections:
            # If this client is not the author of the message, run this code block.
            if connection != sender:
                # Send the message to the client with the author prepended to it and the delimiter appended.
                connection.sendall(
                    (client_name + ": " + message + delimiter).encode())

    # If there was an exception then we should just return from the send function.
    except:
        return


def new_client(connection, client_address, client_name):
    """
    Function that is run in a seperate thread for each client.
    Handles receiving messages from the client, logging them and relaying them to the rest of the chat room.
    """

    # Print to the terminal the details of the connection.
    print('connection from', client_address)

    # Run this continuously while the client is connected.
    while True:
        try:
            # Open a connection to the log text file in append mode.
            log = open("log.txt", "a")

            # Receive the data in small chunks and retransmit it
            while True:

                # Initialize the message variable.s
                message = ""

                # decode() function returns string object
                data = connection.recv(16).decode()

                # If there is data run this code block.
                if data:

                    # Add the data to the message.
                    message += data

                # If the delimiter is at the end of the message, run this code block.
                if message[-7:] == delimiter:

                    # Call the send function to relay the message to the rest of the chat room.
                    send(message, connection, client_name)

                    # Remove the delimiter from the message.
                    message = message.replace(delimiter, '')

                    # Print the message to the server's terminal.
                    print(f"{client_name}: {message}")

                    # Set the time_received equal to the current date and time.
                    time_received = datetime.now()

                    # Write the message and the time received to the log.
                    log.write(
                        f"{client_name}: {message} [{time_received}]\n")

                    # Save the changes to the file.
                    log.flush()

        # If there's an exception run this code block.
        except:

            # Close the connection to the log file.
            log.close()

            # Remove the connection from the connections array.
            connections.remove(connection)

            # Clean up the connection.
            connection.close()

            # Break out of the while loop.
            break

    # If we've broken out of the while loop we should return from the function which will close the thread.
    return


# Print a message explaining how to use the chat.

print("The chat is live. Just type and press enter to send a message.")

# Spin up a thread for the server to send messages in a non-blocking manner.
SendThread(send)

# We want the server to run all the time, so set up a forever true while loop.

while True:

    # Listen for connections on the socket.
    sock.listen(1)

    # accept() returns an open connection between the server and client, along with the address of the client
    connection, client_address = sock.accept()

    # Add the connection to the connections list.
    connections.append(connection)

    # Read the name of the client from the socket.
    client_name = connection.recv(1080).decode()

    # Create a new thread for the new client.
    threading.Thread(target=new_client, args=(
        connection, client_address, client_name)).start()

# now close the socket
sock.close()
