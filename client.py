import pygame
from player import Player
from chat_pubsub import *
import socket
import pickle
import Pyro5.api
import threading

"""

"""

HOST_IP = "10.119.155.246"  # change this to host IP if on different machine
OWN_IP = socket.gethostbyname(socket.gethostname()) # the local ip of this computer
PORT = 9999
CHAT_PORT = 9998

# maybe the worst way to do this
# it feels like there would be a better way than to spin up 2 threads just for the chat
# these *are* software threads though. 
# I feel like asyncio coroutines would work for this, since from what I've briefly read they might be more lightweight than threads
# but I couldn't figure out how to run them looped in the background properly, we're already using threads, and these are extremely lightweight functions anyway.
def sub_thread(daemon: Pyro5.api.Daemon):
    daemon.requestLoop()

def pub_thread(pub: Publisher):
    while True:
        msg = input()
        pub.publish(msg)

def run_client(screen):
    # AF_INET means the socket will use IPv4
    # IPv6 is also used, so this is an important distinction
    # SOCK_DGRAM (basically) assigns the port to use UDP
    # SOCK_STREAM is used for TCP connections
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(False)

    # pubsub setup
    # TODO: this and the threads could probably go in a seperate class
    chat_pub = Publisher(HOST_IP, PORT)
    chat_sub = Subscriber()
    chat_daemon = Pyro5.api.Daemon(host=OWN_IP, port=CHAT_PORT)
    chat_uri = chat_daemon.register(chat_sub)

    # another 2 threads yippee!!!
    threading.Thread(target=sub_thread, daemon=True, args=(chat_daemon,)).start()
    threading.Thread(target=pub_thread, daemon=True, args=(chat_pub,)).start()


    # sets up the player
    player = Player("green", 40, 40)
    player.update_position(pygame.Vector2(
        screen.get_width() / 2, screen.get_height() / 2))
    remote_players = {}

    # sets up the background
    bg = pygame.Surface(screen.get_size())
    bg.fill((50, 50, 50))
    bg_image = pygame.image.load("Assets/win7_bg.jpg")

    # clock is used for locking framerate
    # this game runs (or tries to run) at 60 frames / second
    clock = pygame.time.Clock()
    running = True

    while running:
        # dt is the amount of time passed since the last frame
        dt = clock.tick(60) / 1000

        # this is the pygame event queue, the only thing it checks for here is if the QUIT event is fired (which happens when you close the window)
        # the player class also checks the event queue for keyboard inputs so it can move
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update local player
        player.update(screen, dt)

        # Send position and chat URI to host
        # this is an admittedly wasteful way to send the URI
        # The chat URI should ideally be sent once upon connection
        # doing it this way means there is functionally useless data being sent along with the player position
        # however, the amount of data being transmitted is so little that it should be fine
        # I do want to check exactly how many bytes are being sent here just for my own curiosity
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
                        chat_pub.register(Pyro5.api.Proxy(pos[2]), a)
                    remote_players[a].update_position(pygame.Vector2(pos[0], pos[1]))
                    # detect collision
                    # we can use this for RPC
                    if remote_players[a].rect.colliderect(player.rect):
                        # we have to have the main thread claim ownership when this call happens
                        # if you use the chat at all, the chat thread claims ownership, and this doesn't work anymore
                        # but the chat thread claims ownership on every message, so if we claim ownership on every collision chat will just claim it back when we use it
                        # this will still probably cause a problem if you chat WHILE colliding though
                        chat_pub._pyroClaimOwnership()
                        chat_pub.collide(a)
        except BlockingIOError:
            pass

        # Draw everything
        screen.blit(bg_image, (0, 0))

        player.draw(screen)
        for p in remote_players.values():
            p.draw(screen)
        pygame.display.flip()

    # stuff that happens after the game is closed. 
    chat_daemon.shutdown()
    sock.close()