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
        self.rect.center = (pos.x, pos.y)
        self.position = pygame.Vector2(self.rect.topleft[0], self.rect.topleft[1])
    
    def detect_press(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos[0], mouse_pos[1])

    def draw(self, surf: pygame.Surface):
        surf.blit(self.image, self.position)