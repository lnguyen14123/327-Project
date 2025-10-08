# Example file showing a square moving on screen
import pygame
from pygame.locals import *
from button import Button

# TODO: sprites can be added to groups. figure out how to do this to render all players as a group
class Player(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        # parent class constructor
        pygame.sprite.Sprite.__init__(self)

        # create position for the player
        # we'll assign this after the screen is created so they can go in the center
        self.position: pygame.Vector2

        # create an image
        # we'll load a proper sprite later, they'll just be a rectangle for testing
        self.img: pygame.Surface = pygame.Surface([width, height])
        self.img.fill(color)

        # creates a rectangle from the sprite. this is used for checking collisions and any bounds calculations
        # note: currently this rect only reflects the DIMENSIONS of the character, NOT its POSITION.
        self.rect: pygame.rect.Rect = self.img.get_rect()

        # movespeed for the character
        self.movespeed: int = 900

    def movement_handler(self, dt: float):
        # create temporary position variable
        # this will be reassigned to the main position after we do the movement calculations
        # idk, this is how I'm used to doing it in Unity
        pos: pygame.Vector2 = self.position

        # keys is a list of all the keys that are currently pressed
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            pos.y -= self.movespeed * dt
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            pos.y += self.movespeed * dt
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            pos.x -= self.movespeed * dt
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            pos.x += self.movespeed * dt

        # detect edges of screen
        # hardcoding the screen size for now. hope this doesn't suck to decouple later!
        # also fun fact: pygame coordinates are fucked!
        # the top LEFT of the screen is (0,0), and the y coordinate gets BIGGER as you go down
        if pos.x + self.rect.right > 1280:
            pos.x = 1280 - self.rect.right
        if pos.x + self.rect.left < 0:
            pos.x = 0 - self.rect.left
        if pos.y + self.rect.bottom > 720:
            pos.y = 720 - self.rect.bottom
        if pos.y + self.rect.top < 0:
            pos.y = 0 - self.rect.top
        
        # reassign position
        self.position = pos

    def draw(self, surf: pygame.Surface):
        # draws the player onto the given surface, probably the display surface
        surf.blit(self.img, self.position)

    def update(self, surf: pygame.Surface, dt):
        # just calls movement handler and draw in one lol
        # also update() is a built in function for sprites
        # it doesn't do anything by default, but it's called by Group.update() when the sprite is in a group
        self.movement_handler(dt)
        self.draw(surf)

# TODO: add RemotePlayer class for other players in server


def title_screen():
    onTitleScreen = True
    # TODO: set up the buttons and just loop to detect a button press
    while onTitleScreen:
        pass


    
# pygame setup
pygame.init()
screen: pygame.Surface = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("CECS 327")
clock = pygame.time.Clock()
running: bool = True
dt = 0

# frutiger aero or whatever the kids say
bg_image: pygame.Surface = pygame.image.load("Assets/win7_bg.jpg")

player1: Player = Player("purple", 40, 40)

# put the player in the middle of the screen
player1.position = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

# this while loop runs once per frame
# if you've ever used unity or godot, this is basically the Update()/process() function, while everything before is the Start() function
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if butt.detect_press(pygame.mouse.get_pos()):
                print("You pressed the button!")

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # render the background
    # (technically, draw the background surface onto the display surface)
    screen.blit(bg_image, (0,0))

    player1.update(screen, dt)
    butt.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    # ^ comment from the tutorial I copied the boilerplate from lol
    # for all those complex physics calculations we'll be doing /s
    dt = clock.tick(60) / 1000

pygame.quit()