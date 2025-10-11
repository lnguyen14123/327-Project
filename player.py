import pygame


class Player(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        # parent class constructor
        pygame.sprite.Sprite.__init__(self)

        # create position for the player
        # we'll assign this after the screen is created so they can go in the center
        self.position: pygame.Vector2

        # create an image
        # we'll load a proper sprite later, they'll just be a rectangle for testing
        # sprite groups automatically draw the value under self.image at the position of self.rect when the draw function is called
        self.image: pygame.Surface = pygame.Surface([width, height])
        self.image.fill(color)

        # creates a rectangle from the sprite. this is used for checking collisions and any bounds calculations
        # note: currently this rect only reflects the DIMENSIONS of the character, NOT its POSITION.
        self.rect: pygame.rect.Rect = self.image.get_rect()

        # movespeed for the character
        self.movespeed: int = 900

        # group that contains all instances of this player's bullets
        self.bullets = pygame.sprite.Group()
        self.bullet_speed = 200

    def movement_handler(self, dt, screen_width=1280, screen_height=720):

        # create temporary position variable
        # this will be reassigned to the main position after we do the movement calculations
        # idk, this is how I'm used to doing it in Unity
        pos: pygame.Vector2 = self.position

        # keys is a list of all the keys that are currently pressed
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            pos.y -= self.movespeed * dt
        if keys[pygame.K_s]:
            pos.y += self.movespeed * dt
        if keys[pygame.K_a]:
            pos.x -= self.movespeed * dt
        if keys[pygame.K_d]:
            pos.x += self.movespeed * dt

        # detect edges of screen
        # hardcoding the screen size for now. hope this doesn't suck to decouple later!
        # also fun fact: pygame coordinates are fucked!
        # the top LEFT of the screen is (0,0), and the y coordinate gets BIGGER as you go down

        # also, the rectangle still only reflects the size and not the position
        # but this still works because we're only using the size with the player's current position
        if pos.x + self.rect.width > 1280:
            pos.x = 1280 - self.rect.width
        if pos.x < 0:
            pos.x = 0
        if pos.y + self.rect.height > 720:
            pos.y = 720 - self.rect.height
        if pos.y < 0:
            pos.y = 0

        # reassign position
        self.update_position(pos)

    def draw(self, surf):
        surf.blit(self.image, self.position)

    # simple helper function that updates both positions
    def update_position(self, pos: pygame.Vector2):
        self.position = pos
        self.rect.topleft = pos.x, pos.y

    def fire_bullet(self, vel: pygame.Vector2, pos: pygame.Vector2):
        self.bullets.add(Bullet(vel, pos))

    def bullet_handler(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            pos = self.position + pygame.Vector2(0, -50)
            self.fire_bullet(pygame.Vector2(0, -1)*self.bullet_speed, pos)
        if keys[pygame.K_DOWN]:
            pos = self.position + pygame.Vector2(0, 50)
            self.fire_bullet(pygame.Vector2(0, 1)*self.bullet_speed, pos)
        if keys[pygame.K_LEFT]:
            pos = self.position + pygame.Vector2(-50, 0)
            self.fire_bullet(pygame.Vector2(-1, 0)*self.bullet_speed, pos)
        if keys[pygame.K_RIGHT]:
            pos = self.position + pygame.Vector2(50, 0)
            self.fire_bullet(pygame.Vector2(1, 0)*self.bullet_speed, pos)

    def update(self, surf, dt):
        self.movement_handler(dt)
        self.draw(surf)

        # self.bullet_handler()
        # self.bullets.update(dt)
        # self.bullets.draw(surf)
