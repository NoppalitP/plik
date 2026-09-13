"""Adaptive Memory & Negative Feedback Loop.

Remembers user corrections and undone conversions to permanently suppress repeat
false positives in the same session, personalizing the typing experience.
"""

from typing import Dict, Optional, Set


class AdaptiveMemory:
    """Session-based memory that learns from user corrections and Instant Undos."""

    def __init__(self):
        # Global suppressed tokens (lowercase)
        self._global_suppressed: Set[str] = set()
        # Per-application suppressed tokens: app_name -> Set[token]
        self._app_suppressed: Dict[str, Set[str]] = {}
        # User accepted vocabulary additions
        self._custom_vocab: Set[str] = set()

    def record_negative_feedback(self, token: str, app_name: Optional[str] = None) -> None:
        """Record that an auto-conversion on this token was rejected/undone by the user."""
        t = token.lower().strip()
        if not t:
            return

        self._global_suppressed.add(t)

        if app_name:
            app_lower = app_name.lower().strip()
            if app_lower not in self._app_suppressed:
                self._app_suppressed[app_lower] = set()
            self._app_suppressed[app_lower].add(t)

    def is_suppressed(self, token: str, app_name: Optional[str] = None) -> bool:
        """Check if a token has been suppressed due to negative feedback."""
        t = token.lower().strip()
        if not t:
            return False

        if t in self._global_suppressed:
            return True

        if app_name:
            app_lower = app_name.lower().strip()
            if app_lower in self._app_suppressed and t in self._app_suppressed[app_lower]:
                return True

        return False

    def add_custom_word(self, word: str) -> None:
        """Add user-confirmed custom word to vocabulary."""
        w = word.strip()
        if w:
            self._custom_vocab.add(w)

    def is_custom_word(self, word: str) -> bool:
        """Check if word is in user-confirmed custom vocabulary."""
        return word.strip() in self._custom_vocab

    def clear(self) -> None:
        """Clear all session memory."""
        self._global_suppressed.clear()
        self._app_suppressed.clear()
        self._custom_vocab.clear()
