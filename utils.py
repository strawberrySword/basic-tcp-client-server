#!/usr/bin/env python3

'''
Recieve and return an entire message from a given socket.
Our protocol enforces that messages end with the $STOP$ sequence.
Return value is a string representing the decoded.
'''
def recv_all(sock):
    res = ''
    
    while res[-6:] != "$STOP$":
        fragment = sock.recv(100) #Arbitrary fragment size
        res += fragment.decode('utf-8')
    
    return res

'''
Send a message (str) over a given socket
'''
def send_all(sock, message):
    while len(message) > 0:
        sent = sock.send(message.encode())
        message = message[sent:] #Remove sent part from message

    sock.send(b'$STOP$') #Send end of message
    
class Client: 
    def __init__(self, socket):
        self.socket = socket
        self.last_received = ""
        self.pending_output = ""
        self.user_name = ""