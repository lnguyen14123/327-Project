import pygame
from player import Player
import socket
import pickle

HOST_IP = "127.0.0.1"  # change this to host IP if on different machine
PORT = 9999


def run_client(screen):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    player = Player("green", 40, 40)
    player.position = pygame.Vector2(
        screen.get_width() / 2, screen.get_height() / 2)
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
        data = pickle.dumps((player.position.x, player.position.y))
        sock.sendto(data, (HOST_IP, PORT))

        # Receive other player positions
        try:
            while True:
                recv_data, addr = sock.recvfrom(1024)
                positions = pickle.loads(recv_data)
                for a, pos in positions.items():
                    if a not in remote_players:
                        remote_players[a] = Player("purple", 40, 40)
                    remote_players[a].position = pygame.Vector2(pos[0], pos[1])
        except BlockingIOError:
            pass

        # Draw everything
        screen.blit(bg_image, (0, 0))

        player.draw(screen)
        for p in remote_players.values():
            p.draw(screen)
        pygame.display.flip()
