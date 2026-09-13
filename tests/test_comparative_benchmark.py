"""Automated assertion test: Smart Keyboard must outperform RightLang."""

import pytest
from plik.benchmark.runner import run_comparative_benchmark


def test_plik_outperforms_rightlang():
    smart_res, rightlang_res = run_comparative_benchmark()

    # 1. Overall accuracy must be higher
    assert smart_res["accuracy"] > rightlang_res["accuracy"]
    assert smart_res["accuracy"] >= 95.0

    # 2. Zero false positives in developer tools and code
    s_dev_fp = smart_res["categories"]["DEV_TOOLS_CODE"]["false_positives"]
    assert s_dev_fp == 0

    # 3. Zero false positives on URLs and file paths
    s_url_fp = smart_res["categories"]["URLS_AND_FILE_PATHS"]["false_positives"]
    assert s_url_fp == 0

    # 4. Latency must be well under 1 millisecond (1,000 microseconds)
    assert smart_res["latency_us"] < 500.0
