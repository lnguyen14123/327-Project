import pygame
from player import Player
from chat_pubsub import *
import socket
import pickle
import Pyro5.api
import threading
import time
import struct

# ------------------- SETTINGS -------------------
OWN_IP = socket.gethostbyname(socket.gethostname())
DISCOVERY_GRP = "224.1.1.1"   # multicast group for discovery
DISCOVERY_PORT = 10000         # multicast port
DISCOVERY_INTERVAL = 2         # seconds between broadcasts

# ------------------- THREADS -------------------


def sub_thread(daemon: Pyro5.api.Daemon):
    """Handles incoming Pyro5 calls for chat/collision."""
    daemon.requestLoop()


def pub_thread(pub: Publisher):
    """Handles outgoing chat messages from terminal."""
    while True:
        msg = input()
        pub.publish(msg)


def announce_self(game_port, chat_uri, stop_event):
    """Broadcast this client's existence using multicast."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)

    msg = pickle.dumps((OWN_IP, game_port, chat_uri))
    while not stop_event.is_set():
        sock.sendto(msg, (DISCOVERY_GRP, DISCOVERY_PORT))
        time.sleep(DISCOVERY_INTERVAL)


def listen_peers(peers, peers_lock, chat_pub, stop_event, self_chat_uri):
    """
    Listen for discovery messages from other peers and add them to peers dict.
    Uses self_chat_uri to ignore your own announcements.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,
                        1)  # macOS / Linux
    except AttributeError:
        pass

    sock.bind(('', DISCOVERY_PORT))
    mreq = struct.pack("4s4s", socket.inet_aton(
        DISCOVERY_GRP), socket.inet_aton("0.0.0.0"))
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    sock.setblocking(False)

    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            peer_ip, peer_game_port, peer_chat_uri = pickle.loads(data)

            # Ignore self by chat_uri
            if peer_chat_uri == self_chat_uri:
                continue

            peer_addr = (peer_ip, peer_game_port)
            with peers_lock:
                if peer_addr not in peers:
                    peers[peer_addr] = peer_chat_uri
                    chat_pub.register(Pyro5.api.Proxy(
                        peer_chat_uri), peer_addr)
                    print(f"Discovered peer: {peer_addr}")

        except BlockingIOError:
            continue
        except Exception as e:
            print("listen_peers error:", e)

# ------------------- CLIENT / GAME LOOP -------------------


def run_client(screen):
    # ------------------- GAME SOCKET -------------------
    game_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_sock.bind((OWN_IP, 0))  # OS picks free port
    game_port = game_sock.getsockname()[1]
    game_sock.setblocking(False)

    # ------------------- CHAT SETUP -------------------
    chat_pub = Publisher(OWN_IP, game_port)
    chat_sub = Subscriber()
    chat_daemon = Pyro5.api.Daemon(host=OWN_IP)
    chat_uri = chat_daemon.register(chat_sub)

    threading.Thread(target=sub_thread, daemon=True,
                     args=(chat_daemon,)).start()
    threading.Thread(target=pub_thread, daemon=True, args=(chat_pub,)).start()

    # ------------------- PEER DISCOVERY -------------------
    peers = {}  # peer_addr -> chat_uri
    peers_lock = threading.Lock()
    stop_event = threading.Event()

    threading.Thread(target=announce_self, daemon=True, args=(
        game_port, chat_uri, stop_event)).start()

    # threading.Thread(target=listen_peers, daemon=True, args=(
    #     peers, peers_lock, chat_pub, stop_event)).start()

    # After chat setup
    self_chat_uri = chat_uri  # your unique identifier
    threading.Thread(
        target=listen_peers,
        daemon=True,
        args=(peers, peers_lock, chat_pub, stop_event, self_chat_uri)
    ).start()

    # ------------------- PLAYER SETUP -------------------
    player = Player("green", 40, 40)
    player.update_position(pygame.Vector2(
        screen.get_width() / 2, screen.get_height() / 2))
    remote_players = {}

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

        # ------------------- SEND LOCAL POSITION -------------------
        data = pickle.dumps((player.position.x, player.position.y, chat_uri))
        with peers_lock:
            for (peer_ip, peer_port), _ in peers.items():
                game_sock.sendto(data, (peer_ip, peer_port))

        # ------------------- RECEIVE REMOTE POSITIONS -------------------
        try:
            while True:
                recv_data, addr = game_sock.recvfrom(1024)
                x, y, remote_chat_uri = pickle.loads(recv_data)

                with peers_lock:
                    if addr not in remote_players:
                        remote_players[addr] = Player("purple", 40, 40)
                        chat_pub.register(
                            Pyro5.api.Proxy(remote_chat_uri), addr)
                    remote_players[addr].update_position(pygame.Vector2(x, y))
                    if remote_players[addr].rect.colliderect(player.rect):
                        chat_pub.collide(addr)
        except BlockingIOError:
            pass

        # ------------------- DRAW -------------------
        screen.blit(bg_image, (0, 0))
        player.draw(screen)
        for p in remote_players.values():
            p.draw(screen)
        pygame.display.flip()

    # ------------------- CLEANUP -------------------
    stop_event.set()
    chat_daemon.shutdown()
    game_sock.close()
