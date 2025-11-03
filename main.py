import pygame
from main_menu import MainMenu
from client import run_client
import sys

print("Hello! wasd to move, arrow keys to shoot.")

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("CECS 327")

# If no command line arguments, show menu
choice = ""
if len(sys.argv) <= 1:
    menu = MainMenu()
    choice = menu.exec(screen)

# In fully P2P design, no host is needed
# All players just run the client
# Optionally, you can skip the menu if a CLI argument is provided
if choice == "join" or (len(sys.argv) > 1 and sys.argv[1] == "join"):
    run_client(screen)
else:
    # Default: just run client in P2P mode
    run_client(screen)

pygame.quit()
