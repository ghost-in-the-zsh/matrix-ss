from random import randrange, choice

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
        self.color = color if color else Color('black')
        self.limit = limit if limit else Color('black')

class Stream:
    def __init__(self, matrix, col_idx: int, len: int) -> None:
        self.app = matrix
        self.column = col_idx
        self.chars = [Char() for _ in range(len)]
        updates_limit = randrange(1, 17)
        self.char_delays = [
            randrange(matrix.MIN_MSECS, matrix.MAX_MSECS)
            for _ in range(updates_limit)
        ]
        self.char_indices = list(set([
            randrange(0, len)
            for _ in range(updates_limit)
        ]))

    def update(self, delta_msecs: int) -> None:
        # if self.char_delays <= 0:
        self.change_chars()
        self.render()
        # self.char_delays -= delta_msecs

    def change_chars(self) -> None:
        for i in range(len(self.char_indices)):
            self.change_char(self.char_indices[i])
            self.char_indices[i] = (self.char_indices[i] + 1) % len(self.chars)

    def change_char(self, idx: int) -> None:
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
        # self.app.on_stream_delay_update(self)

    def render(self) -> None:
        for row, char in enumerate(filter(lambda ch: ch.glyph, self.chars)):
            pos = (self.column * self.app.FONT_SIZE, row * self.app.FONT_SIZE)
            ch = self.chars[row]
            self.app.font.render_to(self.app.surface, pos, ch.glyph, fgcolor=ch.color)
            ch.color.r = max(ch.color.r - self.app.DELTA_COLOR, ch.limit.r)
            ch.color.g = max(ch.color.g - self.app.DELTA_COLOR, ch.limit.g)
            ch.color.b = max(ch.color.b - self.app.DELTA_COLOR, ch.limit.b)

