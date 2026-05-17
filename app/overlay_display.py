from typing import Optional
import gi
import os

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf, GtkLayerShell
from gi.repository import GdkPixbuf, Gdk

from PIL import Image
import io


OPACITY = 1


class Overlay(Gtk.Window):

    def __init__(self):
        super().__init__()

        #self.image_path = image_path
        self.image = Gtk.Image()

        # add frame (for border)
        self.frame = Gtk.Frame()
        self.frame.add(self.image)
        self.add(self.frame)

        # add CSS for frame border
        provider = Gtk.CssProvider()
        provider.load_from_data(b"""
        frame {
            border: 2px solid grey;
        }
        """)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        GtkLayerShell.init_for_window(self)

        GtkLayerShell.set_layer(self, GtkLayerShell.Layer.TOP)

        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.BOTTOM, True)
        GtkLayerShell.set_anchor(self, GtkLayerShell.Edge.RIGHT, True)

        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.BOTTOM, 50)
        GtkLayerShell.set_margin(self, GtkLayerShell.Edge.RIGHT, 10)

        GtkLayerShell.set_keyboard_mode(
            self,
            GtkLayerShell.KeyboardMode.NONE
        )

        if 0 <= OPACITY < 1.0:
            self._enable_opacity()

        self.set_app_paintable(True)
        self.hide()

        #self.update_image(self.image_path)
        #self.show_all()

    def _enable_opacity(self):
        self.set_app_paintable(True)
        self.set_opacity(OPACITY)
        screen = self.get_screen()
        rgba = screen.get_rgba_visual()
        if rgba is not None:
            self.set_visual(rgba)

    @staticmethod
    def load_retina_image(file_path):
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(file_path)

        target_width = int(pixbuf.get_width() * 0.25)
        target_height = int(pixbuf.get_height() * 0.25)

        return pixbuf.scale_simple(  # 'HYPER' interpolation for maximum sharpness
            target_width,
            target_height,

            #GdkPixbuf.InterpType.BILINEAR
            GdkPixbuf.InterpType.HYPER
        )

    @staticmethod
    def load_retina_image_with_pillow(file_path):
        # Load image with Pillow
        img = Image.open(file_path)

        # Downscale to 50%
        target_size = (
            img.width // 2,
            img.height // 2
        )

        # Try BICUBIC first for UI/text screenshots
        img = img.resize(
            target_size,
            #Image.Resampling.BICUBIC
            Image.Resampling.LANCZOS
        )

        # Convert Pillow image -> GdkPixbuf
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")

        loader = GdkPixbuf.PixbufLoader.new_with_type("png")
        loader.write(buffer.getvalue())
        loader.close()

        return loader.get_pixbuf()

    def update_image(self, image_path, app_id: Optional[str]=None):
        if not os.path.exists(image_path):
            if app_id is None:
                return  # Fail silently
            pixbuf = create_error_image_pixbuf(app_id)
            self.image.set_from_pixbuf(pixbuf)
            return

        self.image_path = image_path
        pixbuf = GdkPixbuf.Pixbuf.new_from_file(self.image_path)
        #pixbuf = self.load_retina_image(image_path)

        self.image.set_from_pixbuf(pixbuf)

    def show_overlay_old_version(self, image_path, app_id):
        self.update_image(image_path, app_id=app_id)
        self.show_all()
        # print("window scale:", self.get_scale_factor())
        # print("image scale:", self.image.get_scale_factor())

    def show_overlay(self, pix_buf: GdkPixbuf):
        self.image.set_from_pixbuf(pix_buf)
        self.show_all()

    # def toggle(self, image_path, app_id=None):
    #     if self.get_visible():
    #         self.hide()
    #         return
    #
    #     self.update_image(image_path, app_id=app_id)
    #     self.show_all()


        '''
        # deprecated, removed from update_image()
        if SCALE != 100:
            scale = SCALE / 100.0
            width = pixbuf.get_width()
            height = pixbuf.get_height()
            pixbuf = pixbuf.scale_simple(
                int(width * scale),
                int(height * scale),
                GdkPixbuf.InterpType.BILINEAR
            )
        '''
