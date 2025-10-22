import pygame
from button import Button

# this screen lets the user choose whether they want to connect to an existing instance or make a new one


class MainMenu:
    def __init__(self):
        self.HostButton = Button(
            "Create new instance", pygame.Vector2(150, 50), "white")
        self.JoinButton = Button(
            "Join existing instance", pygame.Vector2(150, 50), "green")

    def exec(self, screen: pygame.Surface):
        # renders the buttons, then uses a while loop to detect the click

        screen.fill("black")
        # adds offset for both buttons
        offset = 50
        self.HostButton.update_position(pygame.Vector2(screen.get_width() / 2, (screen.get_height() / 2) + offset))
        self.JoinButton.update_position(pygame.Vector2(screen.get_width() / 2, (screen.get_height() / 2) - offset))
        self.ButtonGroup.draw(screen)
        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                # detect button press

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.HostButton.detect_press(pygame.mouse.get_pos()):
                        return "host"
                    if self.JoinButton.detect_press(pygame.mouse.get_pos()):
                        return "join"
