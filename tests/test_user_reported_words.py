"""Comprehensive unit tests for user-reported words and non-chopping guarantees."""

import pytest
from plik.engine.core import CoreEngine


def test_user_reported_words_delimiter_mode():
    """Verify all words reported by the user convert with 100% precision in delimiter mode."""
    test_cases = [
        ("cotoe ", "แนะนำ", "TH"),
        ("de]y' ", "กำลัง", "TH"),
        ("vtwi ", "อะไร", "TH"),
        ("l;ylfu8iy[ ", "สวัสดีครับ", "TH"),
        ("mew, ", "ทำไม", "TH"),
        ("siv ", "หรอ", "TH"),
        ("oujgik ", "นี่เรา", "TH"),
    ]

    for typed_seq, expected_text, expected_layout in test_cases:
        eng = CoreEngine()
        eng.config.switch_on_delimiter_only = True
        eng.set_layout("EN")

        last_action = None
        for ch in typed_seq:
            act = eng.process_key(ch, active_process="notepad.exe")
            if act.action_type == "AUTO_SWITCH":
                last_action = act

        assert last_action is not None, f"Failed to convert '{typed_seq}'"
        assert last_action.replacement_text == expected_text
        assert last_action.target_layout == expected_layout


def test_user_reported_words_in_flight_mode():
    """Verify in-flight typing converts complete words without chopping partial prefixes."""
    test_cases = [
        ("cotoe", "แนะนำ", "TH"),
        ("de]y'", "กำลัง", "TH"),
        ("vtwi", "อะไร", "TH"),
        ("mew,", "ทำไม", "TH"),
        ("siv", "หรอ", "TH"),
    ]

    for typed_seq, expected_text, expected_layout in test_cases:
        eng = CoreEngine()
        eng.config.switch_on_delimiter_only = False
        eng.set_layout("EN")

        last_action = None
        for ch in typed_seq:
            act = eng.process_key(ch, active_process="notepad.exe")
            if act.action_type == "AUTO_SWITCH":
                last_action = act

        assert last_action is not None, f"Failed to convert in-flight '{typed_seq}'"
        assert last_action.replacement_text == expected_text
        assert last_action.target_layout == expected_layout


def test_thai_to_english_contractions():
    """Verify Thai Kedmanee keys convert to English contractions (ระงห -> it's)."""
    eng = CoreEngine()
    eng.set_layout("TH")

    last_action = None
    for ch in "ระงห ":
        act = eng.process_key(ch, active_process="notepad.exe")
        if act.action_type == "AUTO_SWITCH":
            last_action = act

    assert last_action is not None
    assert last_action.replacement_text == "it's"
    assert last_action.target_layout == "EN"


def test_in_flight_never_chops_partial_syllables():
    """Verify that prefixes of longer words are never prematurely chopped in-flight."""
    eng = CoreEngine()
    eng.config.switch_on_delimiter_only = False
    eng.set_layout("EN")

    # Typing 'de]' (กำล) - must NOT trigger AUTO_SWITCH!
    for ch in "de]":
        act = eng.process_key(ch, active_process="notepad.exe")
        assert act.action_type == "NONE", f"Prefix 'de]' was prematurely chopped: {act}"

    # Typing 'vtw' (อะไ) - must NOT trigger AUTO_SWITCH!
    eng.set_layout("EN")
    for ch in "vtw":
        act = eng.process_key(ch, active_process="notepad.exe")
        assert act.action_type == "NONE", f"Prefix 'vtw' was prematurely chopped: {act}"

    # Typing '.od' (ในก) - must NOT trigger AUTO_SWITCH!
    eng.set_layout("EN")
    for ch in ".od":
        act = eng.process_key(ch, active_process="notepad.exe")
        assert act.action_type == "NONE", f"Prefix '.od' was prematurely chopped: {act}"