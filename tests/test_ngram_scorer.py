"""Unit tests for Tier 2 statistical N-Gram scoring engine."""

import pytest
from plik.engine.ngram_scorer import NGramScorer


def test_ngram_scorer_english_preference():
    scorer = NGramScorer()
    # English word 'apple' typed on Thai layout 'ฟยยสำ'
    target, conf, reason = scorer.evaluate_preference("ฟยยสำ", "TH")
    assert target == "EN"
    assert conf >= 0.85


def test_ngram_scorer_thai_preference():
    scorer = NGramScorer()
    # Thai word 'แบบ' typed on QWERTY 'c[['
    target, conf, reason = scorer.evaluate_preference("c[[", "EN")
    assert target == "TH"
    assert conf >= 0.85


def test_ngram_scorer_preserves_valid_words():
    scorer = NGramScorer()
    # 'test' in English should KEEP
    target, conf, _ = scorer.evaluate_preference("test", "EN")
    assert target == "KEEP"

    # 'สวัสดี' in Thai should KEEP
    target, conf, _ = scorer.evaluate_preference("สวัสดี", "TH")
    assert target == "KEEP"
