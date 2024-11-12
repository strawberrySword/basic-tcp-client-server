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
    

'''
Gets a string that represents a command call (ex: "calculate: 2*5")
'''
def execute_command(command):
    params = command.split(':')

    if params[0] == "calculate":
        return evaluate_exp(params[1].lstrip().rstrip())
    elif params[0] == "max":
        return f'the maximum is {max(params[1].lstrip().rstrip().split(' '))}'
    elif params[0] == "factors":
        return f'the prime factors of {params[1]} are: {[i for i in range(1, int(params[1])+1) if int(params[1]) % i == 0].join(' ')}'
    else:
        return


'''
Evaluates an expression of the form X Y Z, where Y is an operator, X Z are signed ints
'''
def evaluate_exp(expression):
    parts = expression.split(' ')
    x = int(parts[0])
    z = int(parts[2])

    if parts[1] == '+':
        res = str(x+z)
    elif parts[1] == '-':
        res = str(x-z)
    elif parts[1] == '*':
        res = str(x*z)
    elif parts[1] == '/':
        res = str(x/z)
    elif parts[1] == '^':
        res = str(x**z)

    return f'response: {res}.'


class Client: 
    def __init__(self, socket):
        self.socket = socket
        self.message = ""
        self.pending_output = ""
        self.user_name = ""