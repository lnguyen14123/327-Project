import pygame
from player import Player
from chat_pubsub import *
import socket
import pickle
import Pyro5.api
import threading

HOST_IP = "127.0.0.1"  # change this to host IP if on different machine
PORT = 9999

# maybe the worst way to do this
def sub_thread(daemon: Pyro5.api.Daemon):
    daemon.requestLoop()

def pub_thread(pub: Publisher):
    while True:
        msg = input()
        pub.publish(msg)
    


def run_client(screen):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    # pubsub setup
    # TODO: this and the threads could probably go in a seperate class
    chat_pub = Publisher()
    chat_sub = Subscriber()
    chat_daemon = Pyro5.api.Daemon()
    chat_uri = chat_daemon.register(chat_sub)

    # another 2 threads yippee!!!
    threading.Thread(target=sub_thread, daemon=True, args=(chat_daemon,)).start()
    threading.Thread(target=pub_thread, daemon=True, args=(chat_pub,)).start()




    player = Player("green", 40, 40)
    player.update_position(pygame.Vector2(
        screen.get_width() / 2, screen.get_height() / 2))
    remote_players = {}
    bg = pygame.Surface(screen.get_size())
    bg.fill((50, 50, 50))
    bg_image = pygame.image.load("Assets/win7_bg.jpg")

    clock = pygame.time.Clock()
    running = True

    while running:
        dt = clock.tick(60) / 1000

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update local player
        player.update(screen, dt)

        # Send position to host
        # also sends chat subscriber uri now
        # definitely the worst way to do this! This should be sent upon connection
        data = pickle.dumps((player.position.x, player.position.y, chat_uri))
        sock.sendto(data, (HOST_IP, PORT))

        # Receive other player positions
        try:
            while True:
                recv_data, addr = sock.recvfrom(1024)
                positions = pickle.loads(recv_data)
                for a, pos in positions.items():
                    if a not in remote_players:
                        remote_players[a] = Player("purple", 40, 40)
                        # register subscriber
                        chat_pub.register(Pyro5.api.Proxy(pos[2]))
                    remote_players[a].update_position(pygame.Vector2(pos[0], pos[1]))
                    # detect collision
                    if remote_players[a].rect.colliderect(player.rect):
                        print(f"You colliding with player {a}")
        except BlockingIOError:
            pass

        # Draw everything
        screen.blit(bg_image, (0, 0))

        player.draw(screen)
        for p in remote_players.values():
            p.draw(screen)
        pygame.display.flip()
