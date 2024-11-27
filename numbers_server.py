#!/usr/bin/env python3

import socket
import select
import pandas as pd
from utils import *
import sys

FILE_PATH= ""
HOST_NAME = ""
PORT = 1337

def parse_login_info(message): 
    return message.split(" ")[0], message.split(" ")[1] 

class Server: 
    def __init__(self, host_name, port):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setblocking(0)
        self.server_socket.bind((host_name, port))
        self.server_socket.listen(5)
        self.clients = []
        self.read_sockets = [self.server_socket]
        self.write_sockets = []
    
    def run(self):
        running = True
        while running:
            try:
                inputready, outputready, _ = select.select(self.read_sockets, self.write_sockets, [])
            except select.error as e:
                self.server_socket.close()
            except socket.error as e:
                self.server_socket.close()
        
            for s in outputready:
                client = [x for x in self.clients if x.socket == s].pop()
                is_msg_complete = send_chunk(client)
                if is_msg_complete:
                    self.write_sockets.remove(s)
            for s in [s for s in inputready if s not in outputready]:
                client = None
                if s == self.server_socket:
                    client = self.accept_new_client()
                else:
                    client = [x for x in self.clients if x.socket == s].pop()       
                    is_msg_complete = recv_chunk(client)
                    
                    if not is_msg_complete:
                        continue
                    
                    if client.user_name == "":
                        user_name, password = parse_login_info(client.message)
                        self.client_login(user_name, password, client)
                    else: 
                        client.pending_output = execute_command(client.message)
                client.message = ""
                client.msg_len = 0
                client.remaining_msg = 0    
                self.write_sockets.append(client.socket)
        
    def load_users_from_file(self, file_path):
        self.users = pd.read_csv(file_path, sep='\t', names=['username', 'password'],dtype={
            'username': 'string',
            'password': 'string'
            })
    
    def accept_new_client(self):
        client_socket, _ = self.server_socket.accept()
        self.read_sockets.append(client_socket)
        client = Client(client_socket)
        client.pending_output = "Welcome! Please log in."
        self.clients.append(client)
        return client
    
    def client_login(self, user_name, password, client):
        if(user_name in self.users['username'].values and self.users.loc[self.users['username'] == user_name, 'password'].iloc[0] == password):
            client.user_name = user_name
            client.pending_output = "Hi {0}, good to see you.".format(user_name)
            print("Hi {0}, good to see you.".format(user_name))
        else: 
            client.pending_output = "Failed to login."
            print("Failed to login.")
            
if __name__=="__main__":
    FILE_PATH = sys.argv[1]

    if len(sys.argv) > 2: #Port given
        PORT = int(sys.argv[2])

    server = Server(HOST_NAME, PORT)
    
    server.load_users_from_file(FILE_PATH)
    
    server.run()