import socket
import select
import pandas as pd
from utils.py import recv_all, send_all, Client

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
    server_sock.bind((HOST_NAME, PORT))
    server_sock.listen(5)

    clients = []
    inputs = [server_sock]
    outputs = []

    running = True
    while running:
        try:
            inputready,outputready,exceptready = select.select(inputs, outputs, [])
        except select.error as e:
            break
        except socket.error as e:
            break
        for s in inputready:
            if s == server_sock:
                client_socket = s.accept()
                inputs.append(client_socket)
                clients.append(Client(client_socket))
            else:
                message = recv_all(s)
                client = [x for x in clients if x.socket == s].pop()
                if(client.user_name == ""):
                    user_name, password = parse_login_info(message)
                    if(users[users["username"] == user_name]["password"] == password):
                        client.pending_output = f"Hi {user_name}, good to see you."
                    else: 
                        client.pending_output = "Failed to login."
                else: 
                    #parse command
                    client.pending_output = "place holder"
                outputs.append(s)
        for s in outputready:
            client = [x for x in clients if x.socket == s].pop()
            send_all(s, client.pending_output)


    