"""Unit tests for AdaptiveMemory and Negative Feedback."""

import pytest
from plik.engine.adaptive_memory import AdaptiveMemory


def test_adaptive_memory_negative_feedback():
    mem = AdaptiveMemory()
    token = "customtechword"

    assert not mem.is_suppressed(token)

    # User undoes conversion
    mem.record_negative_feedback(token, "chrome.exe")

    # Now it must be suppressed globally and for chrome.exe
    assert mem.is_suppressed(token)
    assert mem.is_suppressed(token, "chrome.exe")
    assert mem.is_suppressed("CUSTOMTECHWORD")  # Case insensitive


def test_adaptive_memory_clear():
    mem = AdaptiveMemory()
    mem.record_negative_feedback("testword")
    assert mem.is_suppressed("testword")

    mem.clear()
    assert not mem.is_suppressed("testword")
