import os
import shutil

from app_detection import cosmic, gnome, kde, hyprland, sway, x11_fallback


def _which(binary_name):
    answer = shutil.which(binary_name)
    if answer is False:
        print(f"warning: binary '{binary_name}' missing")
    return answer


def _detect_active_app_id():
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").upper()
    has_wayland = os.environ.get("WAYLAND_DISPLAY") is not None

    if "COSMIC" not in desktop:
        print('warning: get_active_app_id() is untested for your desktop environment')

    if "COSMIC" in desktop:
        return cosmic.get_active_app_id()

    elif "HYPRLAND" in desktop and _which("hyprctl"):
        return hyprland.get_active_app_id()

    elif "SWAY" in desktop and _which("swaymsg"):
        return sway.get_active_app_id()

    elif "GNOME" in desktop:
        return gnome.get_active_app_id()

    elif "KDE" in desktop or "PLASMA" in desktop:
        return kde.get_active_app_id()

    elif not has_wayland and _which("xdotool"):
        return x11_fallback.get_active_app_id()

    return "error"


def detect_active_app_id():
    app_id = _detect_active_app_id()
    if isinstance(app_id, str):  # ensure lowercase
        app_id = app_id.lower()
    return app_id