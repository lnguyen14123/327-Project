import time
import pygame as pg


class Transaction:
    PICKUP_TIME = 3  # seconds to pick up an item

    def __init__(self, player, item, lamport, publisher):
        self.player = player
        self.item = item
        self.start_time = None
        self.lamport = lamport
        self.publisher = publisher
        self.active = False

    def begin(self):
        self.start_time = time.time()
        self.active = True

    def progress(self):
        """Return progress ratio from 0.0 to 1.0"""
        if not self.active or not self.start_time:
            return 0
        elapsed = time.time() - self.start_time
        return min(elapsed / self.PICKUP_TIME, 1.0)

    def check_commit(self):
        """Commit if enough time passed"""
        if not self.active:
            return False
        if time.time() - self.start_time >= self.PICKUP_TIME:
            self.commit()
            return True
        return False

    def commit(self):
        """Remove item and broadcast transaction"""
        if self.publisher.shared_items and self.item in self.publisher.shared_items.items:
            # Remove locally
            self.publisher.shared_items.items.remove(self.item)

            # Broadcast transaction with coordinates
            ts = self.lamport.send_event() if self.lamport else 0
            msg = f"TX:{ts}:PICK_ITEM:{{'player_id':'{self.player.id}','item_x':{int(self.item.rect.x)},'item_y':{int(self.item.rect.y)}}}"
            self.publisher.publish(msg)

        self.active = False

    def abort(self):
        self.active = False
