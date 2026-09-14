"""Standalone System Tray Application for Smart Keyboard.

Runs silently in the Windows System Tray (notification area) with zero console window.
Provides right-click menu, status toggles, startup registration, and visual icon indicators.
"""

import ctypes
from ctypes import wintypes
import os
import subprocess
import sys
import threading
import time
import traceback
import winreg
from typing import Optional

# Ensure workspace root and package dir are always in sys.path
_current_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_current_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

# File logger for diagnosing live desktop operation
def log_event(msg: str) -> None:
    try:
        log_dir = os.path.expanduser("~")
        log_file = os.path.join(log_dir, "plik.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


def handle_exception(exc_type, exc_value, exc_traceback):
    err = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_event(f"[FATAL_CRASH] Unhandled exception:\n{err}")


sys.excepthook = handle_exception

# GUI-heavy imports (pystray, PIL, LiveKeyboardService) are deferred to the
# functions that actually need them so that lightweight helpers like
# SingleInstanceMutex and get_asset_path remain importable on headless CI
# runners that lack a desktop session.

ERROR_ALREADY_EXISTS = 183


class SingleInstanceMutex:
    """Ensures only one instance of Plik runs per Windows desktop session."""

    def __init__(self, mutex_name: str = "Local\\PlikSingleInstanceMutex"):
        self.mutex_name = mutex_name
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self.kernel32.CreateMutexW.restype = wintypes.HANDLE
        self.kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
        self.kernel32.CloseHandle.restype = wintypes.BOOL
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

        self.handle = self.kernel32.CreateMutexW(None, True, self.mutex_name)
        self.already_running = (ctypes.get_last_error() == ERROR_ALREADY_EXISTS)

    def release(self):
        if self.handle:
            self.kernel32.CloseHandle(self.handle)
            self.handle = None


def get_asset_path(filename: str) -> str:
    """Resolve asset file path, supporting both development and PyInstaller bundled mode."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        p1 = os.path.join(sys._MEIPASS, "plik", "assets", filename)
        if os.path.exists(p1):
            return p1
        p2 = os.path.join(sys._MEIPASS, "assets", filename)
        if os.path.exists(p2):
            return p2
        return p1
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "assets", filename)


def create_tray_icon(is_active: bool = True):
    """Generates or loads a sleek high-res icon for the system tray."""
    from PIL import Image, ImageDraw

    ico_name = "app_icon.png" if is_active else "app_icon_paused.png"
    ico_path = get_asset_path(ico_name)
    if not os.path.exists(ico_path):
        ico_name = "app_icon.ico" if is_active else "app_icon_paused.ico"
        ico_path = get_asset_path(ico_name)

    if os.path.exists(ico_path):
        try:
            img = Image.open(ico_path).convert("RGBA")
            return img.resize((64, 64), Image.Resampling.LANCZOS)
        except Exception:
            pass

    img = Image.new("RGBA", (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    bg_color = "#059669" if is_active else "#f57f17"  # Emerald Green if Active, Amber if Paused
    draw.rounded_rectangle([4, 4, 60, 60], radius=16, fill=bg_color)
    draw.text((22, 16), "P", fill="#ffffff")
    return img


class PlikTrayApp:
    def __init__(self):
        import pystray  # noqa: F811 — lazy import for headless CI compat
        from plik.live_service import LiveKeyboardService
        from plik.storage import SettingsManager

        log_event("Initializing PlikTrayApp...")
        self.settings_mgr = SettingsManager.get_instance()
        saved = self.settings_mgr.settings

        self.service = LiveKeyboardService(
            on_switch_callback=self._on_switch_event,
            on_status_callback=self._on_status_event,
        )

        # Apply persisted settings
        self.service._is_paused = saved.is_paused
        self.service.config.enable_autocorrect = saved.enable_autocorrect
        self.service.config.enable_thai_autocorrect = saved.enable_thai_autocorrect
        self.service.config.enable_eng_autocorrect = saved.enable_eng_autocorrect
        self.service.config.enable_sound_alert = getattr(saved, "enable_sound_alert", True)
        self.service.config.switch_on_delimiter_only = getattr(saved, "switch_on_delimiter_only", True)
        self._is_paused = saved.is_paused

        self.icon: Optional[pystray.Icon] = None
        self._service_thread: Optional[threading.Thread] = None

    def _on_switch_event(self, act_type: str, orig: str, repl: str, target: str, proc: str):
        log_event(f"[{act_type}] Proc: {proc} | '{orig}' -> '{repl}' (Layout: {target})")
        if self.icon and act_type == "AUTO_SWITCH":
            try:
                self.icon.title = f"Plik: {orig} -> {repl} ({target})"
            except Exception:
                pass

    def _on_status_event(self, is_paused: bool):
        self._is_paused = is_paused
        log_event(f"[STATUS] Paused: {is_paused}")
        if self.icon:
            try:
                self.icon.icon = create_tray_icon(not is_paused)
                status_text = "PAUSED (พักชั่วคราว)" if is_paused else "ACTIVE (พร้อมทำงาน)"
                self.icon.title = f"Plik - {status_text}"
            except Exception:
                pass

    def toggle_pause(self, icon=None, item=None):
        """Toggles active/paused state."""
        self._is_paused = self.service.toggle_pause()
        self.settings_mgr.settings.is_paused = self._is_paused
        self.settings_mgr.save()
        self._on_status_event(self._is_paused)

    def is_autocorrect_enabled(self) -> bool:
        """Returns whether auto-correction is currently enabled."""
        return self.service.config.enable_autocorrect

    def toggle_autocorrect(self, icon=None, item=None):
        """Toggles auto-correction on or off."""
        enabled = self.service.toggle_autocorrect()
        self.settings_mgr.settings.enable_autocorrect = enabled
        self.settings_mgr.save()
        status_msg = "เปิดระบบแก้คำผิดแล้ว (Auto-Correct Enabled)" if enabled else "ปิดระบบแก้คำผิดแล้ว (Auto-Correct Disabled)"
        log_event(f"[AUTOCORRECT] {status_msg}")
        if self.icon:
            try:
                self.icon.notify(status_msg, "Plik (พลิก)")
            except Exception:
                pass

    def is_sound_alert_enabled(self) -> bool:
        """Returns whether sound alert is currently enabled."""
        return getattr(self.service.config, "enable_sound_alert", True)

    def toggle_sound_alert(self, icon=None, item=None):
        """Toggles sound alert on or off."""
        enabled = self.service.toggle_sound_alert()
        self.settings_mgr.settings.enable_sound_alert = enabled
        self.settings_mgr.save()
        status_msg = "เปิดเสียงแจ้งเตือนแล้ว (Sound Alert Enabled)" if enabled else "ปิดเสียงแจ้งเตือนแล้ว (Sound Alert Disabled)"
        log_event(f"[SOUND_ALERT] {status_msg}")
        if self.icon:
            try:
                self.icon.notify(status_msg, "Plik (พลิก)")
            except Exception:
                pass

    def is_delimiter_only_enabled(self) -> bool:
        """Returns whether delimiter-only switching (RightLang mode) is currently enabled."""
        return getattr(self.service.config, "switch_on_delimiter_only", True)

    def toggle_delimiter_only(self, icon=None, item=None):
        """Toggles between delimiter-only switching and continuous in-flight switching."""
        curr = getattr(self.service.config, "switch_on_delimiter_only", True)
        new_val = not curr
        self.service.config.switch_on_delimiter_only = new_val
        self.settings_mgr.settings.switch_on_delimiter_only = new_val
        self.settings_mgr.save()
        status_msg = (
            "สลับคำเมื่อเคาะ Spacebar เท่านั้น (โหมดเสถียรแบบ RightLang)"
            if new_val
            else "สลับคำแบบทันทีระหว่างพิมพ์ (In-Flight Mode)"
        )
        log_event(f"[DELIMITER_MODE] {status_msg}")
        if self.icon:
            try:
                self.icon.notify(status_msg, "Plik (พลิก)")
            except Exception:
                pass

    def is_startup_enabled(self) -> bool:
        """Checks if Plik is set to run on Windows startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ,
            )
            val, _ = winreg.QueryValueEx(key, "Plik")
            winreg.CloseKey(key)
            return bool(val)
        except Exception:
            return False

    def toggle_startup(self, icon=None, item=None):
        """Adds or removes Plik from Windows startup."""
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            if self.is_startup_enabled():
                winreg.DeleteValue(key, "Plik")
                log_event("Startup registration removed.")
            else:
                exe_path = sys.executable
                if getattr(sys, "frozen", False):
                    cmd = f'"{sys.executable}"'
                else:
                    script_path = os.path.abspath(__file__)
                    cmd = f'"{exe_path}" "{script_path}"'
                winreg.SetValueEx(key, "Plik", 0, winreg.REG_SZ, cmd)
                log_event(f"Startup registration added: {cmd}")
            winreg.CloseKey(key)
        except Exception as e:
            log_event(f"Failed to toggle startup: {e}")

    def close_rightlang(self, icon=None, item=None):
        """Closes any conflicting RightLang instances."""
        try:
            subprocess.run("taskkill /IM rightlang.exe /F", shell=True, check=True)
            log_event("RightLang terminated via taskkill.")
            if self.icon:
                try:
                    self.icon.notify("ปิด RightLang เรียบร้อยแล้ว", "Plik (พลิก)")
                except Exception:
                    pass
        except Exception:
            if self.icon:
                try:
                    self.icon.notify("ไม่พบ RightLang กำลังทำงาน", "Plik (พลิก)")
                except Exception:
                    pass

    def exit_app(self, icon=None, item=None):
        """Exits the tray app and cleanly unhooks the keyboard."""
        log_event("Exiting Plik...")
        if self.service:
            self.service.stop()
        if self.icon:
            self.icon.stop()

    def run(self):
        import pystray
        from pystray import MenuItem as item

        log_event("Starting background keyboard service thread...")
        self._service_thread = threading.Thread(target=self.service.start, daemon=True)
        self._service_thread.start()

        # Build the System Tray menu
        menu = pystray.Menu(
            item("⚡ Plik (พลิก) - CHA Engine", lambda: None, enabled=False),
            pystray.Menu.SEPARATOR,
            item(
                lambda text: "⏸ พักชั่วคราว (Pause)" if not self._is_paused else "▶ เปิดทำงาน (Resume)",
                self.toggle_pause,
                default=True,
            ),
            item(
                "✨ แก้คำผิดอัตโนมัติ (Auto-Correct)",
                self.toggle_autocorrect,
                checked=lambda item: self.is_autocorrect_enabled(),
            ),
            item(
                "🔔 เสียงแจ้งเตือนเมื่อพลิกคำ (Sound Alert)",
                self.toggle_sound_alert,
                checked=lambda item: self.is_sound_alert_enabled(),
            ),
            item(
                "⚡ สลับเมื่อเคาะ Spacebar (โหมดเสถียรแบบ RightLang)",
                self.toggle_delimiter_only,
                checked=lambda item: self.is_delimiter_only_enabled(),
            ),
            item("🚫 ปิด RightLang ที่รันอยู่", self.close_rightlang),
            item(
                "🚀 เปิดพร้อม Windows (Run on Startup)",
                self.toggle_startup,
                checked=lambda item: self.is_startup_enabled(),
            ),
            pystray.Menu.SEPARATOR,
            item("❌ ออกจากโปรแกรม (Exit)", self.exit_app),
        )

        self.icon = pystray.Icon(
            "Plik",
            create_tray_icon(True),
            "Plik - ACTIVE (พร้อมทำงาน)",
            menu=menu,
        )

        def notify_launch():
            time.sleep(1.0)
            if self.icon:
                try:
                    self.icon.notify(
                        "Plik พร้อมใช้งานแล้ว!\nพลิกภาษาไทย-อังกฤษ และแก้คำผิดอัตโนมัติ",
                        "Plik (พลิก)",
                    )
                except Exception:
                    pass

        threading.Thread(target=notify_launch, daemon=True).start()
        log_event("Entering tray icon mainloop.")
        self.icon.run()


# Alias for backward compatibility
SmartKeyboardTrayApp = PlikTrayApp


def main():
    mutex = SingleInstanceMutex()
    if mutex.already_running:
        log_event("[SINGLE_INSTANCE] Another instance of Plik is already running. Exiting cleanly.")
        sys.exit(0)

    try:
        app = PlikTrayApp()
        app.run()
    finally:
        mutex.release()


if __name__ == "__main__":
    main()
