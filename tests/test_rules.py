"""Unit tests for Tier 1 phonotactic and syntactic rules."""

import pytest
from plik.engine.rules import (
    check_tier1_rules,
    is_impossible_english,
    is_impossible_thai,
)


def test_impossible_thai_starters():
    # Words starting with diacritics
    bad_starters = ["ัำห", "ิพำ", "่ก", "้มา", "์ร", "ะำหะ"]
    for word in bad_starters:
        is_bad, reason = is_impossible_thai(word)
        assert is_bad, f"Expected '{word}' to be invalid Thai, but passed. Reason: {reason}"


def test_impossible_thai_consecutive_diacritics():
    # Double upper vowel or tone mark
    invalid_combos = ["ก้่", "กิี", "กุู", "เ่ก", "กะ่", "ก์ิ"]
    for combo in invalid_combos:
        is_bad, _ = is_impossible_thai(combo)
        assert is_bad, f"Expected '{combo}' to be invalid Thai"


def test_valid_thai_words():
    valid_words = ["สวัสดี", "ภาษา", "แบบ", "ทำงาน", "วันนี้", "การ", "ความ"]
    for word in valid_words:
        is_bad, _ = is_impossible_thai(word)
        assert not is_bad, f"Expected '{word}' to be valid Thai"


def test_impossible_english_syntax():
    # Semicolon in middle of word
    is_bad, _ = is_impossible_english("d;y")
    assert is_bad
    # Brackets in word
    is_bad, _ = is_impossible_english("c[[")
    assert is_bad
    # Consonants with shifted Kedmanee capitals and no vowels
    is_bad, _ = is_impossible_english("4kKk")
    assert is_bad
    is_bad, _ = is_impossible_english("gmLk")
    assert is_bad


def test_valid_english_syntax():
    valid_words = ["apple", "banana", "function", "variable", "status", "commit"]
    for word in valid_words:
        is_bad, _ = is_impossible_english(word)
        assert not is_bad, f"Expected '{word}' to be valid English"


def test_check_tier1_rules():
    assert check_tier1_rules("ัำห", "TH") == "SWITCH_TO_EN"
    assert check_tier1_rules("d;y", "EN") == "SWITCH_TO_TH"
    assert check_tier1_rules("c[[", "EN") == "SWITCH_TO_TH"
    assert check_tier1_rules("hello", "EN") is None
    assert check_tier1_rules("สวัสดี", "TH") is None
