import os
import sys
import platform as pt

import pygame as pg
import pygame.freetype as ft

from random import randrange, choice

from pygame import Color
from pygame.locals import *
from stream import Stream

class Matrix:
    FPS = 60
    MIN_MSECS = 0
    MAX_MSECS = 384
    FONT_SIZE = 8
    BGCOLOR = Color('black')
    KATAKANA = [chr(int('0x30a0', 16) + c) for c in range(96)]
    MAX_FACTOR = 2.75
    MIN_FACTOR = 0.75
    MAX_COLOR = 255
    DELTA_COLOR = 7
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
            for e in pg.event.get():
                self.handle_event(e)
            pg.display.flip()
            self.clock.tick(Matrix.FPS)
            self.elapsed_msecs = current_msecs

    def setup_streams(self):
        stream_cnt = self.screen.get_width() // Matrix.FONT_SIZE
        stream_len = self.screen.get_height() // Matrix.FONT_SIZE
        self.streams = [Stream(self, col, stream_len) for col in range(stream_cnt)]

    def update(self, delta_msecs: float):
        self.surface.fill(Matrix.BGCOLOR)
        for s in self.streams: s.update(delta_msecs)
        self.screen.blit(self.surface, (0, 0))
        if not self.FULLSCREEN:
            pg.display.set_caption('FPS: {:.2f}'.format(self.clock.get_fps()))

    def handle_event(self, event) -> None:
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
