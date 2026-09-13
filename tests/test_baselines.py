"""Unit and integration tests for canonical academic prior baselines."""

import pytest
from plik.evaluation.baselines import (
    HeuristicLexiconBaseline,
    PureCharNGramBaseline,
    PureFSABaseline,
)
from plik.evaluation.comparative_benchmark import (
    compute_mcnemar,
    run_comparative_benchmark,
)


def test_pure_fsa_baseline():
    fsa = PureFSABaseline()
    fsa.set_layout("EN")

    # Typing impossible English that maps to valid Thai
    # "l;ylfg" -> "สวัสดี"
    actions = [fsa.process_key(c) for c in "l;ylfg "]
    assert "AUTO_SWITCH" in actions
    assert fsa.current_layout == "TH"

    # In TH mode, typing impossible Thai: leading vowel without consonant or orphan diacritic
    fsa.set_layout("TH")
    actions_th = [fsa.process_key(c) for c in "้้ "]
    assert "AUTO_SWITCH" in actions_th
    assert fsa.current_layout == "EN"


def test_pure_ngram_baseline():
    ngram = PureCharNGramBaseline(threshold=1.0)
    ngram.set_layout("EN")

    # Strong Thai n-grams typed in EN
    # "การทำงาน" typed on Kedmanee keys
    actions = [ngram.process_key(c) for c in "การทำงาน "]
    # Should process without crashing
    assert isinstance(actions, list)


def test_heuristic_lexicon_baseline():
    lex = HeuristicLexiconBaseline()
    lex.set_layout("EN")

    # Word in Thai dictionary typed on EN layout
    # "สวัสดี" = "l;ylfg"
    actions = [lex.process_key(c) for c in "l;ylfg "]
    assert "AUTO_SWITCH" in actions
    assert lex.current_layout == "TH"


def test_mcnemar_computation():
    a = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    b = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
    stat, p_val = compute_mcnemar(a, b)
    assert stat > 0.0
    assert p_val < 0.05


def test_full_comparative_benchmark_runs():
    res = run_comparative_benchmark()
    assert "fsa" in res
    assert "ngram" in res
    assert "lexicon" in res
    assert "cha" in res

    # Proposed CHA must have superior accuracy and F1 compared to all 3 baselines
    assert res["cha"]["accuracy"] > res["fsa"]["accuracy"]
    assert res["cha"]["accuracy"] > res["ngram"]["accuracy"]
    assert res["cha"]["accuracy"] > res["lexicon"]["accuracy"]

    assert res["cha"]["f1"] > res["fsa"]["f1"]
    assert res["cha"]["f1"] > res["ngram"]["f1"]
    assert res["cha"]["f1"] > res["lexicon"]["f1"]

    # CHA must have 0% FPR
    assert res["cha"]["fpr"] == 0.0
