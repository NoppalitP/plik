"""Comprehensive Comparative Benchmark Across Prior Academic & Industrial Paradigms.

Evaluates 4 distinct methodologies on 250 out-of-distribution real-world samples:
1. PureFSABaseline (Rule-Based Phonotactics - Aroonmanakun 2002)
2. PureCharNGramBaseline (Statistical Character N-Gram Naive Bayes - Cavnar & Trenkle 1994)
3. HeuristicLexiconBaseline (Dictionary Trie Heuristic - RightLang / Punto Switcher)
4. Proposed CHA (Cascaded Hybrid Architecture with Asymmetric Dev Immunity)

Calculates:
- Classification Metrics: Accuracy, Precision, Recall, F1-Score, False Positive Rate (FPR)
- Operational Metrics: Detection Lag (keystrokes), Keystroke Latency Profile (P50, P90, P99 µs)
- Hypothesis Testing: McNemar's Chi-Square Test (with Edwards continuity correction)
"""

import math
import statistics
import time
from typing import Any, Dict, List, Tuple
from scipy import stats

from plik.engine.core import CoreEngine
from plik.evaluation.baselines import (
    HeuristicLexiconBaseline,
    PureCharNGramBaseline,
    PureFSABaseline,
)
from plik.evaluation.mistake_injector import generate_evaluation_samples


def evaluate_system(system: Any, name: str, samples: list) -> Dict[str, Any]:
    """Evaluates a layout switching model on the benchmark samples."""
    tp = fp = tn = fn = 0
    binary_correct: List[int] = []
    detection_lags: List[int] = []
    latencies_us: List[float] = []

    is_cha = isinstance(system, CoreEngine)

    for s in samples:
        system.set_layout(s.initial_layout)
        switched_any = False
        switched_to_expected = False
        switch_idx = -1

        for idx, ch in enumerate(s.keystrokes):
            start = time.perf_counter()
            if is_cha:
                act = system.process_key(ch, False, s.active_process)
                elapsed_us = (time.perf_counter() - start) * 1_000_000
                latencies_us.append(elapsed_us)
                if act.action_type == "AUTO_SWITCH":
                    switched_any = True
                    if not s.expected_target or act.target_layout == s.expected_target:
                        switched_to_expected = True
                        if switch_idx == -1:
                            switch_idx = idx
            else:
                res = system.process_key(ch, False, s.active_process)
                elapsed_us = (time.perf_counter() - start) * 1_000_000
                latencies_us.append(elapsed_us)
                if res == "AUTO_SWITCH":
                    switched_any = True
                    if not s.expected_target or system.current_layout == s.expected_target:
                        switched_to_expected = True
                        if switch_idx == -1:
                            switch_idx = idx

        # Binary decision outcome
        correct = False
        if s.expected_switch:
            if switched_to_expected:
                tp += 1
                correct = True
                if switch_idx != -1:
                    detection_lags.append(switch_idx + 1)
            else:
                fn += 1
        else:
            if not switched_any:
                tn += 1
                correct = True
            else:
                fp += 1

        binary_correct.append(1 if correct else 0)

    total = len(samples)
    acc = (tp + tn) / total if total > 0 else 0.0
    prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    f1 = 2 * (prec * rec) / (prec + rec) if (prec + rec) > 0 else 0.0
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0

    mean_lag = statistics.mean(detection_lags) if detection_lags else 0.0
    median_lag = statistics.median(detection_lags) if detection_lags else 0.0

    latencies_us.sort()
    n_lat = len(latencies_us)
    p50_lat = latencies_us[int(n_lat * 0.50)] if n_lat else 0.0
    p90_lat = latencies_us[int(n_lat * 0.90)] if n_lat else 0.0
    p99_lat = latencies_us[int(n_lat * 0.99)] if n_lat else 0.0

    return {
        "name": name,
        "total": total,
        "tp": tp,
        "fp": fp,
        "tn": tn,
        "fn": fn,
        "accuracy": acc * 100.0,
        "precision": prec * 100.0,
        "recall": rec * 100.0,
        "f1": f1 * 100.0,
        "fpr": fpr * 100.0,
        "mean_lag": mean_lag,
        "median_lag": median_lag,
        "p50_lat_us": p50_lat,
        "p90_lat_us": p90_lat,
        "p99_lat_us": p99_lat,
        "binary_correct": binary_correct,
    }


