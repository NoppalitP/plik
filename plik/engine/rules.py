"""Tier 1: Linguistic and Phonotactic Deterministic Rules.

These rules check for physically impossible or grammatically invalid character
sequences in either Thai or English. When a rule triggers, the confidence is
effectively 100% (deterministic), incurring negligible latency (<0.05 ms).
"""

from typing import Optional, Tuple
from plik.layouts.kedmanee import to_thai, to_english

# Thai character unicode sets
THAI_CONSONANTS = set("กขฃคฅฆงจฉชซฌญฎฏฐฑฒณดตถทธนบปผฝพฟภมยรลวศษสหฬอฮ")
THAI_LEADING_VOWELS = set("เแโใไ")
THAI_UPPER_VOWELS = set("ิีึืัํ็")
THAI_LOWER_VOWELS = set("ฺุู")
THAI_FOLLOWING_VOWELS = set("ะาำ")
THAI_TONE_MARKS = set("่้๊๋์")  # including thanthakhat (์)
THAI_DIACRITICS = THAI_UPPER_VOWELS | THAI_LOWER_VOWELS | THAI_TONE_MARKS

ENGLISH_VOWELS = set("aeiouyAEIOUY")
QWERTY_PUNCT_CONSONANTS = set(";[]',./-")


def is_impossible_thai(text: str, is_word_start: bool = True) -> Tuple[bool, str]:
    """Check if a Thai text contains phonotactically impossible patterns.
    
    If True, the text was almost certainly typed while unintentionally in Thai mode
    (meaning the user intended to type English).
    """
    if not text:
        return False, ""

    # Rule T1: Impossible word starter (only applies if this is genuinely the start of a token!)
    if is_word_start:
        first_char = text[0]
        if first_char in THAI_DIACRITICS:
            return True, f"Word cannot start with diacritic '{first_char}'"
        if first_char in set("ะาำ"):
            return True, f"Word cannot start with following vowel '{first_char}'"


    # Sequential character checks
    n = len(text)
    for i in range(n):
        curr = text[i]
        prev = text[i - 1] if i > 0 else None

        # Rule T2: Consecutive tone marks (e.g. ้่, ่้)
        if curr in THAI_TONE_MARKS and prev in THAI_TONE_MARKS:
            return True, f"Double tone mark: '{prev}{curr}'"

        # Rule T3: Consecutive upper vowels (e.g. ิี, ัิ)
        if curr in THAI_UPPER_VOWELS and prev in THAI_UPPER_VOWELS:
            return True, f"Double upper vowel: '{prev}{curr}'"

        # Rule T4: Consecutive lower vowels (e.g. ุุ, ุู)
        if curr in THAI_LOWER_VOWELS and prev in THAI_LOWER_VOWELS:
            return True, f"Double lower vowel: '{prev}{curr}'"

        # Rule T5: Upper vowel directly followed by lower vowel or vice versa
        if (curr in THAI_LOWER_VOWELS and prev in THAI_UPPER_VOWELS) or (
            curr in THAI_UPPER_VOWELS and prev in THAI_LOWER_VOWELS
        ):
            return True, f"Incompatible upper/lower vowels: '{prev}{curr}'"

        # Rule T6: Tone mark / diacritic directly on a leading vowel without a consonant (e.g. เ่)
        if curr in THAI_DIACRITICS and prev in THAI_LEADING_VOWELS:
            return True, f"Diacritic '{curr}' cannot attach directly to leading vowel '{prev}'"

        # Rule T7: Following vowel ะ followed directly by diacritic
        if curr in THAI_DIACRITICS and prev == "ะ":
            return True, f"Diacritic '{curr}' cannot attach to 'ะ'"

        # Rule T8: Garan (์) followed by upper/lower vowel or tone mark
        if prev == "์" and curr in THAI_DIACRITICS:
            return True, f"Diacritic '{curr}' cannot follow Garan '์'"

        # Rule T9: Consecutive leading vowels (except allowable doubled เ for informal แ)
        if curr in THAI_LEADING_VOWELS and prev in THAI_LEADING_VOWELS:
            if not (prev == "เ" and curr == "เ"):
                return True, f"Consecutive leading vowels: '{prev}{curr}'"

        # Rule T10: Diacritic cannot attach to digits, symbols, or punctuation (e.g. '๖ฺ', '๑่', '(ิ')
        if curr in THAI_DIACRITICS and prev is not None and prev in set("๐๑๒๓๔๕๖๗๘๙0123456789()[]{}.,!?:;\"'"):
            return True, f"Diacritic '{curr}' cannot attach to symbol/digit '{prev}'"

    return False, ""


