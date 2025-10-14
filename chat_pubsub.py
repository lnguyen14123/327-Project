from Pyro5.api import expose

"""
Each local player has 2 objects: a publisher and a subscriber. 

The publisher's job is to take the local player's chat messages and send them to each remote subscriber object (i.e. each other remote player). It also keeps a list of all remote players' subscriber objects.

The subscriber's job is to be accessed by another remote player, and used to display their chat messages on the local player's machine.

the @expose means that Subscriber can be used as a remote object using Pyro5
"""

@expose
class Subscriber():
    def __init__(self):
        pass

    def recieve(self, msg):
        print(msg)

    def on_collision(self, addr):
        print(f"You just collided with the player at {addr}!")

class Publisher():
    def __init__(self, host_ip, port):
        self.subs: list[Subscriber] = []
        self.subs_dict = {}
        self.address = (host_ip, port)

    def register(self, sub, addr):
        self.subs.append(sub)
        self.subs_dict.update({addr: sub})
    
    def publish(self, msg: str):
        for sub in self.subs:
            # the thread this is running in must claim ownership of the proxy before it can use it
            sub._pyroClaimOwnership()
            sub.recieve(msg)

    def collide(self, a):
        self.subs_dict[a].on_collision(self.address)
        