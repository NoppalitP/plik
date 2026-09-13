"""Lexicon Matcher for Smart Keyboard.

Loads English (14,224 words) and Thai (24,647 words) dictionaries bundled from
RightLang to provide ultra-fast O(1) exact vocabulary lookups (<0.01 ms).
"""

import os
import sys
from typing import Optional, Set, Tuple

from plik.layouts.kedmanee import to_english, to_thai


def get_data_dir() -> str:
    """Resolve the directory containing dictionary files in source or PyInstaller mode."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        bundled_dir = os.path.join(sys._MEIPASS, "plik", "data")
        if os.path.isdir(bundled_dir):
            return bundled_dir
        bundled_root = os.path.join(sys._MEIPASS, "data")
        if os.path.isdir(bundled_root):
            return bundled_root

    engine_dir = os.path.dirname(os.path.abspath(__file__))
    package_dir = os.path.dirname(engine_dir)
    data_dir = os.path.join(package_dir, "data")
    return data_dir


# Characters that genuinely wrap words (brackets, quotes)
# Note: Punctuation keys like ; ' [ ] , . / - = map to Thai consonants/vowels in Kedmanee!
# Specifically, ' is 'ง' in Thai, so ' must never be stripped as wrapping punctuation!
WRAP_OPEN = '("“[{<'
WRAP_CLOSE = ')"”]}!?>'
THAI_WRAP_OPEN = WRAP_OPEN + "๖"
THAI_WRAP_CLOSE = WRAP_CLOSE + "๗"


MATCHING_BRACKETS = {
    "(": ")",
    "[": "]",
    "{": "}",
    '"': '"',
    "'": "'",
}


def has_unclosed_bracket(text: str) -> bool:
    """Check if text starts with an opening bracket that is not yet closed."""
    for open_b, close_b in MATCHING_BRACKETS.items():
        if text.startswith(open_b):
            if not text.endswith(close_b):
                return True
    return False


class LexiconMatcher:
    """Fast in-memory dictionary matcher for English and Thai words."""

    _instance: Optional["LexiconMatcher"] = None

    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = data_dir or get_data_dir()
        self.eng_words: Set[str] = set()
        self.thai_words: Set[str] = set()
        self._loaded = False
        self._load_dictionaries()

    @classmethod
    def get_instance(cls) -> "LexiconMatcher":
        """Singleton accessor to prevent reloading dictionaries multiple times."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _load_dictionaries(self) -> None:
        """Load dictionary text files into memory sets."""
        eng_path = os.path.join(self.data_dir, "eng.txt")
        thai_path = os.path.join(self.data_dir, "thai.txt")

        if os.path.isfile(eng_path):
            try:
                with open(eng_path, "r", encoding="utf-8") as f:
                    self.eng_words = {
                        line.strip().lower() for line in f if line.strip()
                    }
            except Exception:
                pass

        if os.path.isfile(thai_path):
            try:
                with open(thai_path, "r", encoding="utf-8") as f:
                    self.thai_words = {
                        line.strip() for line in f if line.strip()
                    }
            except Exception:
                pass

        self._loaded = bool(self.eng_words or self.thai_words)

    def is_english_word(self, word: str) -> bool:
        """Check if a token exists in the English dictionary."""
        return word.lower().strip() in self.eng_words

    def is_thai_word(self, word: str) -> bool:
        """Check if a token exists in the Thai dictionary."""
        return word.strip() in self.thai_words

    def evaluate(
        self,
        token: str,
        current_layout: str,
        is_delimiter: bool = False,
    ) -> Tuple[str, float, str]:
        """Evaluate whether the token is in the wrong layout using lexicon lookups.
        
        Supports punctuation-wrapped words (e.g. '(Bamboo)', '๖ฺฟทินน๗' -> '(Bamboo)').
        
        Args:
            token: The raw typed token.
            current_layout: 'EN' or 'TH'.
            is_delimiter: Whether evaluation is triggered at word delimiter.
            
        Returns:
            Tuple of (target_layout, confidence, reason)
            target_layout can be 'EN', 'TH', or 'NONE'.
        """
        clean_token = token.strip()
        if not clean_token or len(clean_token) < 2:
            return "NONE", 0.0, ""

        if current_layout == "EN":
            en_core = clean_token.lstrip(WRAP_OPEN).rstrip(WRAP_CLOSE + ":;").lower()
            if en_core and self.is_english_word(en_core):
                return "KEEP", 1.0, f"Valid English word '{clean_token}'"

            # Check if token has trailing punctuation like ':' before converting
            th_candidate = to_thai(clean_token)
            th_core = th_candidate.lstrip(THAI_WRAP_OPEN).rstrip(THAI_WRAP_CLOSE)
            if th_core and len(th_core) >= 2 and self.is_thai_word(th_core):
                if not is_delimiter and has_unclosed_bracket(clean_token):
                    return "NONE", 0.0, ""
                return "TH", 1.0, f"Lexicon match: Thai word '{th_candidate}'"

            # Also check if stripping trailing punctuation yields a valid Thai word
            if clean_token.endswith(":") or clean_token.endswith(";"):
                base_token = clean_token.rstrip(":;")
                base_th = to_thai(base_token)
                base_core = base_th.lstrip(THAI_WRAP_OPEN).rstrip(THAI_WRAP_CLOSE)
                if base_core and len(base_core) >= 2 and self.is_thai_word(base_core):
                    return "TH", 1.0, f"Lexicon match: Thai word '{th_candidate}'"

        elif current_layout == "TH":
            th_core = clean_token.lstrip(THAI_WRAP_OPEN).rstrip(THAI_WRAP_CLOSE)
            if th_core and self.is_thai_word(th_core):
                return "KEEP", 1.0, f"Valid Thai word '{clean_token}'"

            en_candidate = to_english(clean_token)
            en_core = en_candidate.lstrip(WRAP_OPEN).rstrip(WRAP_CLOSE + ":;").lower()
            if en_core and len(en_core) >= 2 and self.is_english_word(en_core):
                # If candidate starts with bracket and is unclosed, wait for close bracket or delimiter
                if not is_delimiter and has_unclosed_bracket(en_candidate):
                    return "NONE", 0.0, ""
                return "EN", 1.0, f"Lexicon match: English word '{en_candidate}'"

        return "NONE", 0.0, ""
