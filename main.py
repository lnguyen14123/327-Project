# Example file showing a square moving on screen
import pygame
from pygame.locals import *
from main_menu import MainMenu
from player import Player

# TODO: sprites can be added to groups. figure out how to do this to render all players as a group

# TODO: add RemotePlayer class for other players in server

print("Hello! wasd to move, arrow keys to shoot.")
    
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
player1.update_position(pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2))

# adds the player to the group
# we'll use this group with all the remote players as well
# then when you call group.draw, it renders all the players at the same time
player_group = pygame.sprite.Group(player1)

menu = MainMenu()
menu.exec(screen)

# this while loop runs once per frame
# if you've ever used unity or godot, this is basically the Update()/process() function, while everything before is the Start() function
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # fill the screen with a color to wipe away anything from last frame
    screen.fill("white")

    # render the background
    # (technically, draw the background surface onto the display surface)
    # screen fill into this must be done first, so everything draws in the right order
    screen.blit(bg_image, (0,0))

    player_group.update(dt, screen)
    player_group.draw(screen)

    # flip() the display to put your work on screen
    pygame.display.flip()

    # limits FPS to 60
    # dt is delta time in seconds since last frame, used for framerate-
    # independent physics.
    # ^ comment from the tutorial I copied the boilerplate from lol
    # for all those complex physics calculations we'll be doing /s
    dt = clock.tick(60) / 1000

pygame.quit()