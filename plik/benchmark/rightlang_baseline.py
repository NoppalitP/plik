"""RightLang Baseline Heuristic Model.

Simulates the standard RightLang architecture:
- Fixed dictionary lookup + basic character impossible rules.
- NO process awareness (evaluates VS Code, Terminal, and Notepad identically).
- NO syntax guard (mangles URLs, camelCase, snake_case, and file paths).
- NO Instant Undo mechanism (deleting mistakes requires multiple backspaces + manual re-typing).
- NO adaptive memory / negative feedback loop.
"""

from typing import Optional, Set
from plik.layouts.kedmanee import to_english, to_thai


# RightLang typical wordlists
RIGHTLANG_THAI_WORDS: Set[str] = {
    "การ", "งาน", "คน", "วัน", "ไป", "มา", "มี", "ได้", "จะ", "ใน", "ที่", "ของ",
    "และ", "เป็น", "ให้", "ไม่", "แต่", "นี้", "นั้น", "แล้ว", "กับ", "ทำ", "อยู่",
    "ดี", "สวัสดี", "ภาษา", "แบบ", "ครับ", "ค่ะ", "นะคะ", "เทศา", "กวั",
}

RIGHTLANG_ENGLISH_WORDS: Set[str] = {
    "the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for",
    "not", "on", "with", "he", "as", "you", "do", "at", "this", "but", "his",
    "apple", "test", "break", "code", "run", "push", "pull", "commit", "status",
    "git", "api",
}

THAI_DIACRITICS_SET = set("ิีึืัํ็ฺุู่้๊๋์")


class RightLangBaseline:
    """Simulation of RightLang's core decision logic."""

    def __init__(self):
        self.current_layout: str = "EN"
        self._current_token: str = ""

    def set_layout(self, layout: str) -> None:
        self.current_layout = layout.upper()
        self._current_token = ""

    def process_key(
        self,
        char: str,
        is_backspace: bool = False,
        active_process: Optional[str] = None,  # RightLang ignores active_process!
    ) -> str:
        """Process keypress. Returns 'AUTO_SWITCH', 'INSTANT_UNDO', or 'NONE'."""
        if is_backspace:
            # RightLang has NO Instant Undo: backspace just removes 1 char
            if self._current_token:
                self._current_token = self._current_token[:-1]
            return "NONE"

        if char in " \t\n\r":
            token = self._current_token
            self._current_token = ""
            if not token:
                return "NONE"

            # RightLang logic on word boundary
            return self._evaluate_token(token)

        self._current_token += char
        # RightLang also checks in-flight when word matches dictionary or has impossible chars
        if len(self._current_token) >= 3:
            res = self._evaluate_token(self._current_token)
            if res == "AUTO_SWITCH":
                return "AUTO_SWITCH"

        return "NONE"

    def _evaluate_token(self, token: str) -> str:
        token_lower = token.lower()

        if self.current_layout == "EN":
            # Check if converted to Thai matches Thai dictionary or Kedmanee punctuation
            th_candidate = to_thai(token)
            if th_candidate in RIGHTLANG_THAI_WORDS:
                self.current_layout = "TH"
                return "AUTO_SWITCH"

            # RightLang rule: semicolons or brackets inside word
            if any(c in ";[]" for c in token) and any(c.isalnum() for c in token):
                self.current_layout = "TH"
                return "AUTO_SWITCH"

        elif self.current_layout == "TH":
            # Check if converted to English matches English dictionary
            en_candidate = to_english(token).lower()
            if en_candidate in RIGHTLANG_ENGLISH_WORDS:
                self.current_layout = "EN"
                return "AUTO_SWITCH"

            # RightLang rule: impossible Thai starter
            if token and token[0] in THAI_DIACRITICS_SET:
                self.current_layout = "EN"
                return "AUTO_SWITCH"

        return "NONE"