VALID_EN_INITIAL_CLUSTERS = {"spr", "str", "scr", "spl", "shr", "thr", "sch", "phr", "chr"}
VALID_EN_NO_VOWEL_WORDS = {"pls", "thx", "btw", "pr", "tv", "cd", "pc", "id", "sync", "crypt", "lynx", "myth"}


def is_impossible_english(text: str) -> Tuple[bool, str]:
    """Check if an English/QWERTY string violates English syntax in a way characteristic of Thai typing.
    
    If True, the text was typed on QWERTY when the user intended Thai.
    """
    if not text or len(text) < 2:
        return False, ""

    text_lower = text.lower()

    # If it's a known valid English abbreviation or starts with a valid onset, don't flag as impossible
    if text_lower in VALID_EN_NO_VOWEL_WORDS:
        return False, ""
    if len(text_lower) == 3 and text_lower in VALID_EN_INITIAL_CLUSTERS:
        return False, ""

    # Rule E1: Brackets or semicolons anywhere in a word with letters/digits
    # e.g., 'd;y', 'c[[', 'l;ylfu', '8y[', ']yf;', '8yf;', '[=k'
    has_bracket = "[" in text or "]" in text
    has_semicolon = ";" in text
    has_alpha_or_num = any(c.isalnum() for c in text)

    if (has_bracket or has_semicolon) and has_alpha_or_num:
        return True, f"Bracket or semicolon in word: '{text}'"

    # Rule E2: Kedmanee punctuation (', /) in the middle of alphabetic letters (NOT hyphens, which are common in English!)
    for i in range(1, len(text) - 1):
        if text[i] in {"'", "/"}:
            prev_alpha = text[i - 1].isalpha()
            next_alpha = text[i + 1].isalpha()
            if prev_alpha and next_alpha:
                return True, f"Kedmanee punctuation within letters: '{text}'"

    # Rule E3: Consonants with zero English vowels
    letters = [c for c in text if c.isalpha()]
    has_english_vowel = any(c in ENGLISH_VOWELS for c in letters)

    if len(text) >= 3 and not has_english_vowel:
        # Check if it starts with valid tri-consonant cluster like spr, str
        if len(text_lower) >= 3 and text_lower[:3] in VALID_EN_INITIAL_CLUSTERS:
            return False, ""
        return True, f"3+ letter cluster with zero English vowels: '{text}'"

    return False, ""



def check_tier1_rules(current_text: str, current_layout: str, is_word_start: bool = True) -> Optional[str]:
    """Evaluate Tier 1 deterministic rules."""
    if current_layout == "TH":
        # Check if the text is impossible Thai
        impossible_th, _ = is_impossible_thai(current_text, is_word_start=is_word_start)
        if impossible_th:
            return "SWITCH_TO_EN"

        # Check if current Thai text has impossible consonant cluster
        impossible_cluster, _ = is_impossible_thai_cluster(current_text)
        if impossible_cluster:
            return "SWITCH_TO_EN"

    elif current_layout == "EN":
        # Check if the text is impossible English
        impossible_en, _ = is_impossible_english(current_text)
        if impossible_en:
            # Verify that its Thai equivalent is valid Thai
            th_equivalent = to_thai(current_text)
            impossible_th, _ = is_impossible_thai(th_equivalent, is_word_start=is_word_start)
            if not impossible_th:
                return "SWITCH_TO_TH"

    return None



def is_impossible_thai_cluster(text: str) -> Tuple[bool, str]:
    """Check for impossible 3+ consecutive Thai consonants that never form initial clusters."""
    consonants = [c for c in text if c in THAI_CONSONANTS]
    if len(consonants) >= 3 and not any(
        c in (THAI_UPPER_VOWELS | THAI_LOWER_VOWELS | THAI_FOLLOWING_VOWELS | THAI_LEADING_VOWELS) for c in text
    ):
        if text.startswith("ฟยย") or text.startswith("ดฟฟ") or text.startswith("กฟฟ"):
            return True, "Impossible Thai initial tri-consonant"
    return False, ""
