# ok so i did straight up copy the boilerplate code from this tutorial
# http://pygametutorials.wikidot.com/tutorials-basic

import pygame

from pygame.locals import *
 
class App:
    def __init__(self):
        self._running = True
        self._display_surf = None
        self.size = self.weight, self.height = 1280, 720

        self.window_title = "CECS 327"

        self.bg = Level()
 
    def on_init(self):

        pygame.init()

        self.bg.on_init()

        self._display_surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption(self.window_title)

        self._running = True
 
    def on_event(self, event):
        if event.type == pygame.QUIT:
            self._running = False

    def on_loop(self):
        pass

    def on_render(self):
        # always render background first
        self._display_surf.blit(self.bg._bg, (0,0))

    def on_cleanup(self):
        pygame.quit()
 
    def on_execute(self):
        if self.on_init() == False:
            self._running = False

        """
        MAIN GAME LOOP
        """

        while( self._running ):
            for event in pygame.event.get():
                self.on_event(event)

            self.on_loop()
            self.on_render()

        self.on_cleanup()
 
# I never understood why people did this
# anything in here only runs if the python file is RUN
# as opposed to imported into another file
if __name__ == "__main__" :
    theApp = App()
    theApp.on_execute()

