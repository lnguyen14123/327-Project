import pygame
from player import Player
from chat_box import ChatBox
from item import Item
from shared_items import SharedItems
from transaction import Transaction
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
                        # Ask the first discovered peer for the item list
                        chat_pub.send_direct(peer_chat_uri, ("REQUEST_ITEMS",))

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
    game_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    game_sock.bind((OWN_IP, 0))
    game_port = game_sock.getsockname()[1]
    game_sock.setblocking(False)

    # ------------------- CHAT SETUP -------------------
    cbox = ChatBox()
    lamport = LamportClock()
    chat_queue = Queue()

    shared_items = SharedItems()
    chat_pub = Publisher(OWN_IP, game_port, lamport=lamport,
                         shared_items=shared_items)
    peers = {}  # (ip, port) -> URI
    peers_lock = threading.Lock()
    stop_event = threading.Event()

    chat_sub = Subscriber(cbox, lamport=lamport,
                          shared_items=shared_items, publisher=chat_pub)

    chat_daemon = Pyro5.api.Daemon(host=OWN_IP)
    chat_uri = chat_daemon.register(chat_sub)
    chat_pub.own_uri = chat_uri

    # ------------------- THREADS -------------------
    threading.Thread(target=sub_thread, daemon=True,
                     args=(chat_daemon, stop_event)).start()
    threading.Thread(target=pub_thread, daemon=True,
                     args=(chat_pub, chat_queue)).start()
    threading.Thread(target=announce_self, daemon=True,
                     args=(game_port, chat_uri, stop_event)).start()
    threading.Thread(target=listen_peers, daemon=True,
                     args=(peers, peers_lock, chat_pub, stop_event, chat_uri)).start()

    # ------------------- PLAYER SETUP -------------------
    player = Player("green", 40, 40)
    player.update_position(pygame.Vector2(
        screen.get_width() / 2, screen.get_height() / 2))
    remote_players = {}
    bg_image = pygame.image.load("Assets/win7_bg.jpg")
    clock = pygame.time.Clock()
    running = True
    current_tx = None

    # ------------------- ITEM INITIALIZATION -------------------
    # Wait briefly for peers to appear
    MAX_WAIT = 3.0
    poll_interval = 0.05
    start_time = time.time()
    while time.time() - start_time < MAX_WAIT:
        with peers_lock:
            if peers:
                break
        time.sleep(poll_interval)

    with peers_lock:
        if not peers:
            print("I am the first peer — generating items.")
            shared_items.initialize_items(
                screen.get_width(), screen.get_height())
            shared_items.initialized = True
        else:
            # Pick any peer to request items from
            peer_uri = list(peers.values())[0]
            try:
                chat_pub.send_direct(peer_uri, ("REQUEST_ITEMS",))
            except Exception as e:
                print("Failed sending REQUEST_ITEMS:", e)

    # ------------------- MAIN LOOP -------------------

    collision_cooldown = {}   # addr -> last_time_sent
    COLLISION_COOLDOWN_SECONDS = 1.0

    while running:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            msg = cbox.handle_event(event)
            if msg:
                ts = chat_pub.lamport.send_event() if chat_pub.lamport else 0
                cbox.receive_chat((ts, f"You: {msg}"))
                chat_queue.put(msg)

        # Update local player
        player.update(screen, dt)

        # Send local position
        data = pickle.dumps((player.position.x, player.position.y))
        with peers_lock:
            for (peer_ip, peer_port), _ in peers.items():
                game_sock.sendto(data, (peer_ip, peer_port))

        # Receive remote positions
        try:
            while True:
                recv_data, addr = game_sock.recvfrom(1024)
                x, y = pickle.loads(recv_data)
                with peers_lock:
                    if addr not in remote_players:
                        remote_uri = peers.get(addr)
                        remote_players[addr] = Player("purple", 40, 40)
                        chat_pub.register(remote_uri, addr)

                    remote_players[addr].update_position(pygame.Vector2(x, y))

                    now = time.time()

                    if remote_players[addr].rect.colliderect(player.rect):
                        last_time = collision_cooldown.get(addr, 0)

                        # only send if cooldown passed
                        if now - last_time >= COLLISION_COOLDOWN_SECONDS:
                            collision_cooldown[addr] = now
                            chat_pub.collide(addr)
        except BlockingIOError:
            pass

        # Item pickup / collision
        for item in shared_items.items[:]:
            if player.rect.colliderect(item.rect):
                if not current_tx or not current_tx.active:
                    current_tx = Transaction(player, item, lamport, chat_pub)
                    current_tx.begin()

                conflict = any(
                    other.rect.colliderect(item.rect) and other.id != player.id
                    for other in remote_players.values()
                )

                if conflict:
                    current_tx.abort()
                    current_tx = None
                elif current_tx and current_tx.check_commit():

                    x, y = int(item.rect.x), int(item.rect.y)
                    for local_item in shared_items.items[:]:
                        if int(local_item.rect.x) == x and int(local_item.rect.y) == y:
                            shared_items.items.remove(local_item)
                            break

                    chat_pub.broadcast_transaction(
                        "PICK_ITEM", player.id, item)
                    current_tx = None
            else:
                # If player moved away from the item, abort any ongoing transaction
                if current_tx and current_tx.item == item:
                    current_tx.abort()
                    current_tx = None

        # ------------------- DRAW -------------------
        screen.blit(bg_image, (0, 0))
        player.draw(screen)
        for p in remote_players.values():
            p.draw(screen)
        if shared_items.initialized:
            shared_items.draw(screen)
        if current_tx:
            shared_items.draw_progress(screen, current_tx)
        cbox.draw(screen)
        pygame.display.flip()

    # ------------------- CLEANUP -------------------
    stop_event.set()
    try:
        chat_daemon.shutdown()
    except Exception:
        pass
    game_sock.close()
