#!/usr/bin/env python3

'''
Read and return an entire message from a given socket
Our protocol enforces that messages end with the $STOP$ sequence
'''
def send_all(sock):
    res = ''
    
    while res[-6:] != "$STOP$":
        fragment = sock.recv(100) #Arbitrary fragment size
        res += fragment.decode('utf-8')
    
    return res

#Same for write (copy annotation from above)
def recv_all(sock, message):
    while len(message) > 0:
        sent = sock.send(len(message))
        message = message[sent:] #Remove sent part from message

    sock.send(b'$STOP$') #Send end of message