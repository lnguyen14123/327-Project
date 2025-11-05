from Pyro5.api import expose, Proxy
import threading
from chat_box import ChatBox

@expose
class Subscriber:
    def __init__(self, cbox: ChatBox):
        self.cbox = cbox

    def recieve(self, msg):
        print(msg)
        self.cbox.recieve_chat(msg)

    def on_collision(self, addr):
        print(f"You just collided with the player at {addr}!")


class Publisher:
    def __init__(self, host_ip, port, cbox: ChatBox):
        # Store addresses instead of live proxy objects
        self.subs_uris = []           # list of remote URIs (not objects)
        self.subs_dict = {}           # addr -> URI
        self.address = (host_ip, port)
        self.lock = threading.Lock()  # ensure safe concurrent access
        self.cbox = cbox # chatbox instance

    def register(self, sub_uri, addr):
        """Register a remote subscriber by URI, not by proxy."""
        with self.lock:
            self.subs_uris.append(sub_uri)
            self.subs_dict[addr] = sub_uri

    def publish(self, msg: str):
        """Send a message to all subscribers safely."""
        with self.lock:
            uris = list(self.subs_uris)

        for uri in uris:
            # Each thread creates a *fresh proxy* for this call
            with Proxy(uri) as sub:
                try:
                    sub.recieve(msg)
                except Exception as e:
                    print(f"Failed to send to {uri}: {e}")

        self.cbox.recieve_chat(msg)

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
