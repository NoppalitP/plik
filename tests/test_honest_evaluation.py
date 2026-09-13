"""Pytest integration for honest out-of-distribution evaluation."""

import pytest
from plik.evaluation.evaluator import run_honest_evaluation


def test_honest_evaluation_metrics():
    res = run_honest_evaluation()

    # 1. Precision must exceed 95%
    assert res["precision"] >= 0.95, f"Precision too low: {res['precision']:.4f}"

    # 2. Recall must exceed 95%
    assert res["recall"] >= 0.95, f"Recall too low: {res['recall']:.4f}"

    # 3. F1 score must exceed 95%
    assert res["f1"] >= 0.95, f"F1 score too low: {res['f1']:.4f}"

    # 4. False positive rate on clean text must be <= 3%
    assert res["fpr"] <= 0.03, f"FPR too high: {res['fpr']:.4f}"

    # 5. P99 latency must be well under 1 ms (1,000 µs)
    assert res["p99_latency_us"] < 500.0, f"Latency too high: {res['p99_latency_us']:.1f}µs"
