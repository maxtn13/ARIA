"""
ARIA Config Manager — reads/writes settings to ~/.aria/config.json
"""
import json, os
from pathlib import Path

DEFAULTS = {
    "index_paths": [str(Path.home())],
    "ollama_url": "http://localhost:11434",
    "ollama_model": "mistral",
    "use_ollama": True,
    "hotkey": "Ctrl+Space",
    "start_minimized": True,
    "theme": "light",
    "window_width": 900,
    "window_height": 640,
    "auto_index_on_start": False,
    "index_db_path": str(Path.home() / ".aria" / "files.db"),
    "max_results": 12,
    "semantic_search": False,
}

CONFIG_DIR = Path.home() / ".aria"
CONFIG_FILE = CONFIG_DIR / "config.json"


class Config:
    def __init__(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        self._data = {**DEFAULTS}
        self.load()

    def load(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE) as f:
                    saved = json.load(f)
                self._data.update(saved)
            except Exception:
                pass

    def save(self):
        with open(CONFIG_FILE, "w") as f:
            json.dump(self._data, f, indent=2)

    def get(self, key, default=None):
        return self._data.get(key, DEFAULTS.get(key, default))

    def set(self, key, value):
        self._data[key] = value
        self.save()

    def update(self, d: dict):
        self._data.update(d)
        self.save()


config = Config()
