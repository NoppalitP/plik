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


# Characters that genuinely wrap words (parentheses, quotes, angle brackets)
# Note: Punctuation keys like ; ' [ ] , . / - = map to Thai consonants/vowels in Kedmanee!
# Specifically, [ is 'บ', ] is 'ล', ' is 'ง', ; is 'ว' in Thai!
# They must NEVER be stripped unilaterally as wrapping punctuation!
WRAP_OPEN = '("“<'
WRAP_CLOSE = ')"”>!?'
THAI_WRAP_OPEN = WRAP_OPEN + "๖"
THAI_WRAP_CLOSE = WRAP_CLOSE + "๗"


MATCHING_BRACKETS = {
    "(": ")",
    "[": "]",
    "{": "}",
    '"': '"',
    "'": "'",
}

COMMON_ENGLISH_CONTRACTIONS = {
    "it's", "don't", "can't", "won't", "i'm", "you're", "we're", "they're",
    "he's", "she's", "that's", "what's", "where's", "when's", "why's", "how's",
    "who's", "there's", "here's", "let's", "didn't", "doesn't", "isn't",
    "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't", "couldn't",
    "shouldn't", "wouldn't", "i've", "you've", "we've", "they've", "i'll",
    "you'll", "he'll", "she'll", "we'll", "they'll", "i'd", "you'd", "he'd",
    "she'd", "we'd", "they'd", "ain't", "ma'am", "o'clock"
}


def strip_wrapping_punct(text: str) -> str:
    """Safely strip matching brackets, wrapping quotes, or trailing punctuation from token."""
    t = text.strip()
    if not t:
        return ""
    # Strip balanced brackets
    if len(t) >= 2:
        if (t[0] == "(" and t[-1] == ")") or (t[0] == "[" and t[-1] == "]") or (t[0] == "{" and t[-1] == "}"):
            t = t[1:-1].strip()
        elif (t[0] == '"' and t[-1] == '"') or (t[0] == "“" and t[-1] == "”"):
            t = t[1:-1].strip()
    # Strip safe punctuation from edges (including closing parens, colons, and question marks)
    return t.lstrip('("“<').rstrip(')"”>!?:;')


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
        """Check if a token exists in the English dictionary or standard contractions."""
        w = word.lower().strip()
        if not w:
            return False
        if w in self.eng_words or w in COMMON_ENGLISH_CONTRACTIONS:
            return True
        if w.endswith("'s") and (w[:-2] in self.eng_words or w[:-2] in COMMON_ENGLISH_CONTRACTIONS):
            return True
        if w.endswith("'t") and w[:-2] in self.eng_words:
            return True
        if w.endswith("'"):
            # Plural possessive like users', students'
            return w[:-1] in self.eng_words and w[:-1].endswith("s")
        if w.replace("'", "") in self.eng_words:
            # Must have letters after the apostrophe, e.g. don't, it's, we've
            return "'" in w and not w.startswith("'") and not w.endswith("'")
        return False

    def is_thai_word(self, word: str) -> bool:
        """Check if a token exists in the Thai dictionary."""
        return word.strip() in self.thai_words

    def can_segment_thai(self, text: str) -> bool:
        """Check if a Thai text can be cleanly partitioned into known dictionary words.
        
        Uses dynamic programming to verify compound phrases without spaces
        (e.g. 'นี่เรา', 'คนเรามีกำลัง', 'ทำยังไง', 'ของฉัน', 'สวัสดีครับ').
        """
        clean = text.strip()
        if not clean or len(clean) < 2:
            return False
        if clean in self.thai_words:
            return True
        n = len(clean)
        dp = [False] * (n + 1)
        dp[0] = True
        for i in range(1, n + 1):
            for j in range(max(0, i - 16), i):
                if dp[j] and clean[j:i] in self.thai_words:
                    dp[i] = True
                    break
        return dp[n]

    def evaluate(
        self,
        token: str,
        current_layout: str,
        is_delimiter: bool = False,
        is_dev: bool = False,
    ) -> Tuple[str, float, str]:
        """Evaluate whether the token is in the wrong layout using lexicon lookups.
        
        Supports punctuation-wrapped words (e.g. '(Bamboo)', '๖ฺฟทินน๗' -> '(Bamboo)').
        
        Args:
            token: The raw typed token.
            current_layout: 'EN' or 'TH'.
            is_delimiter: Whether evaluation is triggered at word delimiter.
            is_dev: Whether active process is a developer tool or terminal.
            
        Returns:
            Tuple of (target_layout, confidence, reason)
            target_layout can be 'EN', 'TH', or 'NONE'.
        """
        clean_token = token.strip()
        if not clean_token or len(clean_token) < 2:
            return "NONE", 0.0, ""

        if current_layout == "EN":
            en_core = strip_wrapping_punct(clean_token).lower()
            if en_core and self.is_english_word(en_core):
                return "KEEP", 1.0, f"Valid English word '{clean_token}'"

            # Check if token translates to a valid Thai word or compound phrase
            th_candidate = to_thai(clean_token)
            th_core = strip_wrapping_punct(th_candidate)
            if th_core and len(th_core) >= 2:
                if self.is_thai_word(th_core):
                    if not is_delimiter and has_unclosed_bracket(clean_token):
                        return "NONE", 0.0, ""
                    return "TH", 1.0, f"Lexicon match: Thai word '{th_candidate}'"
                # Compound phrase segmentation: ONLY at word delimiter (e.g. Space) on non-dev tools!
                if is_delimiter and not is_dev and self.can_segment_thai(th_core):
                    return "TH", 1.0, f"Lexicon match: Thai phrase '{th_candidate}'"

            # Also check if stripping trailing punctuation yields a valid Thai word
            if clean_token.endswith(":") or clean_token.endswith(";"):
                base_token = clean_token.rstrip(":;")
                base_th = to_thai(base_token)
                base_core = strip_wrapping_punct(base_th)
                if base_core and len(base_core) >= 2:
                    if self.is_thai_word(base_core):
                        return "TH", 1.0, f"Lexicon match: Thai word '{th_candidate}'"
                    if is_delimiter and not is_dev and self.can_segment_thai(base_core):
                        return "TH", 1.0, f"Lexicon match: Thai phrase '{th_candidate}'"

        elif current_layout == "TH":
            th_core = strip_wrapping_punct(clean_token)
            if th_core and (self.is_thai_word(th_core) or self.can_segment_thai(th_core)):
                return "KEEP", 1.0, f"Valid Thai word '{clean_token}'"

            en_candidate = to_english(clean_token)
            en_core = strip_wrapping_punct(en_candidate).lower()
            if en_core and len(en_core) >= 2 and self.is_english_word(en_core):
                # If candidate starts with bracket and is unclosed, wait for close bracket or delimiter
                if not is_delimiter and has_unclosed_bracket(en_candidate):
                    return "NONE", 0.0, ""
                return "EN", 1.0, f"Lexicon match: English word '{en_candidate}'"

        return "NONE", 0.0, ""
