#!/usr/bin/env python3
import struct
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
Recieve and return all availible message from a given socket.
Our protocol enforces that messages end with the $STOP$ sequence.
Return value is a string representing the decoded availible message and a flag noting if the msg finished.
'''
def recv_chunk(sock, client):
    if(client.msg_len == 0): #new message 
        raw_msglen = recvall(sock, 4) # this is potentially blocking but only if int is passed through many packets which is unlikley
        if not raw_msglen:
            return None
        client.msg_len = struct.unpack('>I', raw_msglen)[0]
        client.remaining_msg = client.msg_len
    packet = sock.recv(client.remaining_msg)
    client.remaining_msg -= len(packet)
    client.message += packet.decode('utf-8')
    return client.remaining_msg == 0
    
    

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data
        
'''
Send a message (str) over a given socket
'''
def send_all(sock, message):
    msg = struct.pack(">I", len(message.encode('utf-8'))) + message.encode('utf-8')
    sock.sendall(msg) # temporary blocking solution
    
def execute_command(command):
    params = command.split(':')
    if len(params) == 1:
        return "Incorrect command format, has to include \":\""
    
    if params[0] == "calculate":
        return evaluate_exp(params[1].strip())
    elif params[0] == "max":
        if params[1].lstrip()[0] == '(' and params[1].rstrip()[-1] == ')':
            return f'the maximum is {max(params[1].strip()[1:-1].strip().split(' '))}'
        else:
            return f'max function has to include parameters with braces around them'
    elif params[0] == "factors":
        return f'the prime factors of {params[1].strip()} are: {",".join(prime_decomposition(int(params[1])))}'
    else:
        return f'Command {params[0]} does not exist'


'''
Evaluates an expression of the form X Y Z, where Y is an operator, X Z are signed ints
'''
def evaluate_exp(expression):
    def checkInt32(a):
        INT32_MIN = -2**31      # -2,147,483,648
        INT32_MAX = 2**31 - 1   #  2,147,483,647

        return INT32_MIN <= a and a <= INT32_MAX
     
    parts = expression.split(' ')
    if len(parts) != 3:
        return f'Incorrect format for calculate function'
    
    x = int(parts[0])
    z = int(parts[2])

    if parts[1] == '+':
        if not(checkInt32(x+z)): return f'error: result is too big'
        res = x+z
    elif parts[1] == '-':
        if not(checkInt32(x-z)): return f'error: result is too big'
        res = x-z
    elif parts[1] == '*':
        if not(checkInt32(x*z)): return f'error: result is too big'
        res = x*z
    elif parts[1] == '/':
        if not(checkInt32(x/z)): return f'error: result is too big'
        return f'response: {x/z:.2f}.'
    elif parts[1] == '^':
        if not(checkInt32(x**z)): return f'error: result is too big'
        res = x**z
    else:
        return f'Error: Operator {parts[1]} not supported'

    return f'response: {res}.'


'''
Returns all prime factors of a given number
'''
def prime_decomposition(x):
    return [str(i) for i in range(2, x+1) if x % i == 0 and all(i % j != 0 for j in range(2, i))]


class Client: 
    def __init__(self, socket):
        self.socket = socket
        self.message = ""
        self.pending_output = ""
        self.user_name = ""
        self.msg_len = 0
        self.remaining_msg = 0 