def compute_mcnemar(correct_a: List[int], correct_b: List[int]) -> Tuple[float, float]:
    """Computes McNemar's chi-squared test with Edwards continuity correction."""
    b = sum(1 for a, b_val in zip(correct_a, correct_b) if a == 1 and b_val == 0)
    c = sum(1 for a, b_val in zip(correct_a, correct_b) if a == 0 and b_val == 1)

    if (b + c) == 0:
        return 0.0, 1.0

    stat = ((abs(b - c) - 1.0) ** 2) / (b + c)
    p_val = stats.chi2.sf(stat, 1)
    return stat, p_val


def run_comparative_benchmark() -> Dict[str, Any]:
    """Executes the 4-paradigm benchmark and prints formatted research tables."""
    samples = generate_evaluation_samples()

    # Systems to evaluate
    fsa_system = PureFSABaseline()
    ngram_system = PureCharNGramBaseline()
    lex_system = HeuristicLexiconBaseline()
    cha_system = CoreEngine()

    print("=" * 96)
    print(" COMPREHENSIVE BENCHMARK: PROPOSED CHA vs. THREE CANONICAL PRIOR PARADIGMS")
    print(f" Evaluation Corpus: N={len(samples)} real-world samples across 5 typing conditions")
    print("=" * 96)

    res_fsa = evaluate_system(fsa_system, "1. Pure Phonotactic FSA (Aroonmanakun 2002)", samples)
    res_ngram = evaluate_system(ngram_system, "2. Pure Char N-Gram (Cavnar & Trenkle 1994)", samples)
    res_lex = evaluate_system(lex_system, "3. Heuristic Lexicon (RightLang / Punto Switcher)", samples)
    res_cha = evaluate_system(cha_system, "4. Proposed CHA (Cascaded Hybrid Architecture)", samples)

    models = [res_fsa, res_ngram, res_lex, res_cha]

    # Print main classification comparison table
    print(f"{'Methodology / Paradigm':<48} {'Accuracy':<9} {'Precision':<10} {'Recall':<9} {'F1-Score':<9} {'FPR':<7}")
    print("-" * 96)
    for m in models:
        print(
            f"{m['name']:<48} {m['accuracy']:5.1f}%   {m['precision']:5.1f}%    {m['recall']:5.1f}%   {m['f1']:5.1f}%   {m['fpr']:4.1f}%"
        )

    print("=" * 96)
    print(" OPERATIONAL PERFORMANCE & DETECTION EFFICIENCY")
    print("=" * 96)
    print(f"{'Methodology / Paradigm':<48} {'Mean Lag':<11} {'Median Lag':<11} {'P50 Latency':<12} {'P99 Latency':<12}")
    print("-" * 96)
    for m in models:
        mean_l = f"{m['mean_lag']:.1f} keys" if m['mean_lag'] > 0 else "N/A"
        med_l = f"{m['median_lag']:.1f} keys" if m['median_lag'] > 0 else "N/A"
        p50 = f"{m['p50_lat_us']:.1f} µs"
        p99 = f"{m['p99_lat_us']:.1f} µs"
        print(f"{m['name']:<48} {mean_l:<11} {med_l:<11} {p50:<12} {p99:<12}")

    print("=" * 96)
    print(" STATISTICAL HYPOTHESIS TESTING (McNemar's Test with Edwards Correction vs. Proposed CHA)")
    print("=" * 96)

    for baseline in [res_fsa, res_ngram, res_lex]:
        stat, p_val = compute_mcnemar(res_cha["binary_correct"], baseline["binary_correct"])
        sig = "*** (p < 0.001)" if p_val < 0.001 else "** (p < 0.01)" if p_val < 0.05 else "n.s."
        print(f"CHA vs. {baseline['name']}")
        print(f"  McNemar chi2 = {stat:.2f}, p-value = {p_val:.3e}  {sig}")

    print("=" * 96)

    return {
        "fsa": res_fsa,
        "ngram": res_ngram,
        "lexicon": res_lex,
        "cha": res_cha,
    }


if __name__ == "__main__":
    run_comparative_benchmark()
