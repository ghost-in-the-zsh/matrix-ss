'''The stream module.

A stream is a single column of text on the screen. Each stream has one or
more "trails". A trail is defined by the character being drawn within the
stream, being brightest when drawn and dimming out with time.
'''

from dataclasses import dataclass
from random import randrange, choice

from pygame import Color

class _Char:
    '''Character data including glyph and colors.'''
    def __init__(
        self,
        glyph: str=None,    # the symbol to render
        color: Color=None,  # color to use when rendering the glyph
        limit: Color=None   # lower bound on how dim to make the rendering color
    ) -> None:
        self.glyph = glyph
        self.color = color if color else Color('black')
        self.limit = limit if limit else Color('black')

@dataclass
class _Time:
    delay: int=0    # how long to wait before rendering a char, in msec
    accum: int=0    # how long has passed since we started waiting, in msec

    def update(self, msecs: int) -> None:
        self.accum += msecs

    def reset(self, delay: int) -> None:
        self.delay = delay
        self.accum = 0

    def has_expired(self) -> bool:
        return self.accum >= self.delay

@dataclass
class _Trail:
    idx: int=0  # "head" index within stream
    time: _Time=None

class Stream:
    def __init__(self, matrix, col_idx: int, length: int) -> None:
        # _column: screen column index
        # _chars : list of characters to be rendered
        # _trails: list of stream indices where trail "heads" are to be rendered
        # length : how long this stream column is (in chars)
        self._app = matrix
        self._column = col_idx
        self._chars = [_Char() for _ in range(length)]
        max_trails = randrange(1, 3)
        stream_indices = list({randrange(0, length) for _ in range(max_trails)})
        trail_count = len(stream_indices)
        self._trails = [_Trail(
            stream_indices[i],
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
            self._app.font.render_to(self._app.surface, pos, char.glyph, fgcolor=char.color)
            char.color.r = max(char.color.r - self._app.DELTA_COLOR, char.limit.r)
            char.color.g = max(char.color.g - self._app.DELTA_COLOR, char.limit.g)
            char.color.b = max(char.color.b - self._app.DELTA_COLOR, char.limit.b)
