import pygame as pg
import pygame.freetype
import numpy as np

from stream import Stream

class Matrix:
    FPS = 60
    MIN_DELAY = 1
    MAX_DELAY = 256
    FONT_SIZE = 8
    BGCOLOR = pg.Color('black')

    def __init__(self):
        pg.init()
        info = pg.display.Info()
        size = (info.current_w, info.current_h)
        self.screen = pg.display.set_mode(size)
        self.surface = pg.Surface(size)
        self.font = pg.freetype.Font('font/msmincho.ttf', Matrix.FONT_SIZE)
        self.clock = pg.time.Clock()
        self.streams = []
        self.stream_delays = [i for i in range(Matrix.MIN_DELAY, Matrix.MAX_DELAY)]
        self._setup_streams()
        self.elapsed_msecs = pg.time.get_ticks()
        pg.display.toggle_fullscreen()
        pg.mouse.set_visible(False)

    def _setup_streams(self):
        stream_cnt = self.screen.get_width() // Matrix.FONT_SIZE
        stream_len = self.screen.get_height() // Matrix.FONT_SIZE + 1
        [self.streams.append(Stream(self, col, stream_len)) for col in range(stream_cnt)]
        [self.on_stream_delay_update(s) for s in self.streams]

    def _update(self, delta_msecs: float):
        self.surface.fill(Matrix.BGCOLOR)
        [s.update(delta_msecs) for s in self.streams]
        self.screen.blit(self.surface, (0, 0))

    def run(self) -> None:
        while True:
            current_msecs = pg.time.get_ticks()
            delta_msecs = current_msecs - self.elapsed_msecs
            self._update(delta_msecs)
            [self._on_event(e) for e in pg.event.get()]
            pg.display.flip()
            self.clock.tick(Matrix.FPS)
            self.elapsed_msecs = current_msecs

    def on_stream_delay_update(self, stream: Stream):
        stream.delay_msecs = np.random.choice(self.stream_delays)

    def _on_event(self, event):
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
            self._exit()

    def _exit(self):
        pg.quit()
        raise SystemExit
