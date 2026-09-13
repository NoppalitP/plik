"""Unit tests for Kedmanee layout bidirectional mapping."""

import pytest
from plik.layouts.kedmanee import to_english, to_thai


def test_thai_to_english_basic():
    # 'แบบ' on Kedmanee is 'c[['
    assert to_english("แบบ") == "c[["
    # 'สวัสดี' is 'l;ylfu'
    assert to_english("สวัสดี") == "l;ylfu"
    # 'ภาษา' is '4kKk'
    assert to_english("ภาษา") == "4kKk"


def test_english_to_thai_basic():
    assert to_thai("c[[") == "แบบ"
    assert to_thai("l;ylfu") == "สวัสดี"
    assert to_thai("4kKk") == "ภาษา"
    assert to_thai("apple") == "ฟยยสำ"


def test_bidirectional_invariance():
    samples = [
        "c[[",
        "l;ylfu",
        "4kKk",
        "gmLk",
        "12345",
    ]
    for sample in samples:
        thai = to_thai(sample)
        en = to_english(thai)
        assert en == sample, f"Failed roundtrip for {sample}: {thai} -> {en}"
