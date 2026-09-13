"""Configuration options for Smart Keyboard."""

from dataclasses import dataclass, field
from typing import Set


@dataclass
class SwitcherConfig:
    """Configuration settings for the intelligent switcher."""

    # Confidence threshold to trigger automatic switching (0.0 - 1.0)
    auto_switch_threshold: float = 0.85

    # Minimum keystrokes before evaluating auto-switch
    min_word_length: int = 3

    # Maximum word length kept in recent buffer
    max_buffer_length: int = 256


    # Time window (seconds) within which pressing Backspace triggers Instant Undo
    instant_undo_window_sec: float = 2.5

    # Enable auto-switching (if False, operates in Hotkey/Manual mode only)
    enable_auto_switch: bool = True

    # Enable auto-correction for common Thai and English typos
    enable_autocorrect: bool = True
    enable_thai_autocorrect: bool = True
    enable_eng_autocorrect: bool = True

    # Hotkey for manual conversion of previous word
    manual_convert_hotkey: str = "pause"  # e.g., 'pause', 'shift+space'

    # Process names where auto-switching is automatically switched to PASSIVE/HOTKEY mode
    dev_process_names: Set[str] = field(
        default_factory=lambda: {
            "code.exe",
            "windowsterminal.exe",
            "powershell.exe",
            "cmd.exe",
            "devenv.exe",
            "pycharm64.exe",
            "idea64.exe",
            "git.exe",
            "bash.exe",
            "conhost.exe",
        }
    )

    # Process names where auto-switch is completely disabled for safety
    secure_process_names: Set[str] = field(
        default_factory=lambda: {
            "keepass.exe",
            "1password.exe",
            "bitwarden.exe",
            "credentialmanager.exe",
        }
    )

    # Slang and acronyms that should be protected from conversion
    protected_tokens: Set[str] = field(
        default_factory=lambda: {
            "555",
            "5555",
            "55555",
            "krub",
            "kub",
            "eiei",
            "na",
            "ha",
            "lol",
            "btw",
            "api",
            "url",
            "id",
            "json",
            "html",
            "css",
            "sql",
            "git",
        }
    )
