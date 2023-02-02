import sys

from typing import List

import pygame as pg
import pygame.freetype as ft

from pygame import Color
from pygame.locals import *

from stream import Stream
from wallpaper import get_wallpaper_filepath

class Matrix:
    FPS = 60
    MIN_MSECS = 0
    MAX_MSECS = 2048
    FONT_SIZE = 8
    BGCOLOR = Color('black')
    KATAKANA = [chr(int('0x30a0', 16) + c) for c in range(96)]
    MAX_FACTOR = 3.75
    MIN_FACTOR = 1.00
    MAX_COLOR = 255
    MIN_COLOR = 0
    DELTA_COLOR = 17
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
        self.wallpaper = self._get_wallpaper()
        self.streams = self._setup_streams()
        self._elapsed_msecs = pg.time.get_ticks()
        if Matrix.FULLSCREEN:
            pg.display.toggle_fullscreen()
            pg.mouse.set_visible(False)

    def run(self) -> None:
        while True:
            current_msecs = pg.time.get_ticks()
            delta_msecs = current_msecs - self._elapsed_msecs
            self._update(delta_msecs)
            for e in pg.event.get():
                self._handle_event(e)
            pg.display.flip()
            self.clock.tick(Matrix.FPS)
            self._elapsed_msecs = current_msecs

    def _setup_streams(self) -> List[Stream]:
        stream_cnt = self.screen.get_width() // Matrix.FONT_SIZE
        stream_len = self.screen.get_height() // Matrix.FONT_SIZE
        return [Stream(self, col, stream_len) for col in range(stream_cnt)]

    def _update(self, delta_msecs: float):
        self.surface.fill(Matrix.BGCOLOR)
        for s in self.streams:
            s.update(delta_msecs)
        self.screen.blit(self.surface, (0, 0))
        if not self.FULLSCREEN:
            pg.display.set_caption('FPS: {:.2f}'.format(self.clock.get_fps()))

    def _handle_event(self, event) -> None:
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            self._exit()

    def _get_wallpaper(self) -> pg.pixelarray.PixelArray:
        try:
            image = pg.image.load(get_wallpaper_filepath()).convert()
        except Exception:
            # Setup a green image as a fallback.
            # NOTE: Is `Color` bugged? Setting `(0, 160, 0)` or `'green'`
            #       stays black rather than green...
            image = pg.Surface(self.screen.get_size()).convert()
            image.fill(Color(160, 0, 160))
        image = pg.transform.scale(image, self.screen.get_size()).convert()
        return pg.pixelarray.PixelArray(image)

    def _exit(self):
        pg.quit()
        sys.exit(0)


if __name__ == '__main__':
    m = Matrix()
    m.run()
