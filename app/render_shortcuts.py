import json
import glob
import os
from os.path import join as join_path, abspath
import subprocess
import sys
import yaml

from utils import load_config


def find_shortcut_filepaths(config):
    filepaths = []

    if isinstance(config['shortcut_data_directories'], str):  # ensure it's a list
        config['shortcut_data_directories'] = [config['shortcut_data_directories']]

    for dir_path in config['shortcut_data_directories']:
        if not dir_path.startswith('/'):
            sys.exit(f'error: shortcut_data_directories must be absolute paths, found: {dir_path}')
        filepaths.extend(
            glob.glob(f"{dir_path}/**/*.shortcuts", recursive=True)
        )
    return filepaths


def create_html_gallery(all_shortcut_data, config):

    # Determine output paths from config
    output_dir = abspath(str(config['output']['output_dir']))
    os.makedirs(output_dir, exist_ok=True)
    gallery_abs_path = abspath(config['output']['gallery_path'])
    ss_config_path = config['output']['scraper_shot_config_path']

    # load assets
    with open("vendor_assets/obsidian-shortcut-viewer-plugin/src/ui/view.js", "r") as f:
        js_core = f.read()
    with open("vendor_assets/obsidian-shortcut-viewer-plugin/src/ui/view.css", "r") as f:
        css_core = f.read()

    scale = config['ui']['css_scale']
    scale_style = f":root {{ --shortcut-scale: {scale}; }}"

    # Build containers and track shots for shots.yaml
    containers = ""
    render_calls = ""
    shots_config = []

    for shortcut_data in all_shortcut_data:
        app_id = shortcut_data['app_id'].lower()
        app_id_w_underscores = app_id.replace('.', '_')
        app_name = shortcut_data.get('app_name', '')

        frame_id = f"frame-{app_id_w_underscores}"  # outer div with padding
        ui_id = f"ui-{app_id_w_underscores}"  # actual UI content

        containers += f'''
        <div id="{frame_id}" class="export-frame">
            <div id="{ui_id}" class="render-target"></div>
        </div>'''

        render_calls += f"renderShortcuts(document.getElementById('{ui_id}'), {json.dumps(shortcut_data['shortcuts'])}, '{app_id}', {json.dumps(app_name)});\n"

        image_filepath = join_path(output_dir, f"{app_id_w_underscores}.png")

        shots_config.append({
            "url": gallery_abs_path,  # no need for file:// prefix
            "output": image_filepath,
            "selector": f"#{frame_id}"
        })

    full_html = f"""
        <html>
        <head>
            <style>{css_core}</style>
            <style>{scale_style}</style>
            <style>        
                body {{ 
                    background-color: white; 
                    padding: 30px; 
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
                    max-width: 950px;
                    margin: 0 auto;
                    gap: 40px 80px;
                }}

                .export-frame {{ padding: 10px; display: inline-block; min-width: fit-content; }}                
                .render-target {{ display: inline-block; }}
            </style>
        </head>
        <body>
            {containers}
            <script type="module">
                {js_core}
                {render_calls}
            </script>
        </body>
        </html>
        """

    with open(gallery_abs_path, "w") as f:
        f.write(full_html)

    # Write shots.yaml
    with open(ss_config_path, "w") as f:
        yaml.dump(shots_config, f)

    print(f"Generated {gallery_abs_path} and {ss_config_path}")


def create_images(config):

    shots_yaml_path = os.path.abspath(
        config['output']['scraper_shot_config_path']
    )
    scale = config['ui']['screenshot_scale']

    try:
        # Executes the terminal command directly from Python
        result = subprocess.run(
            [
                "shot-scraper",
                "multi",
                shots_yaml_path,
                "--scale-factor", str(scale),
            ],
            check=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        print("🎉 All shortcut images captured cleanly!")

    except subprocess.CalledProcessError as e:
        print(f"❌ shot-scraper pipeline failed:\n{e.stderr}")
    except FileNotFoundError:
        print("❌ Error: 'shot-scraper' command not found in environment. Is it installed via pip?")


def main():
    if "JUSTFILE" not in os.environ:
        sys.exit("❌ ERROR: Script must be run via `just`.\nUsage: just render")

    config = load_config()

    output_dir = abspath(str(config['output']['output_dir']))
    os.makedirs(output_dir, exist_ok=True)

    all_shortcut_data = []
    for fp in find_shortcut_filepaths(config):
        try:
            with open(fp, 'r') as file:
                data = yaml.safe_load(file)
        except Exception as e:
            print(f'Error reading {fp}: {e}')
            continue
        if data and 'app_id' in data and 'shortcuts' in data:
            all_shortcut_data.append(data)
        else:
            print(f'Skipping {fp}: missing fields')

    create_html_gallery(all_shortcut_data, config)

    create_images(config)


if __name__ == "__main__":
    main()
