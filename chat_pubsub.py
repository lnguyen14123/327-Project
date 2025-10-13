from Pyro5.api import expose

@expose
class Subscriber():
    def __init__(self):
        pass

    def recieve(self, msg):
        print(msg)

class Publisher():
    def __init__(self):
        self.subs: list[Subscriber] = []

    def register(self, sub):
        self.subs.append(sub)
    
    def publish(self, msg: str):
        for sub in self.subs:
            # the thread this is running in must claim ownership of the proxy before it can use it
            sub._pyroClaimOwnership()
            sub.recieve(msg)