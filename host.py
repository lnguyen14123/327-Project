import threading
import pygame
from player import Player
import socket
import pickle

HOST_IP = "0.0.0.0"  # listen on all interfaces
PORT = 9999
clients = {}  # {addr: (x, y)}


def server_thread():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST_IP, PORT))
    sock.setblocking(False)
    while True:
        try:
            data, addr = sock.recvfrom(1024)
            pos = pickle.loads(data)
            clients[addr] = pos
            # send other players back
            others = {a: p for a, p in clients.items() if a != addr}
            sock.sendto(pickle.dumps(others), addr)
        except BlockingIOError:
            continue


def run_host(screen):
    threading.Thread(target=server_thread, daemon=True).start()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

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
        data = pickle.dumps((player.position.x, player.position.y))
        sock.sendto(data, ("127.0.0.1", PORT))

        # Receive remote player positions
        try:
            while True:
                recv_data, addr = sock.recvfrom(1024)
                positions = pickle.loads(recv_data)
                for a, pos in positions.items():
                    if a not in remote_players:
                        remote_players[a] = Player("green", 40, 40)
                    remote_players[a].update_position(pygame.Vector2(pos[0], pos[1]))
        except BlockingIOError:
            pass

        # Draw
        screen.blit(bg_image, (0, 0))

        player.draw(screen)
        for p in remote_players.values():
            p.draw(screen)
        pygame.display.flip()
