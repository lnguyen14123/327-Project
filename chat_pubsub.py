import Pyro5.api
from Pyro5.api import expose, Proxy
import threading
import pickle


@expose
class Subscriber:
    def __init__(self, cbox, lamport=None, shared_items=None, publisher=None):
        self.cbox = cbox
        self.lamport = lamport
        self.shared_items = shared_items
        self.publisher = publisher

    @Pyro5.api.expose
    def on_collision(self, addr):
        print(f"You just collided with the player at {addr}!")

    @Pyro5.api.expose
    def receive_message(self, sender_uri, packet):
        ts, msg = packet

        # Lamport clock update
        if self.lamport:
            self.lamport.recv_event(ts)

        # Normalize message type
        msg_type = None
        msg_data = None
        if isinstance(msg, tuple):
            msg_type = msg[0]
            msg_data = msg[1:]
        else:
            msg_type = msg

        # ----------------------
        # 1️⃣ Item sync protocol (tuple-based)
        if msg_type == "REQUEST_ITEMS":
            state = self.shared_items.serialize()
            self.publisher.send_direct(sender_uri, ("FULL_ITEM_STATE", state))
            return

        # Subscriber
        if msg_type == "FULL_ITEM_STATE":
            (state,) = msg_data
            self.shared_items.load_from_serialized(state)
            return

        # ----------------------
        # 2️⃣ Transaction (item pickup)
        if isinstance(msg, str) and msg.startswith("TX:"):

            try:
                _, rest = msg.split(":", 1)
                ts, op_data = rest.split(":", 1)
                ts = int(ts)
                # contains 'player_id', 'item_x', 'item_y'
                op_dict = eval(op_data)

                if "PICK_ITEM" in op_data:
                    # Find the local item that matches the coordinates
                    x, y = op_dict["item_x"], op_dict["item_y"]
                    for item in self.shared_items.items[:]:
                        if int(item.rect.x) == x and int(item.rect.y) == y:
                            self.shared_items.items.remove(item)
                            break

                    # Add chat message
                    self.cbox.receive_chat(
                        (ts,
                         f"{op_dict['player_id']} picked up item at ({x},{y})!")
                    )

            except Exception as e:
                print("Failed to apply remote transaction:", e)
            
            return

        # ----------------------
        # 3️⃣ Normal chat
        peer_name = str(sender_uri)
        self.cbox.receive_chat((ts, f"{peer_name}: {msg}"))


class Publisher:
    def __init__(self, host_ip, port, own_uri=None, lamport=None, shared_items=None):
        self.subs_dict = {}  # addr -> URI
        self.address = (host_ip, port)
        self.lock = threading.Lock()
        self.own_uri = own_uri
        self.lamport = lamport
        self.shared_items = shared_items

    def register(self, sub_uri, addr):
        with self.lock:
            self.subs_dict[addr] = sub_uri

    def publish(self, msg: str):
        ts = self.lamport.send_event() if self.lamport else 0
        msg_with_ts = f"[{ts}] {msg}"
        print(f"{self.own_uri or 'You'}: {msg_with_ts}")

        with self.lock:
            uris = list(self.subs_dict.values())

        for uri in uris:
            try:
                with Proxy(uri) as sub:
                    sub._pyroTimeout = 1.0
                    sub.receive_message(self.own_uri, (ts, msg))
            except Exception as e:
                print(f"Failed to send to {uri}: {e}")

    def broadcast_transaction(self, tx_type, player_id, item):
        if not self.shared_items:
            return
        op_dict = {
            'player_id': player_id,
            'item_x': int(item.rect.x),
            'item_y': int(item.rect.y),
            'op': tx_type
        }
        ts = self.lamport.send_event() if self.lamport else 0
        tx_msg = f"TX:{ts}:{op_dict}"
        self.publish(tx_msg)

    def collide(self, addr):
        uri = self.subs_dict.get(addr)
        if not uri:
            print(f"No subscriber found for {addr}")
            return
        try:
            with Proxy(uri) as sub:
                sub._pyroTimeout = 1.0
                sub.on_collision(self.address)
        except Exception as e:
            print(f"Failed to notify collision: {e}")

    def send_direct(self, target_uri, packet):
        ts = self.lamport.send_event() if self.lamport else 0
        try:
            with Proxy(target_uri) as sub:
                sub._pyroTimeout = 1.0
                sub.receive_message(self.own_uri, (ts, packet))
        except Exception as e:
            print(f"Failed direct send to {target_uri}: {e}")
