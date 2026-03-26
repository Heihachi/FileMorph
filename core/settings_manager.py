# FileMorph/core/settings_manager.py
import json
from pathlib import Path

from utils.app_paths import get_user_data_dir


class SettingsManager:
    def __init__(self, settings_path: Path | None = None):
        if settings_path is None:
            settings_path = get_user_data_dir() / "settings.json"

        self.settings_path = settings_path
        self.default_settings = {
            "theme": "light",
            "language": "ru",
            "output_mode": "source_folder",
            "output_folder": ""
        }

        self._ensure_settings_file()

    def _ensure_settings_file(self):
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.settings_path.exists():
            self.save(self.default_settings)

    def load(self) -> dict:
        try:
            with open(self.settings_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = self.default_settings.copy()

        merged = self.default_settings.copy()
        merged.update(data)
        return merged

    def save(self, settings: dict) -> None:
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)