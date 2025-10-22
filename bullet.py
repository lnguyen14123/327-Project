import pygame

class Bullet(pygame.sprite.Sprite):
    def __init__(self, vel: pygame.Vector2, pos: pygame.Vector2):
        pygame.sprite.Sprite.__init__(self)
        self.position = pos
        self.velocity = vel
        # TODO: make img long one way, and make it rotate depending on what side of the player it comes out of
        self.image: pygame.Surface = pygame.Surface([10, 10])
        self.image.fill("white")
        self.rect = self.image.get_rect()

    # simple helper function that updates both positions
    def update_position(self, pos: pygame.Vector2):
        self.position = pos
        self.rect.topleft = pos.x, pos.y

    def movement_handler(self, dt):
        pos = self.position

        # detect if bullet hits a wall, and remove it from the group if it does
        if (
            pos.x + self.rect.width > 1280 or 
            pos.x < 0 or 
            pos.y + self.rect.height > 720 or 
            pos.y < 0
        ):
            self.kill()
        else:
            pos += self.velocity * dt
            self.update_position(pos)

    def draw(self, surf: pygame.Surface):
        surf.blit(self.image, self.position)
    
    def update(self, dt):
        self.movement_handler(dt)
