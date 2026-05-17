import subprocess


def get_active_app_id():
    """Fetches focused window via KWin DBus interfaces."""
    try:
        cmd = ["qdbus", "org.kde.KWin", "/KWin", "org.kde.KWin.activeWindow"]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        window_id = res.stdout.strip()

        # If the returned window descriptor string is empty, nothing is open
        if not window_id or window_id == "" or "null" in window_id.lower():
            return None

        # Parse the app identifier out of the object path/descriptor
        app_id = window_id.split()[-1].lower()
        if not app_id or app_id.strip() == "" or app_id == "unknown":
            return "unlabelled_application"

        return app_id

    except (subprocess.CalledProcessError, FileNotFoundError):
        return "error"
