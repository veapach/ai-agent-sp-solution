import json
from pathlib import Path

CONFIG_FILE = Path(__file__).parent.parent / "browser_config.json"

DEFAULT_CONFIG = {
    "window_x": 0,
    "window_y": 0,
    "window_width": 960,
    "window_height": 1080,
    "viewport_width": 960,
    "viewport_height": 1040,
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
