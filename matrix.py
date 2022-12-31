import os
import sys
import platform as pt

import pygame as pg
import pygame.freetype as ft
import numpy as np

from random import randrange, choice

from pygame.locals import *
from stream import Stream

Color = pg.Color

class Matrix:
    FPS = 60
    MIN_MSECS = 0
    MAX_MSECS = 384
    FONT_SIZE = 8
    BGCOLOR = Color('black')
    KATAKANA = [chr(int('0x30a0', 16) + c) for c in range(96)]
    MAX_FACTOR = 2.75
    MIN_FACTOR = 0.50
    MAX_COLOR = 255
    MIN_COLOR = 64
    DELTA_COLOR = 10
    FULLSCREEN = True

    def __init__(self):
        pg.init()
        pg.event.set_allowed([QUIT, KEYDOWN])
        info = pg.display.Info()
        size = (info.current_w, info.current_h)
        self.screen = pg.display.set_mode(size)
        self.surface = pg.Surface(size)
        self.font = ft.Font('font/msmincho.ttf', Matrix.FONT_SIZE)
        self.clock = pg.time.Clock()
        self.wallpaper = self.get_wallpaper()
        self.streams = []
        self.stream_delays = []
        self.setup_streams()
        self.elapsed_msecs = pg.time.get_ticks()
        if Matrix.FULLSCREEN:
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
        stream_len = self.screen.get_height() // Matrix.FONT_SIZE
        self.stream_delays = [
            randrange(Matrix.MIN_MSECS, Matrix.MAX_MSECS)
            for _ in range(stream_cnt)
        ]
        [self.add_stream(col, stream_len) for col in range(stream_cnt)]
        [self.on_stream_delay_update(s) for s in self.streams]

    def update(self, delta_msecs: float):
        self.surface.fill(Matrix.BGCOLOR)
        [s.update(delta_msecs) for s in self.streams]
        self.screen.blit(self.surface, (0, 0))
        if not self.FULLSCREEN:
            pg.display.set_caption('FPS: {:.2f}'.format(self.clock.get_fps()))

    def on_stream_delay_update(self, stream: Stream) -> None:
        stream.delay_msecs = choice(self.stream_delays)

    def on_event(self, event) -> None:
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            self.exit()

    def get_wallpaper(self) -> pg.pixelarray.PixelArray:
        sys = pt.system()
        if sys == 'Linux':
            # TODO: check distro, gnome/kde, subprocess command to get wallpaper
            image_path = f'{os.path.expanduser("~")}/Pictures/nier_automata/2b_closeup_ingame.jpg'
        elif sys == 'Windows':
            # check if 7, 10, etc
            raise NotImplementedError
        else:
            # not supported or unknown
            raise NotImplementedError

        image = pg.image.load(image_path)
        image = pg.transform.scale(image, self.screen.get_size()).convert()
        return pg.pixelarray.PixelArray(image)

    def exit(self):
        pg.quit()
        sys.exit(0)
