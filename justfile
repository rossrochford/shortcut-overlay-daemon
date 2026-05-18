
set dotenv-load := true
export JUSTFILE := justfile()

# for development only
local_plugin_path := env_var_or_default("LOCAL_PLUGIN_PATH", "<LOCAL_PATH_TO_PLUGIN>")


clone-assets:
    mkdir -p vendor_assets
    rm -rf vendor_assets/obsidian-shortcut-viewer-plugin
    git clone https://github.com/rossrochford/obsidian-shortcut-viewer-plugin vendor_assets/obsidian-shortcut-viewer-plugin

# for development only
link-assets:
    mkdir -p vendor_assets
    @test "{{local_plugin_path}}" != "<LOCAL_PATH_TO_PLUGIN>" || (echo "❌ Set 'local_plugin_path' in justfile!" && exit 1)
    rm -rf vendor_assets/obsidian-shortcut-viewer-plugin
    ln -s /home/rossr/code/obsidian-shortcut-viewer-plugin/ vendor_assets/obsidian-shortcut-viewer-plugin


# Create HTML gallery and shortcut images
render:
    mkdir -p output
    @test -d vendor_assets/obsidian-shortcut-viewer-plugin || (echo "❌ UI Assets missing. Run: 'just clone-assets' (or for dev: 'just link-assets')."; exit 1)
    uv run python app/render_shortcuts.py


# Run the overlay daemon script
run-daemon:
    uv run python app/main_daemon.py


stop-service:
    systemctl --user stop shortcut-overlay.service

restart-service:
    systemctl --user restart shortcut-overlay.service


# Start from scratch, remove: .venv/, output/ and vendor_assets/
clean:
    rm -rf .venv/
    rm -rf output/
    rm -rf vendor_assets/

