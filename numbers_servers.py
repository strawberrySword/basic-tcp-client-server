import socket
import select
import pandas as pd
from utils import *
import sys

FILE_PATH= "users_file"
HOST_NAME = ""
PORT = 1337

def load_users_from_file(file_path):
    return pd.read_table(FILE_PATH, sep='\t', names=['username', 'password'])

def parse_login_info(message): 
    return message.split(" ")[0], message.split(" ")[1] 

if __name__=="__main__":
    users = load_users_from_file(FILE_PATH)
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setblocking(0)
    server_sock.bind((HOST_NAME, PORT))
    server_sock.listen(5)

    clients = []
    read_sockets = [server_sock]
    write_sockets = []

    running = True
    while running:
        try:
            inputready,outputready,exceptready = select.select(read_sockets, write_sockets, [])
        except select.error as e:
            break
        except socket.error as e:
            break
        for s in inputready:
            if s == server_sock:
                client_socket = s.accept()
                read_sockets.append(client_socket)
                clients.append(Client(client_socket))
            else:
                client = [x for x in clients if x.socket == s].pop()       
            
                message_chunk = s.recv(10000) #Arbitrary fragment size
                client.message += message_chunk.decode('utf-8')
                if(client.message[:-6] != "$STOP$"):
                    continue
                result = ""
                
                if(client.user_name == ""):
                    user_name, password = parse_login_info(client.message)
                    if(users[users["username"] == user_name]["password"] == password):
                        client.username = user_name
                        result = f"Hi {user_name}, good to see you."
                    else: 
                        result = "Failed to login."
                else: 
                    result = execute_command(client.message)    
                client.pending_output = result
                write_sockets.append(s)
        for s in outputready:
            client = [x for x in clients if x.socket == s].pop()
            send_all(s, client.pending_output)
            write_sockets.remove(s)