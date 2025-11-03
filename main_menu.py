import pygame
from button import Button

# This screen lets the user start the game in fully P2P mode


class MainMenu:
    def __init__(self):
        self.PlayButton = Button(
            "Play", pygame.Vector2(200, 60), "green"
        )

    def exec(self, screen: pygame.Surface):
        # Render the button in the center of the screen
        screen.fill("black")
        self.PlayButton.update_position(pygame.Vector2(
            screen.get_width() / 2, screen.get_height() / 2))
        self.PlayButton.draw(screen)
        pygame.display.flip()

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None

                # Detect button press
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.PlayButton.detect_press(pygame.mouse.get_pos()):
                        return "play"
