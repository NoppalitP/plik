"""Unit tests for Smart Keyboard Production Features: Settings & Mutex."""

import os
import tempfile
import pytest
from plik.storage import AppSettings, SettingsManager
from plik.tray_app import SingleInstanceMutex, get_asset_path


def test_settings_save_and_load_roundtrip():
    """Verify settings save and load accurately with atomic persistence."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test_settings.json")
        mgr = SettingsManager(custom_path=test_file)

        # Default settings
        assert mgr.settings.is_paused is False
        assert mgr.settings.enable_autocorrect is True

        # Modify and save
        mgr.settings.is_paused = True
        mgr.settings.enable_autocorrect = False
        assert mgr.save() is True

        # Reload from fresh manager
        mgr2 = SettingsManager(custom_path=test_file)
        assert mgr2.settings.is_paused is True
        assert mgr2.settings.enable_autocorrect is False
        assert mgr2.settings.enable_thai_autocorrect is True
        assert mgr2.settings.enable_eng_autocorrect is True


def test_settings_corrupted_fallback():
    """Verify corrupted JSON gracefully falls back to default settings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "bad_settings.json")
        with open(test_file, "w", encoding="utf-8") as f:
            f.write("{invalid_json: true,")

        mgr = SettingsManager(custom_path=test_file)
        assert mgr.settings.is_paused is False
        assert mgr.settings.enable_autocorrect is True


def test_single_instance_mutex_collision_detection():
    """Verify mutex detects dual instances with identical name."""
    test_mutex_name = "Local\\TestSmartKeyboardMutex_UnitTest"

    m1 = SingleInstanceMutex(mutex_name=test_mutex_name)
    try:
        assert m1.already_running is False

        # Attempting second instance should detect collision
        m2 = SingleInstanceMutex(mutex_name=test_mutex_name)
        try:
            assert m2.already_running is True
        finally:
            m2.release()
    finally:
        m1.release()


def test_app_icon_asset_exists():
    """Verify production app_icon.ico exists and is resolvable."""
    ico_path = get_asset_path("app_icon.ico")
    assert os.path.exists(ico_path), f"Asset missing at {ico_path}"
    assert os.path.getsize(ico_path) > 1000, "Icon file appears empty or corrupted"
