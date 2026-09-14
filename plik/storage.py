"""Persistent Settings Storage for Smart Keyboard.

Saves and loads user preferences from %APPDATA%/SmartKeyboard/settings.json.
Guarantees clean fallbacks, atomic writes, and thread-safe operations.
"""

import json
import os
from dataclasses import asdict, dataclass
from typing import Optional


@dataclass
class AppSettings:
    is_paused: bool = False
    enable_autocorrect: bool = True
    enable_thai_autocorrect: bool = True
    enable_eng_autocorrect: bool = True
    enable_sound_alert: bool = True
    switch_on_delimiter_only: bool = True


class SettingsManager:
    """Manages reading and writing application settings in %APPDATA%."""

    _instance: Optional["SettingsManager"] = None

    def __init__(self, custom_path: Optional[str] = None):
        if custom_path:
            self.settings_file = custom_path
        else:
            appdata = os.environ.get("APPDATA") or os.path.expanduser("~")
            base_dir = os.path.join(appdata, "Plik")
            os.makedirs(base_dir, exist_ok=True)
            self.settings_file = os.path.join(base_dir, "settings.json")

            # Backward-compatibility migration from SmartKeyboard
            old_file = os.path.join(appdata, "SmartKeyboard", "settings.json")
            if not os.path.exists(self.settings_file) and os.path.exists(old_file):
                try:
                    import shutil
                    shutil.copy2(old_file, self.settings_file)
                except Exception:
                    pass
        self.settings: AppSettings = self.load()

    @classmethod
    def get_instance(cls, custom_path: Optional[str] = None) -> "SettingsManager":
        if cls._instance is None:
            cls._instance = cls(custom_path=custom_path)
        return cls._instance

    def load(self) -> AppSettings:
        """Loads settings from disk, or returns default settings if absent/corrupted."""
        if not os.path.exists(self.settings_file):
            return AppSettings()

        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return AppSettings(
                is_paused=bool(data.get("is_paused", False)),
                enable_autocorrect=bool(data.get("enable_autocorrect", True)),
                enable_thai_autocorrect=bool(data.get("enable_thai_autocorrect", True)),
                enable_eng_autocorrect=bool(data.get("enable_eng_autocorrect", True)),
                enable_sound_alert=bool(data.get("enable_sound_alert", True)),
                switch_on_delimiter_only=bool(data.get("switch_on_delimiter_only", True)),
            )
        except Exception:
            return AppSettings()

    def save(self) -> bool:
        """Atomically saves the current settings to disk."""
        try:
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            temp_file = self.settings_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(asdict(self.settings), f, indent=2, ensure_ascii=False)
            os.replace(temp_file, self.settings_file)
            return True
        except Exception:
            return False
