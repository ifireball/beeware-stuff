"""
Some fixes to the Toga framework - most should get contributed upstream
"""
import toga
from toga.handlers import wrapped_handler
from . import toga_gtk_fixes


class Canvas(toga.Canvas):
    def __init__(self, on_resize=None, **kwargs):
        kwargs['factory'] = toga_gtk_fixes
        super().__init__(**kwargs)

        self.on_resize = on_resize

    @property
    def on_resize(self):
        return self._on_resize

    @on_resize.setter
    def on_resize(self, handler):
        self._on_resize = wrapped_handler(self, handler)
        self._impl.set_on_resize(self._on_resize)

    async def draw_done(self):
        await self._impl.draw_done()


class Button(toga.Button):
    def __init__(self, *args, **kwargs):
        kwargs['factory'] = toga_gtk_fixes
        super().__init__(*args, **kwargs)
