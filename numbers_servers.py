import socket
import select
import panda as pd

FILE_PATH= "users_file"
HOST_NAME = ""
PORT = "1337"

def load_users_from_file(file_path):
    return pd.read_csv(FILE_PATH, sep='\t', header=None, names=['username', 'password'])

if __name__=="__main__":
    users = load_users_from_file(FILE_PATH)
    print(users)
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST_NAME, PORT))
    server_sock.listen(5)

    inputs = [server_sock]

    queued_clients = []
    pending_welcome = []
    pending_reject = []
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
                client = s.accept()
                inputs.append(client)
            else:
                # read login detalis
                # check if user legit
                # if legit add s to pending welcome
                # else add the s to pending reject
                outputs.append(s)
        for s in outputready:
            if s in pending_reject:
                #send reject message
                pending_reject.remove(s)
            elif s in pending_welcome:
                #send welcome message
                pending_welcome.remove(s)


    