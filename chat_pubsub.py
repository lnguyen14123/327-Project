import Pyro5.api
from Pyro5.api import expose, Proxy
import threading


@expose
class Subscriber:
    def __init__(self, cbox, lamport=None):
        self.cbox = cbox
        self.lamport = lamport
        pass

    def recieve(self, msg):
        print(msg)

    def on_collision(self, addr):
        print(f"You just collided with the player at {addr}!")

    @Pyro5.api.expose
    def receive_message(self, sender_uri, packet):
        ts, msg_with_ts = packet
        if self.lamport:
            self.lamport.recv_event(ts)

        peer_name = str(sender_uri)
        # msg_with_ts already includes timestamp, just display it
        self.cbox.receive_chat(f"{peer_name}: {msg_with_ts}")


class Publisher:
    def __init__(self, host_ip, port, own_uri=None, lamport=None):
        self.subs_dict = {}      # addr -> URI
        self.address = (host_ip, port)
        self.lock = threading.Lock()
        self.own_uri = own_uri   # URI of this client
        self.lamport = lamport

    def register(self, sub_uri, addr):
        with self.lock:
            self.subs_dict[addr] = sub_uri

    def publish(self, msg: str):
        """Send a message to all subscribers including local display"""

        ts = self.lamport.send_event() if self.lamport else 0

        # Append timestamp directly to message string
        msg_with_ts = f"[{ts}] {msg}"

        # Local display
        local_display_uri = self.own_uri or "You"
        print(f"{local_display_uri}: {msg_with_ts}")

        with self.lock:
            uris = list(self.subs_dict.values())

        for uri in uris:
            try:
                with Proxy(uri) as sub:
                    sub._pyroTimeout = 1.0   # 1 second timeout
                    # Send timestamp separately in packet
                    sub.receive_message(local_display_uri, (ts, msg_with_ts))
            except Exception as e:
                print(f"Failed to send to {uri}: {e}")

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
