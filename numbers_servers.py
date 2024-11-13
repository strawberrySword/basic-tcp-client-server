#!/usr/bin/env python3

import socket
import select
import pandas as pd
from utils import *
import sys

FILE_PATH= "users_file"
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
        
            for s in inputready:
                client = None
                if s == self.server_socket:
                    client = self.accept_new_client()
                else:
                    client = [x for x in self.clients if x.socket == s].pop()       
                
                    is_msg_complete = recv_chunk(s, client)
                    
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
            for s in outputready:
                client = [x for x in self.clients if x.socket == s].pop()
                send_all(s, client.pending_output)
                self.write_sockets.remove(s)
        
    def load_users_from_file(self, file_path):
        self.users = pd.read_table(file_path, sep='\t', names=['username', 'password'])
    
    def accept_new_client(self):
        client_socket = self.server_socket.accept()
        self.read_sockets.append(client_socket)
        client = Client(client_socket)
        client.pending_output = "hey hey hey"
        self.clients.append(client)
        return client
    
    def client_login(self, user_name, password, client):
        if(self.users[self.users["username"] == user_name]["password"] == password):
            client.username = user_name
            client.pending_output = f"Hi {user_name}, good to see you."
        else: 
            client.pending_output = "Failed to login."
            
if __name__=="__main__":
    server = Server(HOST_NAME, PORT)
    
    server.load_users_from_file(FILE_PATH)
    
    server.run()
