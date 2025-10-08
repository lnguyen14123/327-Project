import pygame

class Button (pygame.sprite.Sprite):
    def __init__(self, text: str, size:pygame.Vector2, color: str):
        # parent class constructor
        pygame.sprite.Sprite.__init__(self)
        self.text = text
        self.image: pygame.Surface = pygame.Surface([size.x, size.y])
        self.position: pygame.Vector2
        self.image.fill(color)
        self.rect = self.image.get_rect()

    def update_position(self, pos: pygame.Vector2):
        self.position = pos
        self.rect.topleft = (pos.x, pos.y)
    
    def detect_press(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos[0], mouse_pos[1])

    def draw(self, surf: pygame.Surface):
        surf.blit(self.image, self.position)