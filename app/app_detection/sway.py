import json
import subprocess


def get_active_app_id():
    """Crawls Sway/i3 layout trees to find focused node identifiers."""
    try:
        res = subprocess.run(
            ["swaymsg", "-t", "get_tree"],
            capture_output=True,
            text=True,
            check=True
        )
        tree = json.loads(res.stdout)

        # Use a container class instance variable to bypass recursive scope assignment limits
        tracking = {"found_focused": False, "app_id": None}

        def find_focused(node):
            if node.get("focused") is True:
                tracking["found_focused"] = True
                # Wayland native apps prioritize app_id, XWayland relies on class properties
                tracking["app_id"] = node.get("app_id") or node.get("window_properties", {}).get("class")
                return None

            for child in node.get("nodes", []) + node.get("floating_nodes", []):
                find_focused(child)
                if tracking["found_focused"]:
                    return None

        find_focused(tree)

        if not tracking["found_focused"]:
            return None  # Genuinely nothing open or focused in the entire environment tree

        final_id = tracking["app_id"]
        if not final_id or final_id.strip() == "":
            return "unlabelled_application"

        return final_id

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return "error"
