"""
Small app for displaying 3D shapes
"""
from functools import partial
from math import pi
import numpy as np
from time import time
import asyncio

import toga
from . import toga_fixes
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER, BOTTOM
from toga.colors import rgb
from travertino.size import at_least

from . import transforms as tr
from . import models

class Shapes(toga.App):
    home_z_rotation = pi / 8
    home_x_rotation = pi / 4.5

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self._draw_color = rgb(0, 0, 128)
        self._draw_shape = models.box()
        self._z_rotation = self.home_z_rotation
        self._x_rotation = self.home_x_rotation
        self._z_speed = 0
        self._x_speed = 0
        self._animating = False

        self.canvas = toga_fixes.Canvas(
            style=Pack(flex=1),
            on_resize=self.render_event
        )
        self.canvas.intrinsic = \
            Pack.IntrinsicSize(width=at_least(50), height=at_least(50))

        self.main_box = toga.Box(style=Pack(direction=ROW), children=[
            self.canvas,
            toga.Box(style=Pack(direction=COLUMN, padding=5), children=[
                self.make_shapes_box(),
                self.make_colors_box(),
                self.make_motion_box(),
                self.make_fps_box()
            ]),
        ])

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def make_colors_box(self):
        color_buttons = [
            toga_fixes.Button(
                '', on_press=partial(self.set_draw_color, color=color),
                style=Pack(background_color=color, width=34, height=34),
            )
            for color in (
                rgb(rval + intensity, gval + intensity, bval + intensity)
                for intensity in (0, 127)
                for rval in (0, 128)
                for gval in (0, 128)
                for bval in (0, 128)
            )
        ]
        return toga.Box(
            style=Pack(direction=COLUMN, padding=(5,0)),
            children=[
                toga.Box(
                    style=Pack(direction=ROW),
                    children=color_buttons[chunk:chunk+4]
                )
                for chunk in range(0, len(color_buttons), 4)
            ]
        )

    def make_shapes_box(self):
        shape_buttons = [
            toga.Button(
                'Rect',
                on_press=partial(self.set_draw_shape, shape=self.rect),
                style=Pack(width=68, height=68)
            ),
            toga.Button(
                'Ellipse',
                on_press=partial(self.set_draw_shape, shape=self.ellipse),
                style=Pack(width=68, height=68)
            ),
        ]
        return toga.Box(
            style=Pack(direction=ROW),
            children=shape_buttons
        )

    def make_motion_box(self):
        motions = [
            ('up', '\u25B2', 46),
            ('left', '\u25C0', 45),
            ('stop', '\u25A0', 46),
            ('right', '\u25B6', 45),
            ('down', '\u25BC', 45),
            ('home', 'Home', 132),
        ]
        buttons = [
            toga.Button(
                symbol, on_press=async_partial(self.motion, direction=direction),
                style=Pack(width=width, height=46)
            )
            for direction, symbol, width in motions
        ]
        return toga.Box(
            style=Pack(direction=COLUMN, alignment=CENTER),
            children=[
                buttons[0],
                toga.Box(style=Pack(direction=ROW), children=buttons[1:4]),
                buttons[4],
                buttons[5],
            ]
        )

    def make_fps_box(self):
        self._fps_display = toga.Label('0 FPS', style=Pack(
            text_align=CENTER, width=132, height=30
        ))
        return toga.Box(
            style=Pack(direction=COLUMN, alignment=BOTTOM, flex=1),
            children=[
                toga.Box(style=Pack(flex=1)),
                self._fps_display,
            ],
        )

    async def motion(self, widget, direction):
        if direction == 'home':
            self._z_rotation = self.home_z_rotation
            self._x_rotation = self.home_x_rotation
            self._x_speed = 0
            self._z_speed = 0
            self._animating = False
            self.render()
            return
        elif direction == 'stop':
            self._x_speed = 0
            self._z_speed = 0
            self._animating = False
            return
        elif direction == 'up':
            self._x_speed = min(self._x_speed + pi/72, pi)
        elif direction == 'down':
            self._x_speed = max(self._x_speed - pi/72, -pi)
        elif direction == 'left':
            self._z_speed = min(self._z_speed + pi/72, pi)
        elif direction == 'right':
            self._z_speed = max(self._z_speed - pi/72, -pi)
        if self._x_speed == 0 and self._z_speed == 0:
            self._animating = False
            return
        self._start_x_rot = self._x_rotation
        self._start_z_rot = self._z_rotation
        self._start_time = time()
        if self._animating:
            return
        self._animating = True
        fps_time = time()
        fps_cnt = 0
        while self._animating:
            time_passed = time() - self._start_time
            self._x_rotation = (self._start_x_rot + self._x_speed * time_passed) % (2 * pi)
            self._z_rotation = (self._start_z_rot + self._z_speed * time_passed) % (2 * pi)
            self.render()
            await self.canvas.draw_done()
            fps_cnt += 1
            now = time()
            if now - fps_time >= 1.:
                self._fps_display.text = '{:.2f} FPS'.format(fps_cnt/(now - fps_time))
                fps_time = now
                fps_cnt = 0
        print('animation stopped')

    def set_draw_color(self, widget, color):
        self._draw_color = color
        self.render()

    def render_event(self, widget):
        self.render()

    def render(self):
        cw = self.canvas.layout.content_width
        ch = self.canvas.layout.content_height

        vertices = self._draw_shape.vertices
        vertices = vertices @ tr.rotate_z(self._z_rotation)
        vertices = vertices @ tr.rotate_x(self._x_rotation)
        vertices = vertices @ tr.move(0, 5)
        vertices = tr.perspective(vertices, 2)
        vertices = vertices @ tr.scale(cw/2, cw/2, -cw/2)
        vertices = vertices @ tr.move(cw/2, 0, ch/2)

        self.canvas.clear()
        with self.canvas.fill(color='white') as fill:
            fill.rect(x=0, y=0, width=cw, height=ch)
        for f in self._draw_shape.faces:
            edge1 = np.delete(vertices[f[1]] - vertices[f[0]], 3)
            edge2 = np.delete(vertices[f[2]] - vertices[f[1]], 3)
            normal = np.cross(edge1, edge2)
            if normal[1] < 0:
                continue

            with self.canvas.stroke(color='black', line_width=4.0) as stroke:
                with stroke.fill(color=self._draw_color, preserve=True) as fill:
                    fill.move_to(vertices[f[0]][0], vertices[f[0]][2])
                    for v in f[1:]:
                        fill.line_to(vertices[v][0], vertices[v][2])
                    fill.line_to(vertices[f[0]][0], vertices[f[0]][2])

        self.canvas.redraw()

    def rect(self, context, w, h):
        context.rect(x=w / 4, y=h / 4, width=w / 2, height=h / 2)

    def ellipse(self, context, w, h):
        context.ellipse(x=w/2, y=h/2, radiusx=w/4, radiusy=h/4)

    def set_draw_shape(self, widget, shape):
        # self._draw_shape = shape
        # self.render()
        pass

# this is needed because 'partial' does not work well on async functions until
# Python 3.8
def async_partial(func, *args, **kwargs):
    async def _newfunc(*nargs, **nkwargs):
        kwargs.update(nkwargs)
        return await func(*args, *nargs, **kwargs)
    return _newfunc


def main():
    return Shapes()
