"""Honest Evaluation Runner: Computes Precision, Recall, F1, Detection Lag, and Latency."""

import statistics
import time
from typing import Dict, List

from plik.engine.core import CoreEngine
from plik.evaluation.mistake_injector import EvalSample, generate_evaluation_samples


def run_honest_evaluation() -> Dict:
    """Execute evaluation on independent external corpus and calculate objective metrics."""
    samples = generate_evaluation_samples()
    engine = CoreEngine()

    metrics_by_condition: Dict[str, Dict] = {}
    total_tp = 0
    total_fp = 0
    total_tn = 0
    total_fn = 0

    detection_lags: List[int] = []
    all_latencies_us: List[float] = []

    print("=" * 80)
    print(" RIGOROUS & HONEST EVALUATION (OUT-OF-DISTRIBUTION REAL CORPORA)")
    print(f" Total Real-World Test Samples: {len(samples)}")
    print(" (Zero test-set hardcoding; Testing continuous Thai prose & genuine code)")
    print("=" * 80)

    for s in samples:
        cond = s.condition
        if cond not in metrics_by_condition:
            metrics_by_condition[cond] = {
                "total": 0, "tp": 0, "fp": 0, "tn": 0, "fn": 0, "lags": []
            }

        metrics_by_condition[cond]["total"] += 1

        engine.set_layout(s.initial_layout)

        switched_to_expected = False
        switched_any = False
        switch_idx = -1

        for idx, ch in enumerate(s.keystrokes):
            start = time.perf_counter()
            act = engine.process_key(ch, is_backspace=False, active_process=s.active_process)
            elapsed_us = (time.perf_counter() - start) * 1_000_000
            all_latencies_us.append(elapsed_us)

            if act.action_type == "AUTO_SWITCH":
                switched_any = True
                if not s.expected_target or act.target_layout == s.expected_target:
                    switched_to_expected = True
                    if switch_idx == -1:
                        switch_idx = idx

        # Classify result
        if s.expected_switch:
            # Expected to switch
            if switched_to_expected:
                metrics_by_condition[cond]["tp"] += 1
                total_tp += 1
                if switch_idx != -1:
                    metrics_by_condition[cond]["lags"].append(switch_idx + 1)
                    detection_lags.append(switch_idx + 1)
            else:
                metrics_by_condition[cond]["fn"] += 1
                total_fn += 1
        else:
            # Expected to stay (Clean typing)
            if not switched_any:
                metrics_by_condition[cond]["tn"] += 1
                total_tn += 1
            else:
                metrics_by_condition[cond]["fp"] += 1
                total_fp += 1


    # Compute macro and micro statistics
    precision = total_tp / (total_tp + total_fp) if (total_tp + total_fp) > 0 else 0.0
    recall = total_tp / (total_tp + total_fn) if (total_tp + total_fn) > 0 else 0.0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
    fpr = total_fp / (total_fp + total_tn) if (total_fp + total_tn) > 0 else 0.0

    mean_lag = statistics.mean(detection_lags) if detection_lags else 0.0
    median_lag = statistics.median(detection_lags) if detection_lags else 0.0

    all_latencies_us.sort()
    p50_lat = all_latencies_us[int(len(all_latencies_us) * 0.50)] if all_latencies_us else 0.0
    p90_lat = all_latencies_us[int(len(all_latencies_us) * 0.90)] if all_latencies_us else 0.0
    p99_lat = all_latencies_us[int(len(all_latencies_us) * 0.99)] if all_latencies_us else 0.0

    # Print breakdown table
    print(f"{'Condition':<22} {'Total':<7} {'TP':<5} {'FP':<5} {'TN':<5} {'FN':<5} {'Accuracy/Recall':<16} {'Avg Lag':<8}")
    print("-" * 80)

    for cond, m in metrics_by_condition.items():
        if m["tp"] + m["fn"] > 0:
            rate = (m["tp"] / (m["tp"] + m["fn"])) * 100.0
            rate_str = f"Recall: {rate:5.1f}%"
        else:
            rate = (m["tn"] / (m["tn"] + m["fp"])) * 100.0
            rate_str = f"Spec:   {rate:5.1f}%"

        cond_lag = f"{statistics.mean(m['lags']):.1f} keys" if m["lags"] else "N/A"
        print(f"{cond:<22} {m['total']:<7} {m['tp']:<5} {m['fp']:<5} {m['tn']:<5} {m['fn']:<5} {rate_str:<16} {cond_lag:<8}")

    print("=" * 80)
    print(" SCIENTIFIC METRICS SUMMARY")
    print("=" * 80)
    print(f"  Precision:                 {precision * 100:.2f}%  (TP / (TP + FP))")
    print(f"  Recall (Sensitivity):      {recall * 100:.2f}%  (TP / (TP + FN))")
    print(f"  F1-Score:                  {f1 * 100:.2f}%")
    print(f"  False Positive Rate (FPR): {fpr * 100:.2f}%  (FP / (FP + TN) - Goal: < 3%)")
    print(f"  Mean Detection Lag:        {mean_lag:.1f} keystrokes (Median: {median_lag:.1f} keys)")
    print(f"  Latency Profile:           P50={p50_lat:.1f}µs | P90={p90_lat:.1f}µs | P99={p99_lat:.1f}µs")
    print("=" * 80)

    return {
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fpr": fpr,
        "mean_lag": mean_lag,
        "p50_latency_us": p50_lat,
        "p99_latency_us": p99_lat,
        "metrics_by_condition": metrics_by_condition,
    }


if __name__ == "__main__":
    run_honest_evaluation()
