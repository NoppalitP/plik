"""Live Windows Hook Service for Smart Keyboard.

Runs as a real-time background service:
- Intercepts keystrokes via low-level Windows hook (WH_KEYBOARD_LL).
- Evaluates typing through the Cascaded Hybrid Architecture (CHA).
- Performs atomic Unicode text replacement via SendInput.
- Automatically synchronizes OS keyboard layouts.
- Provides Instant Undo on immediate Backspace.

Usage:
    .\\.venv\\Scripts\\python.exe -m plik.live_service
"""

import ctypes
from ctypes import wintypes
import os
import sys
import threading
import time
from typing import Optional

# Ensure standard output can handle Unicode without charmap crashes on Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from plik.config import SwitcherConfig
from plik.engine.core import CoreEngine
from plik.platform.windows import (
    INPUT_KEYBOARD,
    KEYEVENTF_KEYUP,
    KEYEVENTF_UNICODE,
    VK_BACK,
    WindowsPlatform,
)

# Win32 Hook Constants
WH_KEYBOARD_LL = 13
WM_KEYDOWN = 0x0100
WM_SYSKEYDOWN = 0x0104
WM_KEYUP = 0x0101
WM_SYSKEYUP = 0x0105

# Injected keystroke marker to prevent recursive hook triggering
SMART_KEYBOARD_EXTRA_INFO = 0x534D415254  # "SMART" in hex
LLKHF_INJECTED = 0x00000010


def log_event(msg: str) -> None:
    """Write diagnostic messages to %USERPROFILE%/plik.log."""
    try:
        log_dir = os.path.expanduser("~")
        log_file = os.path.join(log_dir, "plik.log")
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass


class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]


HOOKPROC = ctypes.WINFUNCTYPE(
    ctypes.c_longlong, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM
)


