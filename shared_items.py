import threading
from item import Item
from transaction import Transaction
import pygame as pg


class SharedItems:
    def __init__(self):
        self.items = []
        self.lock = threading.Lock()
        self.initialized = False  # whether items have been set

    def serialize(self):
        """Return a list of item positions."""
        data = []
        for item in self.items:
            data.append({
                "x": item.position.x,
                "y": item.position.y
            })
        return data

    def load_from_serialized(self, data):
        """Load items from a list of positions."""
        if self.initialized:
            return  # ignore if we already have items
        self.items = []
        for info in data:
            # Recreate Item at the stored position
            item = Item((info["x"], info["y"]))  # default color & radius
            self.items.append(item)
        self.initialized = True

    def initialize_items(self, screen_width, screen_height, count=5):
        """Only called by the first peer"""
        with self.lock:
            if not self.initialized:
                import random
                for _ in range(count):
                    x = random.randint(50, screen_width - 50)
                    y = random.randint(50, screen_height - 50)
                    self.items.append(Item((x, y)))
                self.initialized = True

    def get_state(self):
        """Return picklable state to share with peers"""
        with self.lock:
            return [(item.position.x, item.position.y, item.picked_up) for item in self.items]

    def load_state(self, state):
        """Load state received from a peer"""
        with self.lock:
            self.items = []
            for x, y, picked_up in state:
                item = Item((x, y))
                item.picked_up = picked_up
                self.items.append(item)
            self.initialized = True

    def draw(self, screen):

        for item in self.items:
            item.draw(screen)

    def draw_progress(self, screen, transaction: Transaction):
        """Draw pickup progress bar above the item"""
        if not transaction or not transaction.active:
            return
        progress = transaction.progress()
        # Draw a small bar above the item
        bar_width = transaction.item.rect.width
        bar_height = 5
        x = transaction.item.rect.x
        y = transaction.item.rect.y - 10  # above item
        pg.draw.rect(screen, (100, 100, 100),
                     (x, y, bar_width, bar_height))  # background
        pg.draw.rect(screen, (0, 255, 0), (x, y, bar_width *
                                           progress, bar_height))  # progress
