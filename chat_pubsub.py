

class Publisher():
    def __init__(self):
        self.subs: list[Subscriber] = []

    def register(sub: Subscriber):
        self.subs.append(sub)
    
    def publish(self, msg: str):
        for sub in self.subs:
            sub.recieve(msg)

class Subscriber():
    def __init__(self):
        pass

    def recieve(self, msg):
        print(msg)