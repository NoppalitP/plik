"""Tests for Sound Alert functionality in Plik."""

import os
import tempfile
import time
import pytest
from unittest.mock import MagicMock, patch

from plik.config import SwitcherConfig
from plik.storage import AppSettings, SettingsManager
from plik.live_service import LiveKeyboardService, KBDLLHOOKSTRUCT, WM_KEYDOWN


def test_config_sound_alert_default():
    """Verify default enable_sound_alert is True."""
    cfg = SwitcherConfig()
    assert cfg.enable_sound_alert is True


def test_storage_sound_alert_persistence():
    """Verify sound alert setting persists across save and load cycles."""
    with tempfile.TemporaryDirectory() as tmpdir:
        settings_file = os.path.join(tmpdir, 'settings.json')
        mgr = SettingsManager(custom_path=settings_file)
        assert mgr.settings.enable_sound_alert is True

        # Toggle off and save
        mgr.settings.enable_sound_alert = False
        mgr.save()

        # Reload from disk
        mgr2 = SettingsManager(custom_path=settings_file)
        assert mgr2.settings.enable_sound_alert is False


def test_live_service_sound_played_on_auto_switch():
    """Verify _play_switch_sound is called when auto-switching with enable_sound_alert=True."""
    service = LiveKeyboardService()
    service.config.enable_sound_alert = True
    service.platform.replace_text_atomic = MagicMock()
    service.platform.switch_layout = MagicMock()

    sound_called = []
    service._play_switch_sound = lambda: sound_called.append(True)

    char_map = {0xBA: ';', 0x59: 'y', 0x4F: 'o'}
    service._vk_to_char = lambda vk, sc: char_map.get(vk)
    service.get_active_process_name = lambda: 'notepad.exe'

    import ctypes
    for vk in [0xBA, 0x59, 0x4F]:
        kb = KBDLLHOOKSTRUCT(vk, 0, 0, 0, 0)
        service._on_keyboard_event(0, WM_KEYDOWN, ctypes.addressof(kb))

    time.sleep(0.06)
    assert len(sound_called) == 1


def test_live_service_sound_not_played_when_disabled():
    """Verify _play_switch_sound is NOT called when enable_sound_alert=False."""
    service = LiveKeyboardService()
    service.config.enable_sound_alert = False
    service.platform.replace_text_atomic = MagicMock()
    service.platform.switch_layout = MagicMock()

    sound_called = []
    service._play_switch_sound = lambda: sound_called.append(True)

    char_map = {0xBA: ';', 0x59: 'y', 0x4F: 'o'}
    service._vk_to_char = lambda vk, sc: char_map.get(vk)
    service.get_active_process_name = lambda: 'notepad.exe'

    import ctypes
    for vk in [0xBA, 0x59, 0x4F]:
        kb = KBDLLHOOKSTRUCT(vk, 0, 0, 0, 0)
        service._on_keyboard_event(0, WM_KEYDOWN, ctypes.addressof(kb))

    time.sleep(0.06)
    assert len(sound_called) == 0


def test_live_service_play_sound_graceful_fallback():
    """Verify _play_switch_sound does_not_raise even if winsound is missing or fails."""
    service = LiveKeyboardService()
    service._play_switch_sound()


def test_live_service_toggle_sound_alert():
    """Verify toggle_sound_alert flips the boolean state."""
    service = LiveKeyboardService()
    service.config.enable_sound_alert = True
    assert service.toggle_sound_alert() is False
    assert service.config.enable_sound_alert is False
    assert service.toggle_sound_alert() is True
    assert service.config.enable_sound_alert is True
