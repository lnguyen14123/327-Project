import Pyro5.api
from Pyro5.api import expose, Proxy
import threading


@expose
class Subscriber:
    def __init__(self, cbox):
        self.cbox = cbox
        pass

    def recieve(self, msg):
        print(msg)

    def on_collision(self, addr):
        print(f"You just collided with the player at {addr}!")

    @Pyro5.api.expose
    def receive_message(self, sender_uri, msg):
        peer_name = str(sender_uri)
        self.cbox.receive_chat(f"{peer_name}: {msg}")


class Publisher:
    def __init__(self, host_ip, port, own_uri=None):
        self.subs_dict = {}      # addr -> URI
        self.address = (host_ip, port)
        self.lock = threading.Lock()
        self.own_uri = own_uri   # URI of this client

    def register(self, sub_uri, addr):
        with self.lock:
            self.subs_dict[addr] = sub_uri

    def publish(self, msg: str):
        """Send a message to all subscribers including local display"""
        # Display locally
        if self.own_uri:
            local_display_uri = self.own_uri
        else:
            local_display_uri = "You"
        print(f"{local_display_uri}: {msg}")  # optional console log

        with self.lock:
            uris = list(self.subs_dict.values())

        for uri in uris:
            try:
                with Proxy(uri) as sub:
                    sub.receive_message(local_display_uri, msg)
            except Exception as e:
                print(f"Failed to send to {uri}: {e}")

    def collide(self, addr):
        """Handle collision safely."""
        uri = self.subs_dict.get(addr)
        if not uri:
            print(f"No subscriber found for {addr}")
            return

        # Create a fresh proxy to call into this subscriber
        with Proxy(uri) as sub:
            try:
                sub.on_collision(self.address)
            except Exception as e:
                print(f"Failed to notify collision: {e}")
