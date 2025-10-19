
# Example file showing a square moving on screen


import pygame
from main_menu import MainMenu
from host import run_host
from client import run_client


# TODO: sprites can be added to groups. figure out how to do this to render all players as a group

# TODO: add RemotePlayer class for other players in server

print("Hello! wasd to move, arrow keys to shoot.")

# pygame setups

pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("CECS 327")


menu = MainMenu()
choice = menu.exec(screen)

if choice == "host":
    run_host(screen)
elif choice == "join":
    run_client(screen)
else:
    print("Menu exited without choosing host or join.")

pygame.quit()
