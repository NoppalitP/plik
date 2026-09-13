"""Tests for LiveKeyboardService Win32 hook and runtime integration."""

import ctypes
import time
import pytest

from plik.live_service import (
    LiveKeyboardService,
    KBDLLHOOKSTRUCT,
    WM_KEYDOWN,
    SMART_KEYBOARD_EXTRA_INFO,
    LLKHF_INJECTED,
)


def test_live_service_init_signatures():
    """Verify that Win32 function signatures are explicitly set for 64-bit stability."""
    service = LiveKeyboardService()
    assert service.user32.CallNextHookEx.argtypes is not None
    assert service.user32.SetWindowsHookExW.argtypes is not None
    assert service.user32.ToUnicodeEx.argtypes is not None


def test_live_service_simulated_switch_and_undo():
    """Verify end-to-end event handling: typing ;yo -> วัน -> Backspace -> undo."""
    switches = []

    def on_switch(act_type, orig, repl, target, proc):
        switches.append((act_type, orig, repl, target))

    service = LiveKeyboardService(on_switch_callback=on_switch)

    # Mock low-level layout translation
    char_map = {0xBA: ";", 0x59: "y", 0x4F: "o"}
    service._vk_to_char = lambda vk, sc: char_map.get(vk)
    service.get_active_process_name = lambda: "notepad.exe"

    current_os_layout = ["EN"]
    service.platform.get_current_layout = lambda: current_os_layout[0]

    replaced = []
    switched = []

    def mock_replace(n, s):
        replaced.append((n, s))

    def mock_switch(l):
        switched.append(l)
        current_os_layout[0] = l

    service.platform.replace_text_atomic = mock_replace
    service.platform.switch_layout = mock_switch

    # 1. Simulate typing ; y o (which maps to วัน in Thai)
    for vk in [0xBA, 0x59, 0x4F]:
        kb = KBDLLHOOKSTRUCT(vk, 0, 0, 0, 0)
        service._on_keyboard_event(0, WM_KEYDOWN, ctypes.addressof(kb))

    time.sleep(0.05)  # Wait for worker thread

    assert len(switches) == 1
    assert switches[0] == ("AUTO_SWITCH", ";yo", "วัน", "TH")
    assert replaced == [(3, "วัน")]
    assert current_os_layout[0] == "TH"

    # 2. Simulate Instant Undo (Backspace within 2.5s)
    kb_back = KBDLLHOOKSTRUCT(0x08, 0, 0, 0, 0)
    res = service._on_keyboard_event(0, WM_KEYDOWN, ctypes.addressof(kb_back))

    assert res == 1  # Suppressed raw backspace
    assert len(switches) == 2
    assert switches[1] == ("INSTANT_UNDO", "วัน", ";yo", "EN")
    assert replaced == [(3, "วัน"), (3, ";yo")]
    assert current_os_layout[0] == "EN"


def test_live_service_pause_toggle():
    """Verify VK_PAUSE key toggles service paused state."""
    service = LiveKeyboardService()
    assert service._is_paused is False

    # Press VK_PAUSE
    kb_pause = KBDLLHOOKSTRUCT(0x13, 0, 0, 0, 0)
    res = service._on_keyboard_event(0, WM_KEYDOWN, ctypes.addressof(kb_pause))
    assert res == 1
    assert service._is_paused is True

    # Press VK_PAUSE again to resume
    res = service._on_keyboard_event(0, WM_KEYDOWN, ctypes.addressof(kb_pause))
    assert res == 1
    assert service._is_paused is False


def test_live_service_ignores_injected_keystrokes():
    """Verify that keystrokes injected by SendInput are safely ignored."""
    service = LiveKeyboardService()
    switches = []
    service.on_switch_callback = lambda *args: switches.append(args)

    # Injected via flag
    kb_injected = KBDLLHOOKSTRUCT(0x41, 0, LLKHF_INJECTED, 0, 0)
    service._on_keyboard_event(0, WM_KEYDOWN, ctypes.addressof(kb_injected))

    # Injected via extra info marker
    kb_marker = KBDLLHOOKSTRUCT(0x41, 0, 0, 0, SMART_KEYBOARD_EXTRA_INFO)
    service._on_keyboard_event(0, WM_KEYDOWN, ctypes.addressof(kb_marker))

    assert len(switches) == 0
