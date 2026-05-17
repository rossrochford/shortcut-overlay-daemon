import json
import subprocess


def get_active_app_id():
    """Fetches focused class on Hyprland Compositors."""
    try:
        res = subprocess.run(
            ["hyprctl", "activewindow", "-j"],
            capture_output=True,
            text=True,
            check=True
        )
        data = json.loads(res.stdout)

        # If the JSON object is empty or missing keys entirely, nothing is open
        if not data or "class" not in data:
            return None

        app_class = data.get("class", "").strip()
        if app_class == "":
            return None  # Genuinely nothing open on the workspace

        if app_class.lower() == "unknown":
            return "unlabelled_application"

        return app_class

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return "error"
