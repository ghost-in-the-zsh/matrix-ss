import pygame as pg
import pygame.freetype
import numpy as np

class Stream:
    KATAKANA = [chr(int('0x30a0', 16) + c) for c in range(96)]

    def __init__(self, matrix, col_idx: int, len: int) -> None:
        self.app = matrix
        self.column = col_idx
        self.chars = [''] * len
        self.delay_msecs = 0
        self._char_idx = 0

    def update(self, delta_msecs: float):
        if self.delay_msecs <= 0:
            self.chars[self._char_idx] = np.random.choice(Stream.KATAKANA)
            self._char_idx = (self._char_idx + 1) % len(self.chars)
            self.app.on_stream_delay_update(self)

        for row, char in enumerate(self.chars):
            pos = (self.column * self.app.FONT_SIZE, row * self.app.FONT_SIZE)
            self.app.font.render_to(self.app.surface, pos, char, fgcolor=(0, 220, 0))

        self.delay_msecs -= delta_msecs
