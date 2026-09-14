"""Unit tests for Core Decision Engine and Instant Undo."""

import pytest
from plik.config import SwitcherConfig
from plik.engine.app_context import AppCategory, AppContextManager
from plik.engine.core import CoreEngine


def test_core_engine_auto_switch():
    engine = CoreEngine()
    engine.set_layout("EN")

    # Type ';', 'y', 'o' -> 'วัน' (valid 3-char Thai word with semicolon)
    engine.process_key(";", active_process="chrome.exe")
    engine.process_key("y", active_process="chrome.exe")
    act = engine.process_key("o", active_process="chrome.exe")

    assert act.action_type == "AUTO_SWITCH"
    assert act.replacement_text == "วัน"
    assert act.target_layout == "TH"
    assert engine.current_layout == "TH"


def test_core_engine_instant_undo():
    engine = CoreEngine()
    engine.set_layout("EN")

    # Trigger switch on 'c[[' -> 'แบบ'
    engine.process_key("c", active_process="chrome.exe")
    engine.process_key("[", active_process="chrome.exe")
    act1 = engine.process_key("[", active_process="chrome.exe")
    assert act1.action_type == "AUTO_SWITCH"
    assert act1.replacement_text == "แบบ"

    # Press backspace immediately
    undo_act = engine.process_key("", is_backspace=True, active_process="chrome.exe")
    assert undo_act.action_type == "INSTANT_UNDO"
    assert undo_act.replacement_text == "c[["
    assert undo_act.target_layout == "EN"
    assert engine.current_layout == "EN"


def test_core_engine_dev_process_protection():
    engine = CoreEngine()
    engine.set_layout("EN")

    # Typing 'd;y' in VS Code should NOT auto-switch
    engine.process_key("d", active_process="code.exe")
    engine.process_key(";", active_process="code.exe")
    act = engine.process_key("y", active_process="code.exe")

    assert act.action_type == "NONE"
    assert engine.current_layout == "EN"


def test_core_engine_manual_convert():
    engine = CoreEngine()
    engine.set_layout("EN")

    # In dev tool, manual convert must still work!
    engine.process_key("d", active_process="code.exe")
    engine.process_key(";", active_process="code.exe")
    engine.process_key("y", active_process="code.exe")

    manual_act = engine.manual_convert()
    assert manual_act.action_type == "MANUAL_CONVERT"
    assert manual_act.replacement_text == "กวั"
    assert manual_act.target_layout == "TH"
    assert engine.current_layout == "TH"


def test_core_engine_protected_tokens():
    engine = CoreEngine()
    engine.set_layout("EN")

    # '555' is protected
    for ch in "555 ":
        act = engine.process_key(ch, active_process="line.exe")
        assert act.action_type == "NONE"

    # 'api' is protected
    for ch in "api ":
        act = engine.process_key(ch, active_process="chrome.exe")
        assert act.action_type == "NONE"
