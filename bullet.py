class Bullet(pygame.sprite.Sprite):
    def __init__(self, vel: pygame.Vector2, pos: pygame.Vector2):
        pygame.sprite.Sprite.__init__(self)
        self.position = pos
        self.velocity = vel
        # TODO: make img long one way, and make it rotate depending on what side of the player it comes out of
        self.img: pygame.Surface = pygame.Surface([10, 10])
        self.img.fill("white")

    def movement_handler(self, dt):
        pos = self.position

        # detect if bullet hits a wall
        if pos.x + self.rect.right > 1280:
            pos.x = 1280 - self.rect.right
        if pos.x + self.rect.left < 0:
            pos.x = 0 - self.rect.left
        if pos.y + self.rect.bottom > 720:
            pos.y = 720 - self.rect.bottom
        if pos.y + self.rect.top < 0:
            pos.y = 0 - self.rect.top
        
        pos += self.velocity * dt
        self.position = pos

        
    def draw(self, surf: pygame.Surface):
        surf.blit(self.img, self.position)
    
    def update(self, surf: pygame.Surface, dt):
        self.movement_handler(dt)
        self.draw(surf)