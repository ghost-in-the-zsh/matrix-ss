from random import randrange, choice

import pygame as pg
from pygame import Color

class _Char:
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
    def __init__(self, matrix, col_idx: int, length: int) -> None:
        self._app = matrix
        self._column = col_idx
        self._chars = [_Char() for _ in range(length)]
        updates_limit = randrange(1, 5)
        self._char_delays = [
            randrange(matrix.MIN_MSECS, matrix.MAX_MSECS)
            for _ in range(updates_limit)
        ]
        self._char_indices = list(set([
            randrange(0, length)
            for _ in range(updates_limit)
        ]))

    def update(self, delta_msecs: int) -> None:
        self._update_trails(delta_msecs)
        self._render()

    def _update_trails(self, delta_msecs: int) -> None:
        for i in range(len(self._char_indices)):
            self._char_delays[i] -= delta_msecs
            if self._char_delays[i] <= 0:
                self._change_char(self._char_indices[i])
                self._char_indices[i] = (self._char_indices[i] + 1) % len(self._chars)
                self._char_delays[i] = randrange(self._app.MIN_MSECS, self._app.MAX_MSECS)

    def _change_char(self, idx: int) -> None:
        pos = (self._column * self._app.FONT_SIZE, idx * self._app.FONT_SIZE)
        ch = self._chars[idx]
        ch.glyph = choice(self._app.KATAKANA)
        ch.color = Color(self._app.wallpaper[pos])
        ch.limit.r = max(round(ch.color.r * self._app.MIN_FACTOR), self._app.MIN_COLOR)
        ch.limit.g = max(round(ch.color.g * self._app.MIN_FACTOR), self._app.MIN_COLOR)
        ch.limit.b = max(round(ch.color.b * self._app.MIN_FACTOR), self._app.MIN_COLOR)
        ch.color.r = min(round(ch.color.r * self._app.MAX_FACTOR), self._app.MAX_COLOR)
        ch.color.g = min(round(ch.color.g * self._app.MAX_FACTOR), self._app.MAX_COLOR)
        ch.color.b = min(round(ch.color.b * self._app.MAX_FACTOR), self._app.MAX_COLOR)

    def _render(self) -> None:
        for row, char in enumerate(filter(lambda ch: ch.glyph, self._chars)):
            pos = (self._column * self._app.FONT_SIZE, row * self._app.FONT_SIZE)
            ch = self._chars[row]
            self._app.font.render_to(self._app.surface, pos, ch.glyph, fgcolor=ch.color)
            ch.color.r = max(ch.color.r - self._app.DELTA_COLOR, ch.limit.r)
            ch.color.g = max(ch.color.g - self._app.DELTA_COLOR, ch.limit.g)
            ch.color.b = max(ch.color.b - self._app.DELTA_COLOR, ch.limit.b)
