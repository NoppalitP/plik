"""Canonical Prior Academic & Industrial Baselines for Keystroke Layout Disambiguation.

This module implements the three dominant prior paradigms from literature and industry:

1. PureFSABaseline (Aroonmanakun 2002; Kawtrakul & Thumkanon 1999):
   - Rule-based deterministic orthographic/phonotactic finite state automaton.
   - Triggers strictly on phonotactically impossible character sequences.
   - NO statistical n-gram scoring; NO syntactic immunity; NO process context.

2. PureCharNGramBaseline (Cavnar & Trenkle 1994; Ljubešić et al. 2014; Carter et al. 2013):
   - Pure statistical character n-gram log-likelihood ratio (LLR) classifier.
   - Evaluates micro-text n-gram frequency distributions with Laplace smoothing.
   - NO phonotactic hard rules; NO syntactic immunity; NO process context.

3. HeuristicLexiconBaseline (RightLang; Bekesh & Moskalev 2001 / Punto Switcher):
   - Lexicon/dictionary trie lookup with rudimentary diacritic heuristics.
   - Triggers when converted token matches dictionary or contains punctuation inside word.
   - NO syntactic immunity; NO process context; NO instant undo state machine.
"""

import math
from typing import Dict, Optional, Set, Tuple

from plik.benchmark.rightlang_baseline import (
    RIGHTLANG_ENGLISH_WORDS,
    RIGHTLANG_THAI_WORDS,
    THAI_DIACRITICS_SET,
)
from plik.engine.ngram_scorer import (
    COMMON_EN_BIGRAMS,
    COMMON_EN_TRIGRAMS,
    COMMON_TH_BIGRAMS,
    COMMON_TH_TRIGRAMS,
)
from plik.engine.rules import is_impossible_english, is_impossible_thai
from plik.layouts.kedmanee import to_english, to_thai


# ==============================================================================
# Baseline 1: Pure Phonotactic Finite State Automaton (Aroonmanakun 2002)
# ==============================================================================
class PureFSABaseline:
    """Pure rule-based orthographic/phonotactic finite-state automaton.
    
    Academic Reference:
    - Aroonmanakun, W. (2002). "Collocation and Thai Word Segmentation".
    - Kawtrakul, A., & Thumkanon, C. (1999). "A Statistical Approach to Thai Word Segmentation".
    
    Operates strictly by verifying phonotactic well-formedness:
    - If current layout is EN, checks if typed keys violate English phonotactics
      and become valid Thai syllable sequences.
    - If current layout is TH, checks if typed keys violate Thai orthotactics
      (e.g. orphan diacritics, double tone marks, invalid vowel clusters).
    - Contains ZERO statistical scoring, ZERO syntactic immunity, and ZERO process context.
    """

    def __init__(self):
        self.current_layout: str = "EN"
        self._buffer: str = ""

    def set_layout(self, layout: str) -> None:
        self.current_layout = layout.upper()
        self._buffer = ""

    def process_key(
        self,
        char: str,
        is_backspace: bool = False,
        active_process: Optional[str] = None,
    ) -> str:
        """Process keystroke using purely rule-based phonotactics.
        
        Returns 'AUTO_SWITCH' or 'NONE'.
        """
        if is_backspace:
            if self._buffer:
                self._buffer = self._buffer[:-1]
            return "NONE"

        self._buffer += char
        if len(self._buffer) > 32:
            self._buffer = self._buffer[-32:]

        # Check delimiter boundary
        if char in " \t\n\r":
            token = self._buffer.strip()
            self._buffer = ""
            if not token:
                return "NONE"
            return self._evaluate_buffer(token)

        # Real-time check on running buffer
        return self._evaluate_buffer(self._buffer)

    def _evaluate_buffer(self, text: str) -> str:
        if len(text) < 2:
            return "NONE"

        if self.current_layout == "EN":
            # Check if English phonotactics are violated
            imp_en, _ = is_impossible_english(text)
            if imp_en:
                th_cand = to_thai(text)
                imp_th, _ = is_impossible_thai(th_cand, is_word_start=True)
                if not imp_th:
                    self.current_layout = "TH"
                    self._buffer = ""
                    return "AUTO_SWITCH"

        elif self.current_layout == "TH":
            # Check if Thai orthotactics are violated
            imp_th, _ = is_impossible_thai(text, is_word_start=True)
            if imp_th:
                en_cand = to_english(text)
                imp_en, _ = is_impossible_english(en_cand)
                if not imp_en:
                    self.current_layout = "EN"
                    self._buffer = ""
                    return "AUTO_SWITCH"

        return "NONE"


