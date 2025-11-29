class LamportClock:
    def __init__(self):
        self.time = 0

    def tick(self):
        """Local event (e.g., typing a message)."""
        self.time += 1
        return self.time

    def send_event(self):
        """Call before sending a message."""
        self.time += 1
        return self.time

    def recv_event(self, received_ts):
        """Call when receiving a message with a timestamp."""
        self.time = max(self.time, received_ts) + 1
        return self.time
