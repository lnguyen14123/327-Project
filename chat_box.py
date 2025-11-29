import pygame as pg
from queue import Queue


class ChatBox:
    def __init__(self, max_msg_count=5, offset=100):
        pg.font.init()

        self.font = pg.font.Font(None, 32)
        self.full_rect = pg.Rect(0, 720-300, 500, 300)  # chat log area
        self.input_rect = pg.Rect(0, 720-50, 500, 50)   # input area
        self.chat_messages = []
        self.max_msg_count = max_msg_count

        # calculate message positions
        px_msg = (self.full_rect.height - offset) / self.max_msg_count
        self.msg_positions = []
        setup_pos = 720-50
        for i in range(self.max_msg_count):
            self.msg_positions.append((0, setup_pos))
            setup_pos -= px_msg

        # typing state
        self.active = False
        self.input_text = ""

    def draw(self, screen: pg.Surface):
        """Draws chat messages and input text"""
        # Draw chat messages
        for i in range(min(self.max_msg_count, len(self.chat_messages))):
            msg = self.chat_messages[i][1]  # get string
            font_surf = self.font.render(msg, True, "Black")
            screen.blit(font_surf, self.msg_positions[i])

        # Draw input box
        pg.draw.rect(screen, "Gray", self.input_rect)
        input_surf = self.font.render(self.input_text, True, "Black")
        screen.blit(input_surf, (self.input_rect.x + 5, self.input_rect.y + 5))

    def msgs_debug(self):
        self.chat_messages = [
            "This is a chat message",
            "This is also a chat message!",
            "This is a third chat message!",
            "How many chat messages are we gonna put in here?",
            "I think this should be the last one."
        ]

    def draw_debug(self, screen):
        pg.draw.rect(screen, "White", self.full_rect)
        pg.draw.rect(screen, "Gray", self.input_rect)

    def receive_chat(self, msg_with_ts):
        """
        Add a message with Lamport timestamp. 
        msg_with_ts should already include [ts] in the string for display.
        We'll parse ts to sort messages.
        """
        # Parse ts from string: assume format "[ts] rest of message"
        try:
            ts_end = msg_with_ts.index("]")
            ts = int(msg_with_ts[1:ts_end])
        except:
            ts = 0  # fallback

        # Store as tuple (timestamp, message)
        self.chat_messages.append((ts, msg_with_ts))

        # Sort by timestamp so messages appear in order
        self.chat_messages.sort(key=lambda x: x[0])

        # Keep only last max_msg_count messages
        while len(self.chat_messages) > self.max_msg_count:
            self.chat_messages.pop(0)

    # -------------------- NEW METHODS --------------------

    def handle_event(self, event):
        """Call this in the main Pygame loop to capture typing"""
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN and self.active:
                msg = self.input_text.strip()
                self.input_text = ""
                return msg  # return the message to send
            elif event.key == pg.K_BACKSPACE and self.active:
                self.input_text = self.input_text[:-1]
            elif self.active:
                self.input_text += event.unicode
        elif event.type == pg.MOUSEBUTTONDOWN:
            # Activate if click is inside input box
            self.active = self.input_rect.collidepoint(event.pos)
        return None

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def is_activated(self):
        return self.active
