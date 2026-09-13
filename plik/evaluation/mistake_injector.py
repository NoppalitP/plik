"""Simulates real-world typing conditions and language-switching mistakes."""

from dataclasses import dataclass
from typing import List, Tuple
from plik.evaluation.corpus_data import (
    CONTINUOUS_THAI_CORPUS,
    REAL_CODE_CORPUS,
    MIXED_COMMUNICATION_CORPUS,
)
from plik.layouts.kedmanee import to_english, to_thai


@dataclass
class EvalSample:
    sample_id: int
    condition: str  # 'CLEAN_THAI', 'CLEAN_CODE', 'FULL_THAI_MISTAKE', 'FULL_CODE_MISTAKE', 'MIXED_MISTAKE'
    keystrokes: str
    initial_layout: str
    active_process: str
    expected_switch: bool  # True if the engine is supposed to switch layout
    expected_target: str   # 'TH', 'EN', or ''
    reference_text: str


def generate_evaluation_samples() -> List[EvalSample]:
    """Generate comprehensive evaluation samples across 4 realistic conditions."""
    samples: List[EvalSample] = []
    sid = 1

    # Condition 1A: Clean Thai Typing (50 samples)
    # The user types valid Thai prose on Thai layout.
    # MUST NOT TRIGGER FALSE POSITIVES!
    for text in CONTINUOUS_THAI_CORPUS:
        samples.append(
            EvalSample(
                sample_id=sid,
                condition="CLEAN_THAI",
                keystrokes=text + " ",
                initial_layout="TH",
                active_process="chrome.exe",
                expected_switch=False,
                expected_target="",
                reference_text=text,
            )
        )
        sid += 1

    # Condition 1B: Clean Code & CLI Typing (50 samples)
    # The user types valid code/CLI on English layout.
    # MUST NOT TRIGGER FALSE POSITIVES!
    for line in REAL_CODE_CORPUS:
        samples.append(
            EvalSample(
                sample_id=sid,
                condition="CLEAN_CODE",
                keystrokes=line + " ",
                initial_layout="EN",
                active_process="code.exe",
                expected_switch=False,
                expected_target="",
                reference_text=line,
            )
        )
        sid += 1

    # Condition 2: Full Thai Mistake (50 samples)
    # The user intended to type Thai prose, but forgot to switch from English layout.
    # MUST DETECT AND SWITCH TO TH!
    for text in CONTINUOUS_THAI_CORPUS:
        keystrokes = to_english(text) + " "
        samples.append(
            EvalSample(
                sample_id=sid,
                condition="FULL_THAI_MISTAKE",
                keystrokes=keystrokes,
                initial_layout="EN",
                active_process="chrome.exe",
                expected_switch=True,
                expected_target="TH",
                reference_text=text,
            )
        )
        sid += 1

    # Condition 3: Full Code/English Mistake (50 samples)
    # The user intended to type code/CLI, but left keyboard in Thai layout.
    # MUST DETECT AND SWITCH TO EN!
    for line in REAL_CODE_CORPUS:
        keystrokes = to_thai(line) + " "
        samples.append(
            EvalSample(
                sample_id=sid,
                condition="FULL_CODE_MISTAKE",
                keystrokes=keystrokes,
                initial_layout="TH",
                active_process="code.exe",
                expected_switch=True,
                expected_target="EN",
                reference_text=line,
            )
        )
        sid += 1

    # Condition 4: Mixed Sentence Mistake (50 samples)
    # The user types a mixed Thai-English sentence, but forgot to switch when typing the English words.
    # (e.g. English words inside Thai sentence typed on Thai keyboard)
    for sent in MIXED_COMMUNICATION_CORPUS:
        # Find English words in the sentence
        words = sent.split(" ")
        corrupted_words = []
        has_english = False
        for w in words:
            if w.isascii() and any(c.isalpha() for c in w):
                # This is an English word typed while in Thai layout!
                corrupted_words.append(to_thai(w))
                has_english = True
            else:
                corrupted_words.append(w)

        if has_english:
            keystrokes = " ".join(corrupted_words) + " "
            samples.append(
                EvalSample(
                    sample_id=sid,
                    condition="MIXED_MISTAKE",
                    keystrokes=keystrokes,
                    initial_layout="TH",
                    active_process="slack.exe",
                    expected_switch=True,
                    expected_target="EN",
                    reference_text=sent,
                )
            )
            sid += 1

    return samples
