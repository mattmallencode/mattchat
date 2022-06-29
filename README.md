# MattChat

Chat room (client and server) written in Python using the socket and threading module.

# About this project:

* The server supports an arbitrary amount of clients.
* Chat is live i.e. you don't have to wait for a response from the server to send a message.
* Messages are relayed to all connections i.e. it is a chat room.
* I've repeated some code from the server file in client / vice versa - wouldn't make sense for someone to have to download the server to use the client.

# Attribution:

All code is my own except:
* The code used to erase user input from terminal to format it. Borrowed from: https://stackoverflow.com/a/43374104
* The foundations of the SendThread class (most of the code to make it work was written by me). Borrowed from: https://stackoverflow.com/a/57387909
