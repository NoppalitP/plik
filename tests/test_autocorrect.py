"""Unit tests for Auto-Correction (แก้คำผิด) in Smart Keyboard."""

import time
import pytest
from plik.config import SwitcherConfig
from plik.engine.core import CoreEngine
from plik.engine.corrector import AutoCorrector


def test_autocorrector_direct_thai_typos():
    """Verify high-frequency Thai typos resolve to correct canonical spelling."""
    corrector = AutoCorrector.get_instance()

    test_cases = [
        ("นะค่ะ", "นะคะ"),
        ("กระเพรา", "กะเพรา"),
        ("สังเกตุ", "สังเกต"),
        ("อนุญาติ", "อนุญาต"),
        ("โอกาศ", "โอกาส"),
        ("ปรากฎ", "ปรากฏ"),
        ("กฏหมาย", "กฎหมาย"),
        ("เซ็นต์ชื่อ", "เซ็นชื่อ"),
        ("ออฟฟิต", "ออฟฟิศ"),
        ("อินเตอร์เน็ท", "อินเทอร์เน็ต"),
        ("คอมเม้น", "คอมเมนต์"),
        ("แอพ", "แอป"),
        ("ผัดกระเพรา", "ผัดกะเพรา"),
    ]

    for typo, expected in test_cases:
        res = corrector.correct(typo, "TH")
        assert res is not None, f"Expected correction for '{typo}'"
        assert res[0] == expected, f"Got '{res[0]}', expected '{expected}'"

    # Correct words should not be touched
    assert corrector.correct("นะคะ", "TH") is None
    assert corrector.correct("สวัสดี", "TH") is None
    assert corrector.correct("กะเพรา", "TH") is None


def test_autocorrector_direct_english_typos_and_casing():
    """Verify English typos with case preservation."""
    corrector = AutoCorrector.get_instance()

    # Lowercase
    res_lower = corrector.correct("teh", "EN")
    assert res_lower is not None and res_lower[0] == "the"

    # Capitalized
    res_cap = corrector.correct("Teh", "EN")
    assert res_cap is not None and res_cap[0] == "The"

    # Uppercase
    res_upper = corrector.correct("TEH", "EN")
    assert res_upper is not None and res_upper[0] == "THE"

    # Other common words
    assert corrector.correct("recieve", "EN")[0] == "receive"
    assert corrector.correct("Recieve", "EN")[0] == "Receive"
    assert corrector.correct("seperate", "EN")[0] == "separate"
    assert corrector.correct("definately", "EN")[0] == "definitely"
    assert corrector.correct("wierd", "EN")[0] == "weird"

    # Correct words should not be touched
    assert corrector.correct("the", "EN") is None
    assert corrector.correct("receive", "EN") is None
    assert corrector.correct("apple", "EN") is None


def test_core_engine_thai_autocorrect():
    """Verify CoreEngine automatically corrects Thai typos in-flight."""
    engine = CoreEngine()
    engine.set_layout("TH")

    action = engine._evaluate_token("นะค่ะ", active_process="notepad.exe", is_delimiter=True)
    assert action.action_type == "AUTO_SWITCH"
    assert action.replacement_text == "นะคะ"
    assert action.target_layout == "TH"

    action2 = engine._evaluate_token("กระเพรา", active_process="notepad.exe", is_delimiter=True)
    assert action2.action_type == "AUTO_SWITCH"
    assert action2.replacement_text == "กะเพรา"
    assert action2.target_layout == "TH"


def test_core_engine_english_autocorrect():
    """Verify CoreEngine automatically corrects English typos in-flight."""
    engine = CoreEngine()
    engine.set_layout("EN")

    action = engine._evaluate_token("teh", active_process="notepad.exe", is_delimiter=True)
    assert action.action_type == "AUTO_SWITCH"
    assert action.replacement_text == "the"
    assert action.target_layout == "EN"

    action_cap = engine._evaluate_token("Teh", active_process="notepad.exe", is_delimiter=True)
    assert action_cap.action_type == "AUTO_SWITCH"
    assert action_cap.replacement_text == "The"
    assert action_cap.target_layout == "EN"


def test_dev_tool_immunity_for_autocorrect():
    """Verify code editors and IDEs (code.exe) are immune to auto-correction."""
    engine = CoreEngine()
    engine.set_layout("EN")

    # In VS Code, 'teh' could be an intentional variable name; it should not be corrected
    action_en = engine._evaluate_token("teh", active_process="code.exe", is_delimiter=True)
    assert action_en.action_type == "NONE"

    engine.set_layout("TH")
    action_th = engine._evaluate_token("นะค่ะ", active_process="code.exe", is_delimiter=True)
    assert action_th.action_type == "NONE"


def test_instant_undo_autocorrect():
    """Verify pressing Backspace immediately restores the original typo."""
    engine = CoreEngine()
    engine.set_layout("EN")

    # Typing 'teh '
    act = engine._evaluate_token("teh", active_process="notepad.exe", is_delimiter=True)
    assert act.action_type == "AUTO_SWITCH"
    assert act.replacement_text == "the"

    # User presses Backspace immediately: should trigger UNDO and restore 'teh'
    undo_action = engine.process_key("", is_backspace=True)
    assert undo_action.action_type == "INSTANT_UNDO"
    assert undo_action.replacement_text == "teh"


def test_config_toggles():
    """Verify config toggles for auto-correction work properly."""
    cfg = SwitcherConfig(enable_autocorrect=False)
    engine = CoreEngine(config=cfg)
    engine.set_layout("EN")

    # Disabled globally
    act1 = engine._evaluate_token("teh", active_process="notepad.exe", is_delimiter=True)
    assert act1.action_type == "NONE"

    # Enabled globally, but Thai disabled
    cfg2 = SwitcherConfig(enable_autocorrect=True, enable_thai_autocorrect=False)
    engine2 = CoreEngine(config=cfg2)
    engine2.set_layout("TH")
    act_th = engine2._evaluate_token("นะค่ะ", active_process="notepad.exe", is_delimiter=True)
    assert act_th.action_type == "NONE"

    # English still works
    engine2.set_layout("EN")
    act_en = engine2._evaluate_token("teh", active_process="notepad.exe", is_delimiter=True)
    assert act_en.action_type == "AUTO_SWITCH"
    assert act_en.replacement_text == "the"


def test_autocorrect_performance():
    """Verify O(1) hash lookup executes in < 2.0 µs per lookup."""
    corrector = AutoCorrector.get_instance()
    words = ["นะค่ะ", "the", "กระเพรา", "apple", "teh", "สังเกตุ", "recieve", "hello"]

    start = time.perf_counter()
    iterations = 50_000
    for i in range(iterations):
        w = words[i % len(words)]
        corrector.correct(w, "TH" if i % 2 == 0 else "EN")
    elapsed = time.perf_counter() - start

    avg_microsec = (elapsed / iterations) * 1_000_000
    assert avg_microsec < 2.0, f"Average lookup took {avg_microsec:.3f} µs (expected < 2.0 µs)"
