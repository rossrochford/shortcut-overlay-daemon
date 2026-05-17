import json
import subprocess


def get_active_app_id():
    """Fetches focused wm_class on GNOME (requires Window Calls Extension)."""
    try:
        cmd = [
            "gdbus", "call", "--session",
            "--dest", "org.gnome.Shell",
            "--print-reply=literal",
            "--object-path", "/org/gnome/Shell/Extensions/Windows",
            "--method", "org.gnome.Shell.Extensions.Windows.List"
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)

        windows = json.loads(res.stdout.strip())

        if not windows:
            return None  # Workspace is completely empty

        for win in windows:
            if win.get("has_focus") is True:
                wm_class = win.get("wm_class")
                if not wm_class or wm_class.strip() == "":
                    return "unlabelled_application"
                return wm_class

        return None  # Windows exist, but none have active focus

    except (subprocess.CalledProcessError, Exception):
        print("Failed to query active window via D-Bus. Ensure the 'Window Calls' Gnome extension is enabled.")
        return "error"
