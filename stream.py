from dataclasses import dataclass
from random import randrange, choice

import pygame as pg
from pygame import Color

class _Char:
    def __init__(
        self,
        glyph: str=None,
        color: Color=None,
        limit: Color=None
    ) -> None:
        self.glyph = glyph
        self.color = color if color else Color('black')
        self.limit = limit if limit else Color('black')

@dataclass
class _Time:
    delay: int=0    # in milliseconds
    accum: int=0    # in milliseconds

    def update(self, msecs: int) -> None:
        self.accum += msecs

    def reset(self, delay: int) -> None:
        self.delay = delay
        self.accum = 0

    def has_expired(self) -> bool:
        return self.accum >= self.delay

@dataclass
class _Trail:
    idx: int=0  # stream index
    time: _Time=None

class Stream:
    def __init__(self, matrix, col_idx: int, length: int) -> None:
        self._app = matrix
        self._column = col_idx
        self._chars = [_Char() for _ in range(length)]
        max_trails = randrange(1, 3)
        trail_indices = list(set([randrange(0, length) for _ in range(max_trails)]))
        trail_count = len(trail_indices)
        self._trails = [_Trail(
            trail_indices[i],
            _Time(randrange(matrix.MIN_MSECS, matrix.MAX_MSECS))
        ) for i in range(trail_count)]

    def update(self, delta_msecs: int) -> None:
        self._update_trails(delta_msecs)
        self._render()

    def _update_trails(self, delta_msecs: int) -> None:
        for i in range(len(self._trails)):
            self._trails[i].time.update(delta_msecs)
            if self._trails[i].time.has_expired():
                self._update_char(self._trails[i].idx)
                self._trails[i].idx = (self._trails[i].idx + 1) % len(self._chars)
                if self._trails[i].idx == 0:
                    delay = randrange(self._app.MIN_MSECS, self._app.MAX_MSECS)
                    self._trails[i].time.reset(delay)

    def _update_char(self, idx: int) -> None:
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
