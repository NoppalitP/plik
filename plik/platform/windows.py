"""Windows Platform Integration via native Win32 APIs (ctypes).

Handles:
- Detecting current keyboard layout (HKL) of focused child controls.
- Switching layout via AttachThreadInput + PostMessage(WM_INPUTLANGCHANGEREQUEST) + ActivateKeyboardLayout.
- Atomic text replacement via SendInput using 40-byte Win32 64-bit INPUT structures and KEYEVENTF_UNICODE.
"""

import sys
import time
from typing import Optional

# Win32 Constants
WM_INPUTLANGCHANGEREQUEST = 0x0050
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
VK_BACK = 0x08

# Thai and English Language IDs
LANG_THAI = 0x041E
LANG_ENGLISH_US = 0x0409

SMART_KEYBOARD_EXTRA_INFO = 0x534D415254  # "SMART" in hex


class WindowsPlatform:
    """Windows low-level keyboard and input manager."""

    def __init__(self):
        self._is_win32 = sys.platform == "win32"
        if self._is_win32:
            import ctypes
            from ctypes import wintypes
            self._ctypes = ctypes
            self._wintypes = wintypes
            self._user32 = ctypes.windll.user32
            self._kernel32 = ctypes.windll.kernel32

            # Configure explicit 64-bit Win32 API signatures
            self._user32.SendInput.restype = wintypes.UINT
            self._user32.SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]

            self._user32.LoadKeyboardLayoutW.restype = wintypes.HKL
            self._user32.LoadKeyboardLayoutW.argtypes = [wintypes.LPCWSTR, wintypes.UINT]

            self._user32.PostMessageW.restype = wintypes.BOOL
            self._user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]

            self._user32.ActivateKeyboardLayout.restype = wintypes.HKL
            self._user32.ActivateKeyboardLayout.argtypes = [wintypes.HKL, wintypes.UINT]

            self._user32.GetForegroundWindow.restype = wintypes.HWND
            self._user32.GetForegroundWindow.argtypes = []

            self._user32.GetWindowThreadProcessId.restype = wintypes.DWORD
            self._user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]

            self._user32.GetKeyboardLayout.restype = wintypes.HKL
            self._user32.GetKeyboardLayout.argtypes = [wintypes.DWORD]

            self._user32.MapVirtualKeyW.restype = wintypes.UINT
            self._user32.MapVirtualKeyW.argtypes = [wintypes.UINT, wintypes.UINT]

            self._user32.AttachThreadInput.restype = wintypes.BOOL
            self._user32.AttachThreadInput.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.BOOL]

            self._kernel32.GetCurrentThreadId.restype = wintypes.DWORD
            self._kernel32.GetCurrentThreadId.argtypes = []

            self._kernel32.GetLastError.restype = wintypes.DWORD
            self._kernel32.GetLastError.argtypes = []
        else:
            self._ctypes = None
            self._wintypes = None
            self._user32 = None
            self._kernel32 = None

    def get_focused_window(self):
        """Finds the actual focused child control window where text input lands."""
        if not self._is_win32:
            return 0
        try:
            hwnd_fore = self._user32.GetForegroundWindow()
            if not hwnd_fore:
                return 0
            thread_id = self._user32.GetWindowThreadProcessId(hwnd_fore, None)
            if not thread_id:
                return hwnd_fore

            ctypes = self._ctypes
            wintypes = self._wintypes

            class GUITHREADINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("flags", wintypes.DWORD),
                    ("hwndActive", wintypes.HWND),
                    ("hwndFocus", wintypes.HWND),
                    ("hwndCapture", wintypes.HWND),
                    ("hwndMenuOwner", wintypes.HWND),
                    ("hwndMoveSize", wintypes.HWND),
                    ("hwndCaret", wintypes.HWND),
                    ("rcCaret", wintypes.RECT),
                ]

            gui = GUITHREADINFO()
            gui.cbSize = ctypes.sizeof(GUITHREADINFO)
            self._user32.GetGUIThreadInfo.argtypes = [wintypes.DWORD, ctypes.POINTER(GUITHREADINFO)]
            self._user32.GetGUIThreadInfo.restype = wintypes.BOOL

            if self._user32.GetGUIThreadInfo(thread_id, ctypes.byref(gui)):
                if gui.hwndFocus:
                    return gui.hwndFocus
            return hwnd_fore
        except Exception:
            return self._user32.GetForegroundWindow() if self._user32 else 0

    def get_current_layout(self) -> str:
        """Return 'TH' or 'EN' based on active window's keyboard layout."""
        if not self._is_win32:
            return "EN"

        try:
            hwnd = self.get_focused_window()
            thread_id = self._user32.GetWindowThreadProcessId(hwnd, None) if hwnd else 0
            hkl = self._user32.GetKeyboardLayout(thread_id)
            lang_id = hkl & 0xFFFF
            if lang_id == LANG_THAI:
                return "TH"
            return "EN"
        except Exception:
            return "EN"

    def switch_layout(self, target: str, hwnd: Optional[int] = None) -> bool:
        """Switch active window layout to 'TH' or 'EN' with thread attachment."""
        if not self._is_win32:
            return True

        try:
            target_hwnd = hwnd or self.get_focused_window() or (self._user32.GetForegroundWindow() if self._user32 else 0)
            if not target_hwnd:
                return False
            hwnd_focus = self.get_focused_window() or target_hwnd
            hwnd_fore = (self._user32.GetForegroundWindow() if self._user32 else 0) or target_hwnd

            target_tid = self._user32.GetWindowThreadProcessId(target_hwnd, None)
            current_tid = self._kernel32.GetCurrentThreadId()

            hkl_str = "0000041E" if target.upper() == "TH" else "00000409"
            hkl = self._user32.LoadKeyboardLayoutW(hkl_str, 1)  # KLF_ACTIVATE = 1
            if not hkl:
                return False

            attached = False
            if target_tid and target_tid != current_tid:
                attached = bool(self._user32.AttachThreadInput(current_tid, target_tid, True))

            try:
                # 1. Post to focused window
                if hwnd_focus:
                    self._user32.PostMessageW(hwnd_focus, WM_INPUTLANGCHANGEREQUEST, 0, hkl)
                # 2. Post to top-level window
                if hwnd_fore and hwnd_fore != hwnd_focus:
                    self._user32.PostMessageW(hwnd_fore, WM_INPUTLANGCHANGEREQUEST, 0, hkl)
                # 3. Activate layout
                self._user32.ActivateKeyboardLayout(hkl, 0)
            finally:
                if attached:
                    self._user32.AttachThreadInput(current_tid, target_tid, False)

            return True
        except Exception:
            return False

    def replace_text_atomic(self, num_backspaces: int, replacement_text: str) -> None:
        """Delete previous characters and type replacement using complete 40-byte Win32 INPUT structures.
        
        Using KEYEVENTF_UNICODE ensures that the inserted characters are NOT
        garbled by whatever layout the target application currently has active.
        """
        if not self._is_win32:
            return

        import ctypes
        from ctypes import wintypes

        class MOUSEINPUT(ctypes.Structure):
            _fields_ = [
                ("dx", wintypes.LONG),
                ("dy", wintypes.LONG),
                ("mouseData", wintypes.DWORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_ulonglong),
            ]

        class KEYBDINPUT(ctypes.Structure):
            _fields_ = [
                ("wVk", wintypes.WORD),
                ("wScan", wintypes.WORD),
                ("dwFlags", wintypes.DWORD),
                ("time", wintypes.DWORD),
                ("dwExtraInfo", ctypes.c_ulonglong),
            ]

        class HARDWAREINPUT(ctypes.Structure):
            _fields_ = [
                ("uMsg", wintypes.DWORD),
                ("wParamL", wintypes.WORD),
                ("wParamH", wintypes.WORD),
            ]

        class INPUT(ctypes.Structure):
            class _INPUT(ctypes.Union):
                _fields_ = [
                    ("mi", MOUSEINPUT),
                    ("ki", KEYBDINPUT),
                    ("hi", HARDWAREINPUT),
                ]
            _anonymous_ = ("_input",)
            _fields_ = [("type", wintypes.DWORD), ("_input", _INPUT)]

        bs_inputs = []
        scan_back = self._user32.MapVirtualKeyW(VK_BACK, 0) if self._user32 else 14

        # 1. Backspaces to remove old text
        for _ in range(num_backspaces):
            # Key down
            inp_down = INPUT(type=INPUT_KEYBOARD)
            inp_down.ki.wVk = VK_BACK
            inp_down.ki.wScan = scan_back
            inp_down.ki.dwFlags = 0
            inp_down.ki.dwExtraInfo = SMART_KEYBOARD_EXTRA_INFO
            bs_inputs.append(inp_down)

            # Key up
            inp_up = INPUT(type=INPUT_KEYBOARD)
            inp_up.ki.wVk = VK_BACK
            inp_up.ki.wScan = scan_back
            inp_up.ki.dwFlags = KEYEVENTF_KEYUP
            inp_up.ki.dwExtraInfo = SMART_KEYBOARD_EXTRA_INFO
            bs_inputs.append(inp_up)

        if bs_inputs:
            n_bs = len(bs_inputs)
            arr_bs = (INPUT * n_bs)(*bs_inputs)
            self._user32.SendInput(n_bs, ctypes.byref(arr_bs), ctypes.sizeof(INPUT))
            # Micro-pause allows target app message queue to process deletions before insertions
            time.sleep(0.005)

        # 2. Unicode characters for replacement
        char_inputs = []
        for ch in replacement_text:
            code = ord(ch)
            # Key down
            inp_down = INPUT(type=INPUT_KEYBOARD)
            inp_down.ki.wVk = 0
            inp_down.ki.wScan = code
            inp_down.ki.dwFlags = KEYEVENTF_UNICODE
            inp_down.ki.dwExtraInfo = SMART_KEYBOARD_EXTRA_INFO
            char_inputs.append(inp_down)

            # Key up
            inp_up = INPUT(type=INPUT_KEYBOARD)
            inp_up.ki.wVk = 0
            inp_up.ki.wScan = code
            inp_up.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP
            inp_up.ki.dwExtraInfo = SMART_KEYBOARD_EXTRA_INFO
            char_inputs.append(inp_up)

        if char_inputs:
            n_ch = len(char_inputs)
            arr_ch = (INPUT * n_ch)(*char_inputs)
            self._user32.SendInput(n_ch, ctypes.byref(arr_ch), ctypes.sizeof(INPUT))
