import json
import os
import sys


class SettingsManager:
    DEFAULTS = {
        "min_ram": 1024, "max_ram": 2048, "width": 854, "height": 480,
        "fullscreen": False, "close_launcher": True, "performance_mode": "Balanced",
        "custom_jvm_args": "", "language": "en", "show_console": False,
        "username": "Player", "auth_type": "offline", "uuid": "", "access_token": "",
        "optimize_jvm": True, "java_path": "", "game_dir": "", "debug_mode": False, "first_run": True,
        "performance": {"g1gc": True, "pretouch": True, "largepages": False, "parallel": True, "aggressive": False, "stringdedup": False}
    }

    def __init__(self, root_dir):
        if getattr(sys, 'frozen', False):
            self.data_dir = os.path.join(os.path.dirname(sys.executable), ".launcher")
        else:
            self.data_dir = os.path.join(root_dir, ".launcher")
        self.settings_file = os.path.join(self.data_dir, "settings.json")
        self.settings = self.load()

    def load(self):
        if not os.path.exists(self.settings_file):
            return self.DEFAULTS.copy()
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                merged = self.DEFAULTS.copy()
                for key, value in data.items():
                    if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                        merged[key].update(value)
                    else:
                        merged[key] = value
                return merged
        except Exception:
            return self.DEFAULTS.copy()

    def save(self):
        os.makedirs(self.data_dir, exist_ok=True)
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

    def get(self, key):
        return self.settings.get(key, self.DEFAULTS.get(key))

    def set(self, key, value):
        if isinstance(value, dict) and key in self.settings and isinstance(self.settings[key], dict):
            self.settings[key].update(value)
        else:
            self.settings[key] = value
        self.save()
