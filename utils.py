#!/usr/bin/env python3
import struct

#A server-side function, recieves a fragment from a read-ready socket
def recv_chunk(client):
    if(client.msg_len == 0): #new message 
        raw_msglen = recvall(client.socket, 4) # this is potentially blocking but only if int is passed through many packets which is unlikley
        if not raw_msglen:
            return None
        client.msg_len = struct.unpack('>I', raw_msglen)[0]
        client.remaining_msg = client.msg_len
    packet = client.socket.recv(client.remaining_msg)
    client.remaining_msg -= len(packet)
    client.message += packet.decode('utf-8')
    return client.remaining_msg == 0
    
#A server-side function, sends a fragment to a write ready socket
def send_chunk(client):
    if client.amount_sent == 0:
        client.socket.sendall(struct.pack(">I", len(client.pending_output.encode('utf-8'))))
        client.amount_sent += 1
    sent = client.socket.send(client.pending_output[client.amount_sent-1:].encode('utf-8'))
    client.amount_sent += sent
    ret =  (client.amount_sent == len(client.pending_output.encode())+1)
    if ret:
        client.amount_sent = 0
        client.pending_output = ""

    return ret
    
    
    
#Client-side function, blocking recieve until recieved n bytes
#Returns None on error
def recvall(sock, n):
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data

#Cliend-side function, blocking send until whole message is sent.
#Note the use of our application protocol: message length at start
def sendall(sock, message):
    msg = struct.pack(">I", len(message.encode('utf-8'))) + message.encode('utf-8')

    sent = 0
    while sent < len(msg):
        packet = sock.send(msg[sent:])
        if(packet == 0):
            return None
        sent += packet



#Server-side command execution
def execute_command(command):
    params = command.split(':')
    if len(params) == 1:
        return "Incorrect command format, has to include \":\""
    
    if params[0] == "calculate":
        return evaluate_exp(params[1].strip())
    elif params[0] == "max":
        if params[1].lstrip()[0] == '(' and params[1].rstrip()[-1] == ')':
            return 'the maximum is {0}'.format(max(list(map(int, params[1].strip()[1:-1].strip().split(' ')))))
        else:
            return 'max function has to include parameters with braces around them'
    elif params[0] == "factors":
        return 'the prime factors of {0} are: {1}'.format(params[1].strip(), ",".join(prime_decomposition(int(params[1]))))
    else:
        return 'Command {0} does not exist'.format(params[0])

#Helper for execute_command(...)
def evaluate_exp(expression):
    def checkInt32(a):
        INT32_MIN = -2**31      # -2,147,483,648
        INT32_MAX = 2**31 - 1   #  2,147,483,647

        return INT32_MIN <= a and a <= INT32_MAX
     
    parts = expression.split(' ')
    if len(parts) != 3:
        return 'Incorrect format for calculate function'
    
    x = int(parts[0])
    z = int(parts[2])

    if parts[1] == '+':
        if not(checkInt32(x+z)): return 'error: result is too big'
        res = x+z
    elif parts[1] == '-':
        if not(checkInt32(x-z)): return 'error: result is too big'
        res = x-z
    elif parts[1] == '*':
        if not(checkInt32(x*z)): return 'error: result is too big'
        res = x*z
    elif parts[1] == '/':
        if not(checkInt32(x/z)): return 'error: result is too big'
        return 'response: {0:.2f}.'.format(x/z)
    elif parts[1] == '^':
        if not(checkInt32(x**z)): return 'error: result is too big'
        res = x**z
    else:
        return 'Error: Operator {0} not supported'.format(parts[1])

    return 'response: {0}.'.format(res)

#Helper for execute_command(...)
def prime_decomposition(x):
    return [str(i) for i in range(2, x+1) if x % i == 0 and all(i % j != 0 for j in range(2, i))]



#Server-side representation of a client
class Client: 
    def __init__(self, socket):
        self.socket = socket
        self.user_name = ""
        self.message = "" #Message recieved from client
        self.msg_len = 0 #Length is recieved before message and should be stored to ensure we get the entire message
        self.pending_output = "" #Message to be sent to client

        #Keeping track of sent/recieved fragments
        self.remaining_msg = 0 
        self.amount_sent = 0