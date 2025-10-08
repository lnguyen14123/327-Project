import socket
import threading

def recieve_msg(sock):
    while (True):
        msg = sock.recv(1024).decode()

        if len(msg) == 0:
            sock.close()
            print("Peer closed connection. Please type exit.")
            break

        print(msg)

def send_msg(sock):
    while(True):
        msg = input()

        if msg == "exit":
            sock.close()
            print("You closed connection")
            break

        sock.send(msg.encode())

WINDOWS_IP = "localhost"
LINUX_IP = "localhost"
PORT = 25565

s = socket.socket()

# SERVER SETUP
s.bind(('', PORT))
s.listen(1)
print("Listening on port " + str(PORT))

# SERVER ACCEPT CONNECTION
c, addr = s.accept()
print("CONNECTED TO " + str(addr))
c.send("IM WINDOWZ".encode())

recThread = threading.Thread(target=recieve_msg, args=(c,))
sendThread = threading.Thread(target=send_msg, args=(c,))

recThread.start()
sendThread.start()

recThread.join()
sendThread.join()
