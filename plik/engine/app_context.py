"""Tier 3: Process and Application Context Engine.

Detects the active foreground window and applies context-aware policies.
Prevents auto-switching in IDEs, terminals, and password fields to eliminate
RightLang's biggest annoyance.
"""

import enum
import os
import sys
from typing import Optional, Set
from plik.config import SwitcherConfig


class AppCategory(enum.Enum):
    """Classification of the active application."""

    GENERAL = "GENERAL"          # Standard apps: browsers, editors, chat (Auto-switch ON)
    DEV_TOOL = "DEV_TOOL"        # Coding tools, terminals, IDEs (Passive / Hotkey only)
    SECURE = "SECURE"            # Password managers, lock dialogs (Completely disabled)


class AppContextManager:
    """Monitors the active foreground window process and enforces app-level safety policies."""

    def __init__(self, config: Optional[SwitcherConfig] = None):
        self.config = config or SwitcherConfig()
        self._dev_processes = {p.lower() for p in self.config.dev_process_names}
        self._secure_processes = {p.lower() for p in self.config.secure_process_names}
        self._cached_pid: Optional[int] = None
        self._cached_proc_name: str = ""
        self._cached_category: AppCategory = AppCategory.GENERAL

    def get_active_process_name(self) -> str:
        """Get the executable filename of the currently focused window on Windows."""
        if sys.platform != "win32":
            return "mock_process.exe"

        try:
            import ctypes
            from ctypes import wintypes

            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32

            hwnd = user32.GetForegroundWindow()
            if not hwnd:
                return ""

            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            if not pid.value:
                return ""

            if pid.value == self._cached_pid:
                return self._cached_proc_name

            # PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            h_process = kernel32.OpenProcess(0x1000, False, pid.value)
            if not h_process:
                return ""

            try:
                buffer = ctypes.create_unicode_buffer(1024)
                size = wintypes.DWORD(len(buffer))
                if kernel32.QueryFullProcessImageNameW(h_process, 0, buffer, ctypes.byref(size)):
                    full_path = buffer.value
                    proc_name = os.path.basename(full_path).lower()
                    self._cached_pid = pid.value
                    self._cached_proc_name = proc_name
                    return proc_name
            finally:
                kernel32.CloseHandle(h_process)

        except Exception:
            pass

        return ""

    def get_app_category(self, process_name: Optional[str] = None) -> AppCategory:
        """Classify process into GENERAL, DEV_TOOL, or SECURE."""
        if process_name is None:
            process_name = self.get_active_process_name()

        proc_lower = process_name.lower().strip()
        if not proc_lower:
            return AppCategory.GENERAL

        if proc_lower in self._secure_processes:
            return AppCategory.SECURE

        if proc_lower in self._dev_processes:
            return AppCategory.DEV_TOOL

        return AppCategory.GENERAL

    def is_dev_tool(self, process_name: Optional[str] = None) -> bool:
        """Check if process is a developer tool (IDE, terminal)."""
        return self.get_app_category(process_name) == AppCategory.DEV_TOOL

    def should_auto_switch(
        self, process_name: Optional[str] = None, current_layout: str = "EN"
    ) -> bool:
        """Check if automatic switching is permitted for the current application.
        
        - SECURE applications (password managers): Completely disabled.
        - DEV_TOOL (IDEs, terminals) & GENERAL: Auto-switch permitted.
        """
        category = self.get_app_category(process_name)
        if category == AppCategory.SECURE:
            return False
        return self.config.enable_auto_switch


