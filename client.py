import socket, sys

def main():
    host, port = ("127.0.0.1", 1337)
    if len(sys.argv) > 1: #Host given
        host = sys.argv[1] 
    if len(sys.argv == 3): #Host and port given
        port = int(sys.argv[2])

    conn = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)

    conn.connect((host,port))

if __name__ == '__main__':
    main()