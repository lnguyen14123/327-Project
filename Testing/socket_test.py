import socket
import threading

UNAME = "USER_CLIENT"

def recieve_msg(sock):
    while (True):
        msg = sock.recv(1024).decode()

        # if msg len is 0, connection got closed
        if len(msg) == 0:
            sock.close()
            print("Peer closed connection. Please type exit.")
            break

        print(msg)

def send_msg(sock):
    while (True):
        msg = input()

        if msg == "exit":
            sock.close()
            print("You closed connection")
            break

        sock.send((UNAME+msg).encode())


WINDOWS_IP = "localhost"
LINUX_IP = "localhost"
PORT = 25565

s = socket.socket()

# CONNECT TO SERVER
s.connect((WINDOWS_IP, PORT))

recThread = threading.Thread(target=recieve_msg, args=(s,))
sendThread = threading.Thread(target=send_msg, args=(s,))

recThread.start()
sendThread.start()
recThread.join()
sendThread.join()
