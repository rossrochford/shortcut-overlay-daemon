import json
import subprocess


'''
def get_active_app_id():
    try:
        result = subprocess.run(
            ['cosmic-ext-window-helper', 'state'],
            capture_output=True,
            text=True,
            check=True
        )
        windows = json.loads(result.stdout)
        for window in windows:
            if window.get("is_active"):
                return window.get("app_id")
    except Exception as e:
        print(f"Error fetching window state: {e}")
    return None
'''


def get_active_app_id():
    try:
        res = subprocess.run(
            ["cosmic-ext-window-helper", "state"],
            capture_output=True,
            text=True,
            check=True
        )
        windows = json.loads(res.stdout)

        if not windows:
            return None  # Genuinely nothing open

        for window in windows:
            if window.get("is_active") is True:
                app_id = window.get("app_id")

                if not app_id or app_id.strip() == "":
                    # An app is open, but it is missing an identifier string
                    return "unlabelled_application"

                return app_id

        return None  # Windows exist but not in this workspace

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f'Exception: {e}')
        return "error"
