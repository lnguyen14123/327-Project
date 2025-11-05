import pygame as pg

class ChatBox:
    def __init__(self, max_msg_count=5, offset=100):
        pg.font.init()

        self.font = pg.font.Font(None, 32) # font object 
        self.full_rect = pg.Rect(0, 720-300, 500, 300) # rectangle that contains chat logs
        self.input_rect = pg.Rect(0, 720-50, 500, 50) # rectangle that contains player's chat input
        self.chat_messages = [] # array that holds chat messages
        self.max_msg_count = max_msg_count # maximum amount of chat messages allowed on screen

        # positions to draw the chat messages in
        # take the total height of the rectangle - offset (100, 50px for top + 50px for input rect)
        # divide this by max_msg_count to get number of pixels / chat msg (px_msg). 
        # start from 50 (offset), and count up by px_msg, max_msg_count times.

        px_msg = (self.full_rect.height - offset) / self.max_msg_count
        self.msg_positions = []
        setup_pos = 720-50
        for i in range(self.max_msg_count):
            self.msg_positions.append((0, setup_pos))
            setup_pos -= px_msg



    def draw(self, screen: pg.surface):
        """Draws chat messages on the screen"""
        for i in range(self.max_msg_count):
            font_surf = self.font.render(self.chat_messages[i], True, "Black")
            screen.blit(font_surf, self.msg_positions[i])



    def msgs_debug(self):
        """Add some test messages to the queue"""
        self.chat_messages = ["This is a chat message", "This is also a chat message!", "This is a third chat message!", "How many chat messages are we gonna put in here?", "I think this should be the last one."]

    def draw_debug(self, screen):
        """Draws the rectangles on the screen to make sure they're in the right spot"""
        pg.draw.rect(screen, "White", self.full_rect)
        pg.draw.rect(screen, "Gray", self.input_rect)
    
    def recieve_chat(self, msg):
        """Adds a chat message to the message list, and removes the oldest message if the total message count goes over the max"""
        self.chat_messages.append(msg)

        # remove the oldest chat message if it goes over the max
        while len(self.chat_messages) > self.max_msg_count:
            self.chat_messages.pop(0)


    def activate(self):
        """Activates the input box to allow the user to input a chat message"""
        pass

    def is_activated():
        """Returns true if the input box is activated, i.e. the player is currently writing a chat message"""
        pass

