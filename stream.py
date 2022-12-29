import pygame as pg
import numpy as np

class Stream:
    def __init__(self, matrix, col_idx: int, len: int) -> None:
        self.app = matrix
        self.column = col_idx
        self.chars = [''] * len
        # prevent the same color ref in all list entries
        self.colors = []
        for _ in range(len):
            self.colors.append(pg.Color(0, matrix.MAX_COLOR, 0))
        self.delay_msecs = 0
        self._char_idx = 0

    def update(self, delta_msecs: int) -> None:
        if self.delay_msecs <= 0:
            idx = self._char_idx
            self.chars[idx] = np.random.choice(self.app.KATAKANA)
            self.colors[idx].g = self.app.MAX_COLOR
            self._char_idx = (self._char_idx + 1) % len(self.chars)
            self.app.on_stream_delay_update(self)

        for row, char in enumerate(self.chars):
            pos = (self.column * self.app.FONT_SIZE, row * self.app.FONT_SIZE)
            self.app.font.render_to(self.app.surface, pos, char, fgcolor=self.colors[row])
            self.colors[row].g = max(self.colors[row].g - self.app.DELTA_COLOR, self.app.MIN_COLOR)

        self.delay_msecs -= delta_msecs
