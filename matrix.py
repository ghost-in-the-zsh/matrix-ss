import sys

import pygame as pg
import pygame.freetype as ft
import numpy as np

from stream import Stream

class Matrix:
    FPS = 30
    MIN_MSECS = 1
    MAX_MSECS = 256
    FONT_SIZE = 8
    BGCOLOR = pg.Color('black')
    KATAKANA = [chr(int('0x30a0', 16) + c) for c in range(96)]
    MIN_COLOR = 100
    MAX_COLOR = 255
    DELTA_COLOR = 5

    def __init__(self):
        pg.init()
        info = pg.display.Info()
        size = (info.current_w, info.current_h)
        self.screen = pg.display.set_mode(size)
        self.surface = pg.Surface(size)
        self.font = ft.Font('font/msmincho.ttf', Matrix.FONT_SIZE)
        self.clock = pg.time.Clock()
        self.streams = []
        self.stream_delays = [i for i in range(Matrix.MIN_MSECS, Matrix.MAX_MSECS)]
        self.setup_streams()
        self.elapsed_msecs = pg.time.get_ticks()
        pg.display.toggle_fullscreen()
        pg.mouse.set_visible(False)

    def run(self) -> None:
        while True:
            current_msecs = pg.time.get_ticks()
            delta_msecs = current_msecs - self.elapsed_msecs
            self.update(delta_msecs)
            [self.on_event(e) for e in pg.event.get()]
            pg.display.flip()
            self.clock.tick(Matrix.FPS)
            self.elapsed_msecs = current_msecs

    def add_stream(self, column: int, length: int) -> Stream:
        s = Stream(self, column, length)
        self.streams.append(s)
        return s

    def setup_streams(self):
        stream_cnt = self.screen.get_width() // Matrix.FONT_SIZE
        stream_len = self.screen.get_height() // Matrix.FONT_SIZE + 1
        [self.add_stream(col, stream_len) for col in range(stream_cnt)]
        [self.on_stream_delay_update(s) for s in self.streams]

    def update(self, delta_msecs: float):
        self.surface.fill(Matrix.BGCOLOR)
        [s.update(delta_msecs) for s in self.streams]
        self.screen.blit(self.surface, (0, 0))

    def on_stream_delay_update(self, stream: Stream):
        stream.delay_msecs = np.random.choice(self.stream_delays)

    def on_event(self, event):
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            self.exit()

    def exit(self):
        pg.quit()
        sys.exit(0)
