import pygame
from button import Button

# this screen lets the user choose whether they want to connect to an existing instance or make a new one

class MainMenu:
    def __init__(self):
        self.HostButton: Button = Button("Create new instance", pygame.Vector2(150, 50), "white")
        self.JoinButton: Button = Button("Join existing instance", pygame.Vector2(150, 50), "white")
        # my first time using Group, not sure how it works
        self.ButtonGroup: pygame.sprite.Group = pygame.sprite.Group(self.HostButton, self.JoinButton)

    def exec(self, screen: pygame.Surface):
        # renders the buttons, then uses a while loop to detect the click
        screen.fill("black")
        # offset from center for both buttons
        offset: int = 50
        self.HostButton.update_position(pygame.Vector2(screen.get_width() / 2, (screen.get_height() / 2)+offset))
        self.JoinButton.update_position(pygame.Vector2(screen.get_width() / 2, (screen.get_height() / 2)-offset))
        self.HostButton.draw(screen)
        self.JoinButton.draw(screen)
        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # detect button press
                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.HostButton.detect_press(pygame.mouse.get_pos()):
                        print("You pressed the Host button!")
                        running = False

                    if self.JoinButton.detect_press(pygame.mouse.get_pos()):
                        print("You pressed the Join button!")
                        running = False