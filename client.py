#!/usr/bin/env python3

import socket, sys
import struct
from utils import *

def main():
    host, port = ("127.0.0.1", 1337)
    if len(sys.argv) > 1: #Host given
        host = sys.argv[1] 
    if len(sys.argv) == 3: #Host and port given
        port = int(sys.argv[2])

    conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    conn.connect((host,port))

    print(recvall(conn, struct.unpack('>I', recvall(conn,4))[0])) #Get welcome message
    user = input()[5:].strip()
    password = input()[9:].strip()
    send_all(conn ,user+' '+password)

    m = 'Failed to login.'
    resp = recvall(conn, struct.unpack('>I', recvall(conn,4))[0]).decode('utf-8')
    print(resp)

    while resp == m:
        print("Please try logging in again:")
        user = input()[5:].strip()
        password = input()[9:].strip()
        send_all(conn, user+' '+password)

        resp = recvall(conn, struct.unpack('>I', recvall(conn,4))[0]).decode('utf-8')
        print(resp)

    usr_in = input()
    while(usr_in != 'quit'):
        send_all(conn, usr_in)
        print(recvall(conn, struct.unpack('>I', recvall(conn,4))[0]).decode('utf-8'))
        usr_in = input()

    conn.close()

if __name__ == '__main__':
    main()