"""Tests for adversarial stress benchmark."""

from plik.evaluation.stress_benchmark import generate_stress_samples, run_stress_benchmark


def test_stress_samples_generation():
    samples = generate_stress_samples()
    assert len(samples) == 150
    categories = set(s.category for s in samples)
    assert len(categories) == 5


def test_stress_benchmark_runs():
    results = run_stress_benchmark()
    assert len(results) == 4

    cha_res = results[3]
    fsa_res = results[0]
    ngram_res = results[1]
    rl_res = results[2]

    # Under brutal stress, CHA should still maintain highest overall accuracy and F1
    assert cha_res["accuracy"] >= rl_res["accuracy"]
    assert cha_res["accuracy"] >= fsa_res["accuracy"]
    assert cha_res["accuracy"] >= ngram_res["accuracy"]
    assert cha_res["f1"] > rl_res["f1"]