# ==============================================================================
# Baseline 2: Pure Statistical Character N-Gram Naive Bayes (Cavnar & Trenkle 1994)
# ==============================================================================
class PureCharNGramBaseline:
    """Pure statistical character n-gram language classifier for micro-text.
    
    Academic References:
    - Cavnar, W. B., & Trenkle, J. M. (1994). "N-Gram-Based Text Categorization".
      Proceedings of SDAIR-94, pp. 161-175.
    - Ljubešić, N., Erjavec, T., & Kranjčić, D. (2014). "Discriminating between
      very similar languages in Twitter data". Language Resources and Evaluation.
    - Carter, S., Tsagkias, M., & Weerkamp, W. (2013). "Micro-blog Language
      Identification". JASIST, 64(7), 1301-1315.
      
    Operates strictly by calculating character n-gram Log-Likelihood Ratio (LLR):
      LLR = log P(T_alt | L_alt) - log P(T_curr | L_curr)
    - If LLR > threshold (tau = 1.2), switch layout.
    - Contains ZERO phonotactic hard rules, ZERO syntactic immunity, and ZERO process context.
    """

    def __init__(self, threshold: float = 1.2):
        self.current_layout: str = "EN"
        self._buffer: str = ""
        self.threshold = threshold

        self.en_bigrams = COMMON_EN_BIGRAMS
        self.en_trigrams = COMMON_EN_TRIGRAMS
        self.th_bigrams = COMMON_TH_BIGRAMS
        self.th_trigrams = COMMON_TH_TRIGRAMS

    def set_layout(self, layout: str) -> None:
        self.current_layout = layout.upper()
        self._buffer = ""

    def process_key(
        self,
        char: str,
        is_backspace: bool = False,
        active_process: Optional[str] = None,
    ) -> str:
        """Process keystroke using pure n-gram statistical scoring."""
        if is_backspace:
            if self._buffer:
                self._buffer = self._buffer[:-1]
            return "NONE"

        self._buffer += char
        if len(self._buffer) > 24:
            self._buffer = self._buffer[-24:]

        if char in " \t\n\r":
            token = self._buffer.strip()
            self._buffer = ""
            if not token:
                return "NONE"
            return self._evaluate_ngram(token)

        # Real-time check on token slice
        if len(self._buffer) >= 3:
            return self._evaluate_ngram(self._buffer)

        return "NONE"

    def _score_en(self, text: str) -> float:
        text_lower = text.lower()
        if not text_lower:
            return 0.0
        score = 0.0
        for i in range(len(text_lower) - 1):
            score += self.en_bigrams.get(text_lower[i : i + 2], -0.5)
        for i in range(len(text_lower) - 2):
            score += self.en_trigrams.get(text_lower[i : i + 3], -0.8)
        return score / max(1, len(text))

    def _score_th(self, text: str) -> float:
        if not text:
            return 0.0
        score = 0.0
        for i in range(len(text) - 1):
            score += self.th_bigrams.get(text[i : i + 2], -0.5)
        for i in range(len(text) - 2):
            score += self.th_trigrams.get(text[i : i + 3], -0.8)
        return score / max(1, len(text))

    def _evaluate_ngram(self, token: str) -> str:
        if len(token) < 3:
            return "NONE"

        if self.current_layout == "EN":
            en_score = self._score_en(token)
            th_candidate = to_thai(token)
            th_score = self._score_th(th_candidate)

            delta = th_score - en_score
            if delta > self.threshold:
                self.current_layout = "TH"
                self._buffer = ""
                return "AUTO_SWITCH"

        elif self.current_layout == "TH":
            th_score = self._score_th(token)
            en_candidate = to_english(token)
            en_score = self._score_en(en_candidate)

            delta = en_score - th_score
            if delta > self.threshold:
                self.current_layout = "EN"
                self._buffer = ""
                return "AUTO_SWITCH"

        return "NONE"


