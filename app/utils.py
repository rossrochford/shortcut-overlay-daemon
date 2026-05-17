import yaml
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GtkLayerShell", "0.1")

import cairo
from gi.repository import Gtk, Gdk, GdkPixbuf, GtkLayerShell
from gi.repository import GdkPixbuf, Gdk

from PIL import Image


def load_config():
    with open("config.yaml", "r") as f:
        return yaml.safe_load(f)



def create_error_image_pixbuf(text: str):
    # Set dimensions (match your usual shortcut width)
    width, height = 650, 150

    # 1. Create a Cairo surface in memory (Alpha channel included)
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # 2. Draw a semi-transparent dark background
    ctx.set_source_rgba(0.1, 0.1, 0.1, 0.8)  # Dark grey, 80% opaque
    ctx.rectangle(0, 0, width, height)
    ctx.fill()

    # 3. Draw a border
    ctx.set_source_rgba(0.8, 0.2, 0.2, 1.0)  # Red border
    ctx.set_line_width(2)
    ctx.rectangle(1, 1, width - 2, height - 2)
    ctx.stroke()

    # 4. Draw the Text
    ctx.set_source_rgb(1, 1, 1)  # White text
    ctx.select_font_face("Sans", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(18)

    # Simple multi-line text centering
    for i, line in enumerate(text.split('\n')):
        extents = ctx.text_extents(line)
        x = (width / 2) - (extents.width / 2)
        y = (height / 2) + (i * 25) - 10  # Offset each line
        ctx.move_to(x, y)
        ctx.show_text(line)

    # 5. Convert Cairo surface to GdkPixbuf
    # This is the "Image in memory" GTK understands
    return Gdk.pixbuf_get_from_surface(surface, 0, 0, width, height)
