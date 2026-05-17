import os
from os.path import abspath
import gi

gi.require_version('Gtk', '3.0')
from gi.repository import GLib, Gtk, GdkPixbuf

from app_detection import detect_active_app_id
from overlay_display import Overlay
from utils import load_config, create_error_image_pixbuf


config = load_config()

PIPE_PATH = config['fifo_pipe_path']


# recreate fifo
if os.path.exists(PIPE_PATH):
    os.remove(PIPE_PATH)
os.mkfifo(PIPE_PATH)

fifo_fd = os.open(PIPE_PATH, os.O_RDONLY | os.O_NONBLOCK)


FALLBACK_APP_ID = config.get("fallback_app_id", "cosmic_desktop").lower()

output_dir = abspath(str(config['output']['output_dir']))


if os.path.exists(output_dir) is False or len(os.listdir(output_dir)) == 0:
    exit('\n❌ No shortcut images found, first run: "just render" \n')


overlay = Overlay()


def _map_app_id_to_image_filepath(config, app_id):
    image_filename = f"{app_id.lower().replace('.', '_')}.png"
    target_image_path = os.path.join(config['output']['output_dir'], image_filename)
    return abspath(target_image_path)


def resolve_overlay_image(config, detected_id):
    """ Load image file into a GdkPixbuf object if exists, otherwise generate an error image. """

    if detected_id == "error":
        return create_error_image_pixbuf(
            f"Error: Unable to query window manager state ({detected_id})."
        )
    if detected_id == "unlabelled_application":
        return create_error_image_pixbuf(
            f"App detected but it has no identifier string."
        )

    target_id = detected_id
    if target_id is None:
        target_id = FALLBACK_APP_ID

    image_filepath = _map_app_id_to_image_filepath(config, target_id)

    if not os.path.exists(image_filepath):
        if target_id == FALLBACK_APP_ID:
            return create_error_image_pixbuf(
                f"No active application detected, no image found for fallback_app_id '{FALLBACK_APP_ID}'"
            )
        else:
            return create_error_image_pixbuf(
                f'Overlay image not found for application id: "{target_id}" '
                f'\n\nEnsure a .shortcuts file exists with with app_id and run \'just render\' '
            )

    return GdkPixbuf.Pixbuf.new_from_file(image_filepath)


def check_fifo():
    """Polls the FIFO non-blockingly, driven seamlessly by the GLib Main Loop."""
    try:
        data = os.read(fifo_fd, 1024).decode().strip()
        if not data:
            return True  # Must return True so GLib keeps the timeout loop alive

        if overlay.get_visible():
            overlay.hide()
            return True

        app_id = detect_active_app_id()
        image_pixbuf = resolve_overlay_image(config, app_id)

        overlay.show_overlay(image_pixbuf)

    except (BlockingIOError, KeyboardInterrupt):
        pass

    return True  # Must return True so GLib keeps the timeout loop alive


GLib.timeout_add(100, check_fifo)
from gi.repository import Gtk
Gtk.main()