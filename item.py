import pygame as pg


class Item:
    def __init__(self, position, color="yellow", radius=10):
        self.position = pg.Vector2(position)
        self.color = color
        self.radius = radius
        self.rect = pg.Rect(self.position.x - radius,
                            self.position.y - radius, radius*2, radius*2)
        self.picked_up = False  # track if someone already got it

    def draw(self, screen):
        if not self.picked_up:
            pg.draw.circle(screen, self.color, (int(
                self.position.x), int(self.position.y)), self.radius)

    def pick_up(self):
        if not self.picked_up:
            self.picked_up = True
            return True
        return False