class LiveKeyboardService:
    """Manages the active OS keyboard hook and real-time layout switcher."""

    def __init__(
        self,
        config: Optional[SwitcherConfig] = None,
        on_switch_callback=None,
        on_status_callback=None,
    ):
        self.config = config or SwitcherConfig()
        self.engine = CoreEngine(config=self.config)
        self.platform = WindowsPlatform()
        self.user32 = ctypes.windll.user32
        self.kernel32 = ctypes.windll.kernel32
        self.on_switch_callback = on_switch_callback
        self.on_status_callback = on_status_callback

        self._hook = None
        self._hook_proc = None
        self._is_paused = False
        self._key_state = (ctypes.c_ubyte * 256)()
        self._thread_id = 0

        # Configure explicit 64-bit Win32 API signatures for stability
        self._setup_win32_signatures()

    def _setup_win32_signatures(self):
        """Set explicit argtypes and restype for all native Win32 calls."""
        # user32 Hook APIs
        self.user32.CallNextHookEx.restype = ctypes.c_longlong
        self.user32.CallNextHookEx.argtypes = [
            wintypes.HHOOK,
            ctypes.c_int,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]

        self.user32.SetWindowsHookExW.restype = wintypes.HHOOK
        self.user32.SetWindowsHookExW.argtypes = [
            ctypes.c_int,
            HOOKPROC,
            wintypes.HINSTANCE,
            wintypes.DWORD,
        ]

        self.user32.UnhookWindowsHookEx.restype = wintypes.BOOL
        self.user32.UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]

        # Translation and Window APIs
        self.user32.ToUnicodeEx.restype = ctypes.c_int
        self.user32.ToUnicodeEx.argtypes = [
            wintypes.UINT,
            wintypes.UINT,
            ctypes.POINTER(ctypes.c_ubyte),
            wintypes.LPWSTR,
            ctypes.c_int,
            wintypes.UINT,
            wintypes.HKL,
        ]

        self.user32.GetKeyboardLayout.restype = wintypes.HKL
        self.user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]

        self.user32.GetForegroundWindow.restype = wintypes.HWND
        self.user32.GetForegroundWindow.argtypes = []

        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD
        self.user32.GetWindowThreadProcessId.argtypes = [
            wintypes.HWND,
            ctypes.POINTER(wintypes.DWORD),
        ]

        self.user32.GetAsyncKeyState.restype = ctypes.c_short
        self.user32.GetAsyncKeyState.argtypes = [ctypes.c_int]

        self.user32.GetKeyState.restype = ctypes.c_short
        self.user32.GetKeyState.argtypes = [ctypes.c_int]

        self.user32.PostThreadMessageW.restype = wintypes.BOOL
        self.user32.PostThreadMessageW.argtypes = [
            wintypes.DWORD,
            wintypes.UINT,
            wintypes.WPARAM,
            wintypes.LPARAM,
        ]

        # kernel32 APIs
        self.kernel32.GetModuleHandleW.restype = wintypes.HMODULE
        self.kernel32.GetModuleHandleW.argtypes = [wintypes.LPCWSTR]

        self.kernel32.GetCurrentThreadId.restype = wintypes.DWORD
        self.kernel32.GetCurrentThreadId.argtypes = []

        self.kernel32.GetLastError.restype = wintypes.DWORD
        self.kernel32.GetLastError.argtypes = []

        self.kernel32.OpenProcess.restype = wintypes.HANDLE
        self.kernel32.OpenProcess.argtypes = [
            wintypes.DWORD,
            wintypes.BOOL,
            wintypes.DWORD,
        ]

        self.kernel32.QueryFullProcessImageNameW.restype = wintypes.BOOL
        self.kernel32.QueryFullProcessImageNameW.argtypes = [
            wintypes.HANDLE,
            wintypes.DWORD,
            wintypes.LPWSTR,
            ctypes.POINTER(wintypes.DWORD),
        ]

        self.kernel32.CloseHandle.restype = wintypes.BOOL
        self.kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

    def toggle_pause(self) -> bool:
        """Toggles the paused state of the service."""
        self._is_paused = not self._is_paused
        if self.on_status_callback:
            try:
                self.on_status_callback(self._is_paused)
            except Exception:
                pass
        return self._is_paused

    def toggle_autocorrect(self) -> bool:
        """Toggles the auto-correction feature on or off."""
        self.config.enable_autocorrect = not self.config.enable_autocorrect
        return self.config.enable_autocorrect

    def get_active_process_name(self) -> str:
        """Resolves the executable name of the current foreground window."""
        try:
            hwnd = self.user32.GetForegroundWindow()
            if not hwnd:
                return "unknown.exe"
            pid = wintypes.DWORD()
            self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            hProc = self.kernel32.OpenProcess(0x1000, False, pid.value)
            if not hProc:
                return "unknown.exe"
            buf = ctypes.create_unicode_buffer(1024)
            size = wintypes.DWORD(1024)
            self.kernel32.QueryFullProcessImageNameW(hProc, 0, buf, ctypes.byref(size))
            self.kernel32.CloseHandle(hProc)
            return buf.value.split("\\")[-1].lower()
        except Exception:
            return "unknown.exe"

    def _vk_to_char(self, vk_code: int, scan_code: int) -> Optional[str]:
        """Translates a virtual key code to character based on current keyboard state."""
        try:
            # 1. Check special non-character keys
            if vk_code in (VK_BACK, 0x1B):  # Backspace, Escape
                return None

            # Ignore navigation and functional keys
            if 0x21 <= vk_code <= 0x2F or 0x70 <= vk_code <= 0x87:  # Arrows, Page, Function keys F1-F24
                return None

            # 2. Ignore modifier combinations (Ctrl, Alt, Win) so hotkeys aren't captured
            ctrl_pressed = bool(self.user32.GetAsyncKeyState(0x11) & 0x8000)
            alt_pressed = bool(self.user32.GetAsyncKeyState(0x12) & 0x8000)
            win_pressed = bool(
                self.user32.GetAsyncKeyState(0x5B) & 0x8000
                or self.user32.GetAsyncKeyState(0x5C) & 0x8000
            )
            if ctrl_pressed or alt_pressed or win_pressed:
                return None

            # 3. Read physical modifier state (Shift, CapsLock)
            key_state = (ctypes.c_ubyte * 256)()
            if self.user32.GetAsyncKeyState(0x10) & 0x8000:  # VK_SHIFT
                key_state[0x10] = 0x80
            if self.user32.GetKeyState(0x14) & 0x0001:  # VK_CAPITAL
                key_state[0x14] = 0x01

            # 4. Get active window keyboard layout
            hwnd = self.user32.GetForegroundWindow()
            thread_id = self.user32.GetWindowThreadProcessId(hwnd, None) if hwnd else 0
            hkl = self.user32.GetKeyboardLayout(thread_id)

            # 5. Translate via ToUnicodeEx
            buf = ctypes.create_unicode_buffer(8)
            ret = self.user32.ToUnicodeEx(
                vk_code, scan_code, key_state, buf, len(buf), 0, hkl
            )

            if ret > 0:
                return buf.value
            return None
        except Exception:
            return None

    def _on_keyboard_event(self, nCode: int, wParam: wintypes.WPARAM, lParam: wintypes.LPARAM) -> int:
        """Low-level keyboard hook callback."""
        if nCode < 0:
            return self.user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

        try:
            # Only process Key Down events
            if wParam in (WM_KEYDOWN, WM_SYSKEYDOWN):
                kb = KBDLLHOOKSTRUCT.from_address(lParam)

                # Only ignore keystrokes sent by our own program to prevent infinite loops
                if kb.dwExtraInfo == SMART_KEYBOARD_EXTRA_INFO:
                    return self.user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

                vk = kb.vkCode

                # Hotkey: Pause / Break key toggles active status
                if vk == 0x13:  # VK_PAUSE
                    self._is_paused = not self._is_paused
                    status = "PAUSED" if self._is_paused else "ACTIVE"
                    log_event(f"[HOTKEY] Pause/Break pressed. Status: {status}")
                    if self.on_status_callback:
                        try:
                            self.on_status_callback(self._is_paused)
                        except Exception:
                            pass
                    return 1

                if not self._is_paused:
                    active_proc = self.get_active_process_name()
                    active_hwnd = self.user32.GetForegroundWindow() if self.user32 else 0

                    if vk == VK_BACK:
                        # Handle Backspace for Instant Undo
                        act = self.engine.process_key("", is_backspace=True, active_process=active_proc)
                        if act.action_type == "INSTANT_UNDO":
                            log_event(f"[INSTANT_UNDO] Restored: '{act.replacement_text}' (Layout: {act.target_layout})")
                            if self.on_switch_callback:
                                try:
                                    self.on_switch_callback(
                                        "INSTANT_UNDO",
                                        act.original_text,
                                        act.replacement_text,
                                        act.target_layout,
                                        active_proc,
                                    )
                                except Exception:
                                    pass
                            # Perform undo: delete replaced word, re-type original, switch layout
                            self.platform.replace_text_atomic(len(act.original_text), act.replacement_text)
                            try:
                                self.platform.switch_layout(act.target_layout, hwnd=active_hwnd)
                            except TypeError:
                                self.platform.switch_layout(act.target_layout)
                            return 1  # Suppress the raw backspace since we handled the replacement

                    elif vk in (0x25, 0x26, 0x27, 0x28, 0x2E, 0x1B):  # Arrow keys, Delete, Escape
                        # Cursor movement flushes current buffer
                        self.engine._current_token = ""
                        self.engine._chars_since_delimiter = 0

                    else:
                        char = self._vk_to_char(vk, kb.scanCode)
                        if char and len(char) == 1 and (char.isprintable() or char in " \t\n\r"):
                            # Deterministic layout synchronization directly from character!
                            if any("\u0e00" <= c <= "\u0e7f" for c in char):
                                if self.engine.current_layout != "TH":
                                    self.engine.set_layout("TH")
                            elif any("a" <= c <= "z" or "A" <= c <= "Z" or c in ";[]',./-" for c in char):
                                if self.engine.current_layout != "EN":
                                    self.engine.set_layout("EN")

                            act = self.engine.process_key(char, is_backspace=False, active_process=active_proc)

                            if act.action_type == "AUTO_SWITCH":
                                try:
                                    print(
                                        f"\n[AUTO_SWITCH] Process: {active_proc} | "
                                        f"'{act.original_text}' -> '{act.replacement_text}' | "
                                        f"New Layout: {act.target_layout} (Conf: {act.confidence:.2f})"
                                    )
                                except Exception:
                                    pass
                                if self.on_switch_callback:
                                    try:
                                        self.on_switch_callback(
                                            "AUTO_SWITCH",
                                            act.original_text,
                                            act.replacement_text,
                                            act.target_layout,
                                            active_proc,
                                        )
                                    except Exception:
                                        pass

                                # Execute replacement in worker thread after letting the last key land
                                orig_len = len(act.original_text)
                                repl = act.replacement_text
                                tgt = act.target_layout
                                is_delim = getattr(act, "is_delimiter", False)
                                delim_ch = getattr(act, "delimiter_char", "")

                                # If triggered on delimiter (e.g. space), the delimiter has already landed on screen
                                if is_delim:
                                    orig_len += len(delim_ch) if delim_ch else 1
                                    repl = repl + (delim_ch if delim_ch else char)

                                log_event(
                                    f"[AUTO_SWITCH] Proc: {active_proc} | "
                                    f"'{act.original_text}' -> '{act.replacement_text}' | "
                                    f"New Layout: {tgt} (Conf: {act.confidence:.2f}, is_delim={is_delim})"
                                )

                                def do_replace():
                                    time.sleep(0.015)
                                    self.platform.replace_text_atomic(orig_len, repl)
                                    try:
                                        self.platform.switch_layout(tgt, hwnd=active_hwnd)
                                    except TypeError:
                                        self.platform.switch_layout(tgt)

                                threading.Thread(target=do_replace, daemon=True).start()
                                return self.user32.CallNextHookEx(self._hook, nCode, wParam, lParam)
        except Exception as e:
            log_event(f"[HOOK_EXCEPTION] Exception in _on_keyboard_event: {e}")

        return self.user32.CallNextHookEx(self._hook, nCode, wParam, lParam)

    def start(self) -> None:
        """Installs the keyboard hook and enters the Windows message pump."""
        print("=" * 70)
        print("  SMART KEYBOARD - REAL-TIME LIVE DAEMON (CHA ENGINE)")
        print("=" * 70)
        print("  Status: RUNNING")
        print("  - Automatic Layout Switching: ACTIVE")
        print("  - Asymmetric Dev Tool Protection: ACTIVE (VS Code, Terminal protected)")
        print("  - Instant Undo: ACTIVE (Hit Backspace within 2.5s to revert)")
        print("  - Toggle Pause/Resume: Press 'Pause/Break' key")
        print("  - Stop Service: Press Ctrl+C in this console")
        print("=" * 70)

        self._thread_id = self.kernel32.GetCurrentThreadId()
        self._hook_proc = HOOKPROC(self._on_keyboard_event)

        # On 64-bit Windows in Python, hMod must be 0 for global WH_KEYBOARD_LL hook
        self._hook = self.user32.SetWindowsHookExW(
            WH_KEYBOARD_LL, self._hook_proc, 0, 0
        )

        if not self._hook:
            hMod = self.kernel32.GetModuleHandleW(None)
            self._hook = self.user32.SetWindowsHookExW(
                WH_KEYBOARD_LL, self._hook_proc, hMod, 0
            )

        if not self._hook:
            err = self.kernel32.GetLastError()
            log_event(f"[HOOK_ERROR] Failed to install WH_KEYBOARD_LL hook (Win32 Error: {err})")
            print(f"[ERROR] Failed to install WH_KEYBOARD_LL hook (Win32 Error: {err}). Please run with adequate privileges.")
            return

        log_event(f"[HOOK_SUCCESS] Keyboard hook installed successfully (handle={self._hook})")
        print("[OK] Keyboard hook installed successfully. Start typing anywhere!\n")

        try:
            msg = wintypes.MSG()
            while self.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) > 0:
                self.user32.TranslateMessage(ctypes.byref(msg))
                self.user32.DispatchMessageW(ctypes.byref(msg))
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()

    def stop(self) -> None:
        """Uninstalls the hook and exits cleanly."""
        if self._hook:
            self.user32.UnhookWindowsHookEx(self._hook)
            self._hook = None
            log_event("[HOOK_UNHOOKED] Keyboard hook uninstalled cleanly.")
            print("\n[OK] Keyboard hook uninstalled cleanly. Goodbye!")
        if self._thread_id:
            self.user32.PostThreadMessageW(self._thread_id, 0x0012, 0, 0)
            self._thread_id = 0


def main():
    service = LiveKeyboardService()
    service.start()


if __name__ == "__main__":
    main()
