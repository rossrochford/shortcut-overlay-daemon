import subprocess


def get_active_app_id():
    """Legacy catch-all tracker using xdotool window queries."""
    try:
        # Step 1: Check if a focused window handle even exists
        focus_res = subprocess.run(["xdotool", "getwindowfocus"], capture_output=True, text=True)
        if focus_res.returncode != 0:
            return None  # Nothing open or focused on the desktop layout layer

        window_id = focus_res.stdout.strip()
        if not window_id or window_id == "0":
            return None

        # Step 2: Grab the class string for that verified window handle
        class_res = subprocess.run(["xdotool", "getwindowclassname", window_id], capture_output=True, text=True,
                                   check=True)
        app_class = class_res.stdout.strip()

        if not app_class or app_class == "":
            return "unlabelled_application"

        return app_class

    except (subprocess.CalledProcessError, FileNotFoundError):
        # If xdotool isn't installed or fails internally, return system error
        return "error"
