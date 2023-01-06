from random import choice

import pygame as pg

Color = pg.Color

class Char:
    def __init__(
        self,
        glyph: str='',
        color: Color=None,
        limit: Color=None
    ) -> None:
        self.glyph = glyph
        self.color = color if color else Color(0, 0, 0)
        self.limit = limit if limit else Color(0, 0, 0)

class Stream:
    def __init__(self, matrix, col_idx: int, len: int) -> None:
        self.app = matrix
        self.column = col_idx
        self.chars = [Char() for _ in range(len)]
        self.delay_msecs = 0
        self._char_idx = 0

    def update(self, delta_msecs: int) -> None:
        if self.delay_msecs <= 0:
            self.change_char()
        self.render()
        self.delay_msecs -= delta_msecs

    def change_char(self) -> None:
        idx = self._char_idx
        pos = (self.column * self.app.FONT_SIZE, idx * self.app.FONT_SIZE)
        ch = self.chars[idx]
        ch.glyph = choice(self.app.KATAKANA)
        ch.color = Color(self.app.wallpaper[pos])
        ch.limit.r = max(round(ch.color.r * self.app.MIN_FACTOR), self.app.MIN_COLOR)
        ch.limit.g = max(round(ch.color.g * self.app.MIN_FACTOR), self.app.MIN_COLOR)
        ch.limit.b = max(round(ch.color.b * self.app.MIN_FACTOR), self.app.MIN_COLOR)
        ch.color.r = min(round(ch.color.r * self.app.MAX_FACTOR), self.app.MAX_COLOR)
        ch.color.g = min(round(ch.color.g * self.app.MAX_FACTOR), self.app.MAX_COLOR)
        ch.color.b = min(round(ch.color.b * self.app.MAX_FACTOR), self.app.MAX_COLOR)
        self._char_idx = (self._char_idx + 1) % len(self.chars)
        self.app.on_stream_delay_update(self)

    def render(self) -> None:
        for row, char in enumerate(filter(lambda ch: ch.glyph, self.chars)):
            pos = (self.column * self.app.FONT_SIZE, row * self.app.FONT_SIZE)
            ch = self.chars[row]
            self.app.font.render_to(self.app.surface, pos, ch.glyph, fgcolor=ch.color)
            ch.color.r = max(ch.color.r - self.app.DELTA_COLOR, ch.limit.r)
            ch.color.g = max(ch.color.g - self.app.DELTA_COLOR, ch.limit.g)
            ch.color.b = max(ch.color.b - self.app.DELTA_COLOR, ch.limit.b)

