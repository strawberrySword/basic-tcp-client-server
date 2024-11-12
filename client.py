import socket, sys
from utils import *

def main():
    host, port = ("127.0.0.1", 1337)
    if len(sys.argv) > 1: #Host given
        host = sys.argv[1] 
    if len(sys.argv == 3): #Host and port given
        port = sys.argv[2]

    conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    conn.connect((host,port))

    conn.recv(100) #Get welcome message

    user = input()[5:].strip()
    password = input()[9:].strip()
    conn.send(user+' '+password)


    if conn.recv(100).decode() == 'Failed to login.':
        print("Please retry logging in:")
        user = input()[5:].strip()
        password = input()[9:].strip()
        conn.send(user+' '+password)

    usr_in = input()
    while(usr_in != 'quit'):
        send_all(conn, usr_in)
        usr_in = input()


if __name__ == '__main__':
    main()