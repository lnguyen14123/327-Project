import pygame as pg


class ChatBox:
    def __init__(self, max_msg_count=5, offset=100):
        pg.font.init()
        self.font = pg.font.Font(None, 32)
        self.full_rect = pg.Rect(0, 720-300, 500, 300)
        self.input_rect = pg.Rect(0, 720-50, 500, 50)
        self.chat_messages = []  # list of (ts:int, msg:str)
        self.max_msg_count = max_msg_count

        px_msg = (self.full_rect.height - offset) / self.max_msg_count
        self.msg_positions = []
        setup_pos = 720-100
        for i in range(self.max_msg_count):
            self.msg_positions.append((0, setup_pos))
            setup_pos -= px_msg

        self.active = False
        self.input_text = ""

    def draw(self, screen: pg.Surface):

        for i, (ts, msg) in enumerate(reversed(self.chat_messages[-self.max_msg_count:])):
            font_surf = self.font.render(msg, True, "Black")
            screen.blit(font_surf, self.msg_positions[i])

        pg.draw.rect(screen, "Gray", self.input_rect)
        input_surf = self.font.render(self.input_text, True, "Black")
        screen.blit(input_surf, (self.input_rect.x + 5, self.input_rect.y + 5))

    def draw_debug(self, screen):
        pg.draw.rect(screen, "White", self.full_rect)
        pg.draw.rect(screen, "Gray", self.input_rect)

    def receive_chat(self, msg):
        """
        Accepts either:
          1) a tuple (ts:int, message:str)
          2) a string starting with [ts] for legacy messages
        """
        if isinstance(msg, tuple) and len(msg) == 2:
            ts, message = msg
        elif isinstance(msg, str):
            # try parsing [ts] prefix
            try:
                ts_end = msg.index("]")
                ts = int(msg[1:ts_end])
                message = msg
            except:
                ts = 0
                message = msg
        else:
            # fallback
            ts = 0
            message = str(msg)

        self.chat_messages.append((ts, message))
        self.chat_messages.sort(key=lambda x: x[0])

        while len(self.chat_messages) > self.max_msg_count:
            self.chat_messages.pop(0)

    # -------------------- Input Handling --------------------
    def handle_event(self, event):
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN and self.active:
                msg = self.input_text.strip()
                self.input_text = ""
                return msg
            elif event.key == pg.K_BACKSPACE and self.active:
                self.input_text = self.input_text[:-1]
            elif self.active:
                self.input_text += event.unicode
        elif event.type == pg.MOUSEBUTTONDOWN:
            self.active = self.input_rect.collidepoint(event.pos)
        return None

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False

    def is_activated(self):
        return self.active