import os

INSTALLED_RIGHTLANG_DIR = r"C:\Program Files (x86)\RightLang\dict"

def _load_installed_rightlang_words() -> Tuple[Set[str], Set[str]]:
    """Loads actual 38,871 words from user's installed RightLang files if present."""
    th_path = os.path.join(INSTALLED_RIGHTLANG_DIR, "thai.txt")
    en_path = os.path.join(INSTALLED_RIGHTLANG_DIR, "eng.txt")
    if os.path.exists(th_path) and os.path.exists(en_path):
        try:
            with open(th_path, "r", encoding="utf-8") as f:
                th_set = set(line.strip().lstrip("\ufeff") for line in f if line.strip())
            with open(en_path, "r", encoding="utf-8") as f:
                en_set = set(line.strip().lower() for line in f if line.strip())
            return th_set, en_set
        except Exception:
            pass
    return RIGHTLANG_THAI_WORDS, RIGHTLANG_ENGLISH_WORDS


# ==============================================================================
# Baseline 3: Heuristic Lexicon / Dictionary Matching (RightLang / Punto Switcher)
# ==============================================================================
class HeuristicLexiconBaseline:
    """Lexicon lookup + rudimentary diacritic heuristics (RightLang / Punto Switcher).
    
    Academic & Industrial References:
    - Bekesh, A., & Moskalev, S. (2001). "Punto Switcher Architecture".
    - Sornlertlamvanich, T. (1993, 1999). "Word Segmentation for Thai using Lexitron".
    
    Operates by checking exact dictionary wordlists and rudimentary impossible characters.
    Automatically loads the actual installed RightLang 38,871-word dictionary from
    C:\\Program Files (x86)\\RightLang\\dict if available on the system.
    - NO syntactic immunity (mangles code, URLs, paths, camelCase).
    - NO process context (evaluates dev tools and word processors identically).
    - NO instant undo or adaptive negative feedback loop.
    """

    def __init__(self, use_installed_dict: bool = True):
        self.current_layout: str = "EN"
        self._current_token: str = ""
        if use_installed_dict:
            self.th_words, self.en_words = _load_installed_rightlang_words()
        else:
            self.th_words = RIGHTLANG_THAI_WORDS
            self.en_words = RIGHTLANG_ENGLISH_WORDS
        self.is_using_real_installed = len(self.th_words) > 1000

    def set_layout(self, layout: str) -> None:
        self.current_layout = layout.upper()
        self._current_token = ""

    def process_key(
        self,
        char: str,
        is_backspace: bool = False,
        active_process: Optional[str] = None,
    ) -> str:
        if is_backspace:
            if self._current_token:
                self._current_token = self._current_token[:-1]
            return "NONE"

        if char in " \t\n\r":
            token = self._current_token
            self._current_token = ""
            if not token:
                return "NONE"
            return self._evaluate_token(token)

        self._current_token += char
        if len(self._current_token) >= 3:
            res = self._evaluate_token(self._current_token)
            if res == "AUTO_SWITCH":
                return "AUTO_SWITCH"

        return "NONE"

    def _evaluate_token(self, token: str) -> str:
        if self.current_layout == "EN":
            th_candidate = to_thai(token)
            if th_candidate in self.th_words:
                self.current_layout = "TH"
                return "AUTO_SWITCH"

            # Punctuation heuristic: semicolon or brackets inside word
            if any(c in ";[]" for c in token) and any(c.isalnum() for c in token):
                self.current_layout = "TH"
                return "AUTO_SWITCH"

        elif self.current_layout == "TH":
            en_candidate = to_english(token).lower()
            if en_candidate in self.en_words:
                self.current_layout = "EN"
                return "AUTO_SWITCH"

            # Diacritic heuristic: impossible Thai starter
            if token and token[0] in THAI_DIACRITICS_SET:
                self.current_layout = "EN"
                return "AUTO_SWITCH"

        return "NONE"
