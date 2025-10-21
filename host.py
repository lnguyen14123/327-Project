import threading
import pygame
from player import Player
import socket
import pickle
import Pyro5.api
from chat_pubsub import *

# more detailed comments in client.py

# binding to the 0.0.0.0 IP address means the program can accept connections
# from itself (localhost), as well as other computers on the local network
# this makes it easy to test on both fronts
HOST_IP = "0.0.0.0"  # listen on all interfaces
OWN_IP = socket.gethostbyname(socket.gethostname()) # the local ip of this computer
PORT = 9999
CHAT_PORT = 9998
clients = {}  # {addr: (x, y)}

def sub_thread(daemon: Pyro5.api.Daemon):
    daemon.requestLoop()

def pub_thread(pub: Publisher):
    while True:
        # input blocks this thread from finishing until an input occurs
        # this will be fixed when chat is added in-game instead of the terminal
        msg = input()
        pub.publish(msg)

def server_thread(stop_event: threading.Event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST_IP, PORT))
    sock.setblocking(False)
    server_running = True
    while server_running:
        try:
            # stop the thread if the program exits
            if stop_event.is_set():
                server_running = False

            data, addr = sock.recvfrom(1024)
            pos = pickle.loads(data)
            clients[addr] = pos
            # send other players back
            others = {a: p for a, p in clients.items() if a != addr}
            sock.sendto(pickle.dumps(others), addr) 
                
        except BlockingIOError:
            continue

    sock.close()


def run_host(screen):

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)
    # pubsub setup
    # TODO: this and the threads could probably go in a seperate class
    chat_pub = Publisher(HOST_IP, PORT)
    chat_sub = Subscriber()
    chat_daemon = Pyro5.api.Daemon(host=OWN_IP)
    chat_uri = chat_daemon.register(chat_sub)

    # another 2 threads yippee!!!
    threading.Thread(target=sub_thread, daemon=True, args=(chat_daemon,)).start()
    threading.Thread(target=pub_thread, daemon=True, args=(chat_pub,)).start()

    stop_event = threading.Event()
    threading.Thread(target=server_thread, args=(stop_event,)).start()

    player = Player("purple", 40, 40)
    player.update_position(pygame.Vector2(
        screen.get_width()/2, screen.get_height()/2)) 
    remote_players = {}
    bg = pygame.Surface(screen.get_size())
    bg.fill((50, 50, 50))
    bg_image = pygame.image.load("Assets/win7_bg.jpg")

    clock = pygame.time.Clock()
    running = True
    while running:
        dt = clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update local player
        player.update(screen, dt)

        # Send position to self (server)
        data = pickle.dumps((player.position.x, player.position.y, chat_uri))
        sock.sendto(data, ("127.0.0.1", PORT))

        # Receive remote player positions
        try:
            while True:
                recv_data, addr = sock.recvfrom(1024)
                positions = pickle.loads(recv_data)
                for a, pos in positions.items():
                    if a not in remote_players:
                        remote_players[a] = Player("green", 40, 40)
                        # register subscriber
                        chat_pub.register(Pyro5.api.Proxy(pos[2]), a)
                    remote_players[a].update_position(pygame.Vector2(pos[0], pos[1]))
                    # detect collision
                    if remote_players[a].rect.colliderect(player.rect):
                        chat_pub.collide(a)
        except BlockingIOError:
            pass

        # Draw
        screen.blit(bg_image, (0, 0))

        player.draw(screen)
        for p in remote_players.values():
            p.draw(screen)
        pygame.display.flip()

    # all the stuff that needs to happen after the game closes
    chat_daemon.shutdown()
    stop_event.set()
    