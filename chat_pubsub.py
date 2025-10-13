from Pyro5.api import expose
import asyncio

@expose
class Subscriber():
    def __init__(self):
        pass

    def recieve(self, msg):
        print(msg)

class Publisher():
    def __init__(self):
        self.subs: list[Subscriber] = []

    def register(self, sub: Subscriber):
        self.subs.append(sub)
    
    def publish(self, msg: str):
        for sub in self.subs:
            sub.recieve(msg)


async def pub_task(pub: Publisher, sub: Subscriber):
    pub.register(sub)
    while (True):
        msg = input()
        pub.publish(msg)
        if msg == "exit":
            break

pub = Publisher()
sub = Subscriber()
loop = asyncio.get_event_loop()
loop.create_task(pub_task(pub, sub))
loop.run_forever()