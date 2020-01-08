"""
Some fixes to the toga_gtk framework - most should get contributed upstream
"""
from toga_gtk.libs import Gtk, Gdk
import toga_gtk.factory
from toga_gtk.factory import not_implemented

class Canvas(toga_gtk.factory.Canvas):
    def create(self):
        super().create()
        self.draw_done_futures = []
        self.__old_width = None
        self.__old_height = None
        self.__is_drawing = False

    def redraw(self):
        self.native.queue_draw()

    def gtk_draw_callback(self, canvas, gtk_context):
        new_width = self.native.get_allocated_width()
        new_height = self.native.get_allocated_height()
        if (
            new_width != self.__old_width \
            or new_height != self.__old_height
        ):
            if self.interface.on_resize:
                self.__is_drawing = True
                try:
                    self.interface.on_resize(self.interface)
                finally:
                    self.__is_drawing = False
            self.__old_width = new_width
            self.__old_height = new_height
        super().gtk_draw_callback(canvas, gtk_context)
        for future in self.draw_done_futures:
            future.set_result(True)
        self.draw_done_futures = []

    def set_on_resize(self, handler):
        pass

    def draw_done(self):
        future = self.interface.app._impl.loop.create_future()
        self.draw_done_futures.append(future)
        return future


class Button(toga_gtk.factory.Button):
    def __init__(self, *args, **kwargs):
        self._style_provider = None
        self._background_color = None
        super().__init__(*args, **kwargs)

    def create(self):
        super().create()
        self._set_background_color()

    def set_background_color(self, value):
        self._background_color = value
        self._set_background_color()

    def _set_background_color(self):
        if self.native is None:
            return
        if self._background_color is None:
            if self._style_provider is not None:
                style_context = self.native.get_style_context()
                style_context.remove_provider(self._style_provider)
                self._style_provider = None
            return
        if self._style_provider is None:
            self._style_provider = Gtk.CssProvider()
            style_context = self.native.get_style_context()
            style_context.add_provider(
                self._style_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
        self._style_provider.load_from_data(
            """
            * {{
                background-color: {};
                background-image: none;
            }}
            """.format(self._background_color).encode('utf8')
        )
