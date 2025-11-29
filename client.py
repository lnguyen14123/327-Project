import pygame
from player import Player
from chat_box import ChatBox
from chat_pubsub import *
import socket
import pickle
import Pyro5.api
import threading
import time
import struct
from queue import Queue
from lamport_clock import LamportClock


# ------------------- SETTINGS -------------------
OWN_IP = socket.gethostbyname(socket.gethostname())
DISCOVERY_GRP = "224.1.1.1"   # multicast group for discovery
DISCOVERY_PORT = 10000         # multicast port
DISCOVERY_INTERVAL = 2         # seconds between broadcasts

# ------------------- THREADS -------------------


def sub_thread(daemon: Pyro5.api.Daemon, stop_event: threading.Event):
    """Handles incoming Pyro5 calls for chat/collision."""
    try:
        # requestLoop accepts a loopCondition callable. Keep serving while not stopped.
        daemon.requestLoop(loopCondition=lambda: not stop_event.is_set())
    except Exception as e:
        print("sub_thread error:", e)
    finally:
        try:
            daemon.shutdown()
        except Exception:
            pass


def pub_thread(pub: Publisher, chat_queue):
    """Handles outgoing chat messages from terminal."""
    while True:
        try:
            msg = chat_queue.get_nowait()
            pub.publish(msg)
        except:
            pass
        time.sleep(0.05)


def announce_self(game_port, chat_uri, stop_event):
    """Broadcast this client's existence using multicast."""
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    except Exception as e:
        print(e)

    msg = pickle.dumps((OWN_IP, game_port, chat_uri))

    try:
        while not stop_event.is_set():
            try:
                sock.sendto(msg, (DISCOVERY_GRP, DISCOVERY_PORT))
            except Exception as e:

                print('Failed on self announce')
                print(e)

            stop_event.wait(DISCOVERY_INTERVAL)

    finally:
        try:
            sock.close()
        except Exception:
            pass


def listen_peers(peers, peers_lock, chat_pub, stop_event, self_chat_uri):
    """
    Listen for discovery messages from other peers and add them to peers dict.
    Uses self_chat_uri to ignore your own announcements.
    """
    try:
        sock = socket.socket(
            socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except Exception as e:

        print(e)
        print("failed to set ports as reusable")

    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT,
                        1)  # macOS / Linux
    except AttributeError:
        pass

    try:
        sock.bind(('', DISCOVERY_PORT))
        mreq = struct.pack("4s4s", socket.inet_aton(
            DISCOVERY_GRP), socket.inet_aton("0.0.0.0"))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setblocking(False)
    except Exception as e:
        print(e)
        print("Failed to bind to discovery port")

    try:
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
                        chat_pub.register(peer_chat_uri, peer_addr)
                        print(f"Discovered peer: {peer_addr}")

            except BlockingIOError:
                continue
            except Exception as e:
                print("listen_peers error:", e)

    finally:
        try:
            sock.close()
        except Exception:
            pass

# ------------------- CLIENT / GAME LOOP -------------------


def run_client(screen):
    # ------------------- GAME SOCKET -------------------
    try:

        game_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        game_sock.bind((OWN_IP, 0))  # OS picks free port
        game_port = game_sock.getsockname()[1]
        game_sock.setblocking(False)
    except Exception as e:
        print(e)
        print('Failed to initialize game socket')

    # ------------------- CHAT SETUP -------------------
    cbox = ChatBox()
    # CHAT DEBUG
    cbox.msgs_debug()

    lamport = LamportClock()

    chat_sub = Subscriber(cbox, lamport=lamport)
    chat_daemon = Pyro5.api.Daemon(host=OWN_IP)
    chat_uri = chat_daemon.register(chat_sub)
    chat_queue = Queue()
    chat_pub = Publisher(OWN_IP, game_port, own_uri=chat_uri, lamport=lamport)

    chat_pub.own_uri = chat_uri

    stop_event = threading.Event()
    threading.Thread(target=sub_thread, daemon=True,
                     args=(chat_daemon, stop_event)).start()

    threading.Thread(target=sub_thread, daemon=True,
                     args=(chat_daemon,)).start()
    threading.Thread(target=pub_thread, daemon=True,
                     args=(chat_pub, chat_queue,)).start()

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

            msg = cbox.handle_event(event)

            if msg:
                cbox.receive_chat(f"You: {msg}")
                chat_queue.put(msg)

        # Update local player
        player.update(screen, dt)

        # ------------------- SEND LOCAL POSITION -------------------
        data = pickle.dumps((player.position.x, player.position.y))
        with peers_lock:
            for (peer_ip, peer_port), _ in peers.items():
                game_sock.sendto(data, (peer_ip, peer_port))

        # ------------------- RECEIVE REMOTE POSITIONS -------------------
        try:
            while True:
                recv_data, addr = game_sock.recvfrom(1024)
                x, y = pickle.loads(recv_data)

                with peers_lock:
                    if addr not in remote_players:
                        remote_chat_uri = peers.get(addr)
                        remote_players[addr] = Player("purple", 40, 40)
                        chat_pub.register(remote_chat_uri, addr)

                    remote_players[addr].update_position(pygame.Vector2(x, y))
                    if remote_players[addr].rect.colliderect(player.rect):
                        chat_pub.collide(addr)

                # chat_msg = subscriber.get_message(addr)
                # peer_name = str(addr)
                # cbox.receive_chat(f"{peer_name}: {chat_msg}")

        except BlockingIOError:
            pass

        # ------------------- DRAW -------------------
        screen.blit(bg_image, (0, 0))
        player.draw(screen)
        for p in remote_players.values():
            p.draw(screen)
        # cbox.draw_debug(screen)
        cbox.draw(screen)
        pygame.display.flip()

    # ------------------- CLEANUP -------------------
    stop_event.set()

    try:
        # trigger proper shutdown of Pyro's request loop (sub_thread uses stop_event)
        chat_daemon.shutdown()
    except Exception:
        pass
    try:
        game_sock.close()
    except Exception:
        pass
