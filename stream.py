from dataclasses import dataclass
from random import randrange, choice

import pygame as pg
from pygame import Color

@dataclass
class _RGB:
    '''Simple data class for RGB color values.

    This class takes takes up less space than `pygame.Color` instances
    and is more self-documenting than a tuple. It's also hashable.
    '''
    r: int=0
    g: int=0
    b: int=0

    def __eq__(self, other) -> bool:
        return (self.r == other.r) and (self.g == other.g) and (self.b == other.b)

    def __hash__(self) -> int:
        return hash(self.r) ^ hash(self.g) ^ hash(self.b)

@dataclass
class _Time:
    delay: int=0
    accum: int=0

class Stream:
    def __init__(self, matrix, col_idx: int, length: int) -> None:
        self.app = matrix
        self.column = col_idx
        self.length = length
        self.glyphs = [None] * length
        self.colors = [None] * length
        glyph_count = randrange(1, 5)
        self.delays = [
            _Time(randrange(matrix.MIN_MSECS, matrix.MAX_MSECS), 0)
            for _ in range(glyph_count)
        ]
        self.trails = list(set([
            randrange(0, length)
            for _ in range(glyph_count)
        ]))
        self.fonts_cache = {}
        self._prerender_fonts(length)

    def update(self, delta_msecs: int) -> None:
        self._update_trails(delta_msecs)
        self._render()

    def _update_trails(self, delta_msecs: float) -> None:
        for i in range(len(self.trails)):
            self.delays[i].accum += delta_msecs
            if self.delays[i].accum >= self.delays[i].delay:
                self._update_glyph(self.trails[i])
                self.trails[i] = (self.trails[i] + 1) % self.length
                if self.trails[i] == 0:
                    # char trails get new delays when they start over at the top
                    self.delays[i].delay = randrange(self.app.MIN_MSECS, self.app.MAX_MSECS)
                    self.delays[i].accum = 0

    def _update_glyph(self, i: int) -> None:
        pos = (self.column * self.app.FONT_SIZE, i * self.app.FONT_SIZE)
        color = Color(self.app.wallpaper[pos])
        max_rgb = (
            min(round(color.r * self.app.MAX_FACTOR), self.app.MAX_COLOR),
            min(round(color.g * self.app.MAX_FACTOR), self.app.MAX_COLOR),
            min(round(color.b * self.app.MAX_FACTOR), self.app.MAX_COLOR),
        )
        glyph = choice(self.app.KATAKANA)
        self.glyphs[i] = glyph
        self.colors[i] = _RGB(max_rgb[0], max_rgb[1], max_rgb[2])

    def _render(self) -> None:
        for row, glyph in enumerate(self.glyphs):
            if not glyph: continue
            pos = (self.column * self.app.FONT_SIZE, row * self.app.FONT_SIZE)
            curr = self.colors[row]
            font = self.fonts_cache[glyph][(curr.r, curr.g, curr.b)][0]
            self.app.surface.blit(font, pos)
            next = _RGB(
                max(curr.r - self.app.DELTA_COLOR, 0),
                max(curr.g - self.app.DELTA_COLOR, 0),
                max(curr.b - self.app.DELTA_COLOR, 0)
            )
            if next in self.fonts_cache[glyph]:
                self.colors[self.trails[row]] = next

    def _prerender_fonts(self, stream_len: int) -> None:
        for glyph in self.app.KATAKANA:
            self.fonts_cache[glyph] = {}
            for i in range(stream_len):
                j = (self.column * self.app.FONT_SIZE, i * self.app.FONT_SIZE)
                mi = Color(self.app.wallpaper[j])
                hi = Color(
                    min(round(mi.r * self.app.MAX_FACTOR), self.app.MAX_COLOR),
                    min(round(mi.g * self.app.MAX_FACTOR), self.app.MAX_COLOR),
                    min(round(mi.b * self.app.MAX_FACTOR), self.app.MAX_COLOR)
                )
                lo = Color(
                    round(mi.r * self.app.MIN_FACTOR),
                    round(mi.g * self.app.MIN_FACTOR),
                    round(mi.b * self.app.MIN_FACTOR)
                )
                self.colors[i] = _RGB(hi.r, hi.g, hi.b)
                while hi != lo:
                    self.fonts_cache[glyph][(hi.r, hi.g, hi.b)] = self.app.font.render(
                        glyph,
                        fgcolor=hi,
                        bgcolor=self.app.BGCOLOR
                    )
                    hi.r = max(hi.r - self.app.DELTA_COLOR, lo.r)
                    hi.g = max(hi.g - self.app.DELTA_COLOR, lo.g)
                    hi.b = max(hi.b - self.app.DELTA_COLOR, lo.b)

