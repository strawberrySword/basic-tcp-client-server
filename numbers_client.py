#!/usr/bin/env python3

import socket, sys
import struct
from utils import *

def main():
    HOST, PORT = ("127.0.0.1", 1337)
    if len(sys.argv) > 1: #Host given
        HOST = sys.argv[1] 
    if len(sys.argv) == 3: #Host and port given
        PORT = int(sys.argv[2])

    conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    conn.connect((HOST,PORT))

    print(recvall(conn, struct.unpack('>I', recvall(conn,4))[0]).decode('utf-8')) #Get welcome message

    #Insert login credentials: login is assumed to be in the specified format. Otherwise, the sent credentials will be truncated
    user = input()[5:].strip()
    password = input()[9:].strip()
    send_all(conn ,user+' '+password)

    #Recieve login success/failure
    resp = recvall(conn, struct.unpack('>I', recvall(conn,4))[0]).decode('utf-8')
    print(resp)

    #Rety login
    while resp == 'Failed to login.':
        print("Please try logging in again:")
        user = input()[5:].strip()
        password = input()[9:].strip()
        send_all(conn, user+' '+password)

        resp = recvall(conn, struct.unpack('>I', recvall(conn,4))[0]).decode('utf-8')
        print(resp)

    #Send commands and get server's response
    usr_in = input()
    while(usr_in != 'quit'):
        send_all(conn, usr_in)
        print(recvall(conn, struct.unpack('>I', recvall(conn,4))[0]).decode('utf-8'))
        usr_in = input()

    conn.close()

if __name__ == '__main__':
    main()