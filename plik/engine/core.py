"""Core Decision Engine for Smart Keyboard.

Coordinates Tier 1 (Rules), Tier 2 (N-Gram Scorer), Tier 3 (App Context),
and the Instant Undo State Machine.
"""

import time
from dataclasses import dataclass, field
from typing import List, Optional, Set, Tuple

from plik.config import SwitcherConfig
from plik.engine.adaptive_memory import AdaptiveMemory
from plik.engine.app_context import AppCategory, AppContextManager
from plik.engine.corrector import AutoCorrector
from plik.engine.lexicon import LexiconMatcher
from plik.engine.ngram_scorer import NGramScorer
from plik.engine.rules import check_tier1_rules
from plik.engine.syntax_guard import SyntaxGuard
from plik.layouts.kedmanee import to_english, to_thai


@dataclass
class ConversionRecord:
    """Record of a recently performed conversion for Instant Undo."""
    original_text: str
    converted_text: str
    from_layout: str
    to_layout: str
    timestamp: float


@dataclass
class SwitchAction:
    """Action emitted by the Core Engine."""
    action_type: str  # 'AUTO_SWITCH', 'MANUAL_CONVERT', 'INSTANT_UNDO', 'NONE'
    original_text: str = ""
    replacement_text: str = ""
    target_layout: str = ""  # 'TH' or 'EN'
    confidence: float = 0.0
    reason: str = ""
    is_delimiter: bool = False
    delimiter_char: str = ""


class CoreEngine:
    """Intelligent switching decision engine."""

    def __init__(
        self,
        config: Optional[SwitcherConfig] = None,
        context_mgr: Optional[AppContextManager] = None,
        scorer: Optional[NGramScorer] = None,
        syntax_guard: Optional[SyntaxGuard] = None,
        adaptive_memory: Optional[AdaptiveMemory] = None,
        lexicon: Optional[LexiconMatcher] = None,
        corrector: Optional[AutoCorrector] = None,
    ):
        self.config = config or SwitcherConfig()
        self.context_mgr = context_mgr or AppContextManager(self.config)
        self.scorer = scorer or NGramScorer()
        self.syntax_guard = syntax_guard or SyntaxGuard()
        self.adaptive_memory = adaptive_memory or AdaptiveMemory()
        self.lexicon = lexicon or LexiconMatcher.get_instance()
        self.corrector = corrector or AutoCorrector.get_instance()

        # Internal buffer for the current in-flight token
        self._current_token: str = ""
        # Current active layout ('EN' or 'TH')
        self._current_layout: str = "EN"

        # Undo and feedback memory
        self._last_conversion: Optional[ConversionRecord] = None
        self._suppressed_tokens: Set[str] = set()


        # Word boundary delimiters (strictly whitespace so punctuation used by Kedmanee is not split)
        self._delimiters = set(" \t\n\r")
        self._chars_since_delimiter: int = 0

    @property
    def current_token(self) -> str:
        return self._current_token

    @property
    def current_layout(self) -> str:
        return self._current_layout

    def set_layout(self, layout: str) -> None:
        """Explicitly update the engine's known layout ('EN' or 'TH')."""
        new_layout = layout.upper()
        if new_layout == self._current_layout:
            return
        self._current_layout = new_layout
        self._current_token = ""
        self._last_conversion = None
        self._chars_since_delimiter = 0



    def process_key(
        self,
        char: str,
        is_backspace: bool = False,
        active_process: Optional[str] = None,
    ) -> SwitchAction:
        """Process a typed character and return any required action.
        
        Args:
            char: The single character typed (empty if backspace).
            is_backspace: True if the user pressed Backspace.
            active_process: Optional process name override for testing.
        """
        now = time.time()

        # Handle Backspace for Instant Undo
        if is_backspace:
            if self._last_conversion is not None:
                elapsed = now - self._last_conversion.timestamp
                if elapsed <= self.config.instant_undo_window_sec:
                    # Trigger Instant Undo!
                    rec = self._last_conversion
                    self._last_conversion = None
                    # Suppress this token so we don't immediately re-convert it
                    self._suppressed_tokens.add(rec.original_text.lower())
                    self._suppressed_tokens.add(rec.converted_text.lower())
                    self.adaptive_memory.record_negative_feedback(rec.original_text, active_process)
                    self.adaptive_memory.record_negative_feedback(rec.converted_text, active_process)
                    self._current_layout = rec.from_layout
                    self._current_token = rec.original_text

                    return SwitchAction(
                        action_type="INSTANT_UNDO",
                        original_text=rec.converted_text,
                        replacement_text=rec.original_text,
                        target_layout=rec.from_layout,
                        confidence=1.0,
                        reason=f"Instant Undo triggered within {elapsed:.2f}s",
                    )

            # Normal backspace
            if self._current_token:
                self._current_token = self._current_token[:-1]
            return SwitchAction(action_type="NONE")

        # Invalidate old undo record if time expired
        if self._last_conversion and (now - self._last_conversion.timestamp > self.config.instant_undo_window_sec):
            self._last_conversion = None

        # Check delimiters (word boundary)
        if char in self._delimiters:
            self._chars_since_delimiter = 0
            token_to_evaluate = self._current_token
            self._current_token = ""
            if token_to_evaluate:
                return self._evaluate_token(
                    token_to_evaluate,
                    active_process,
                    is_word_start=True,
                    is_delimiter=True,
                    delimiter_char=char,
                )
            return SwitchAction(action_type="NONE")

        # Append character to buffer
        self._current_token += char
        self._chars_since_delimiter += 1
        if len(self._current_token) > self.config.max_buffer_length:
            self._current_token = self._current_token[-self.config.max_buffer_length :]

        # Continuous evaluation if token length meets threshold
        if len(self._current_token) >= self.config.min_word_length:
            is_start = (self._chars_since_delimiter <= len(self._current_token))
            return self._evaluate_token(
                self._current_token,
                active_process,
                in_flight=True,
                is_word_start=is_start,
                is_delimiter=False,
            )

        return SwitchAction(action_type="NONE")

    def manual_convert(self, token_override: Optional[str] = None) -> SwitchAction:
        """Trigger explicit conversion of the current token or specified string."""
        target_token = token_override if token_override is not None else self._current_token
        if not target_token:
            return SwitchAction(action_type="NONE")

        if self._current_layout == "EN":
            converted = to_thai(target_token)
            target_layout = "TH"
        else:
            converted = to_english(target_token)
            target_layout = "EN"

        self._record_conversion(target_token, converted, self._current_layout, target_layout)
        self._current_layout = target_layout
        self._current_token = ""

        return SwitchAction(
            action_type="MANUAL_CONVERT",
            original_text=target_token,
            replacement_text=converted,
            target_layout=target_layout,
            confidence=1.0,
            reason="Manual hotkey conversion triggered",
        )

    def _evaluate_token(
        self,
        token: str,
        active_process: Optional[str] = None,
        in_flight: bool = False,
        is_word_start: bool = True,
        is_delimiter: bool = False,
        delimiter_char: str = "",
    ) -> SwitchAction:
        """Internal evaluation pipeline."""
        token_lower = token.lower().strip()
        if not token_lower or token_lower in self.config.protected_tokens or token_lower in self._suppressed_tokens:
            return SwitchAction(action_type="NONE")

        proc = active_process or self.context_mgr.get_active_process_name()

        # Check adaptive negative feedback memory
        if self.adaptive_memory.is_suppressed(token, proc):
            return SwitchAction(action_type="NONE", reason="Suppressed by adaptive user memory")

        # Tier 3: Process check (Dev tools & secure dialogs)
        if not self.context_mgr.should_auto_switch(proc, self._current_layout):
            return SwitchAction(action_type="NONE", reason=f"Auto-switch disabled for {proc} in {self._current_layout}")

        # Syntax Guard: Code, URLs, paths, and identifier immunity
        is_syntax, syntax_reason = self.syntax_guard.is_protected_syntax(token)
        if is_syntax:
            return SwitchAction(action_type="NONE", reason=f"SyntaxGuard: {syntax_reason}")

        # For DEV_TOOL, protect short tokens (<3 chars like 'pd', 'np', 'db') in EN layout
        is_dev = self.context_mgr.is_dev_tool(proc)
        if is_dev and self._current_layout == "EN" and len(token_lower) < 3:
            return SwitchAction(action_type="NONE", reason=f"Dev tool {proc}: short token '{token}' preserved")

        # Auto-Correction for common typos in current layout
        if self.config.enable_autocorrect and not is_dev:
            lang_enabled = (
                self.config.enable_thai_autocorrect if self._current_layout == "TH"
                else self.config.enable_eng_autocorrect
            )
            if lang_enabled:
                correction = self.corrector.correct(token, self._current_layout)
                if correction:
                    fixed_text, fix_reason = correction
                    self._record_conversion(token, fixed_text, self._current_layout, self._current_layout)
                    if in_flight:
                        if self._current_layout == "TH":
                            self._current_token = ""
                            self._chars_since_delimiter = 0
                        else:
                            self._current_token = fixed_text
                    return SwitchAction(
                        action_type="AUTO_SWITCH",
                        original_text=token,
                        replacement_text=fixed_text,
                        target_layout=self._current_layout,
                        confidence=1.0,
                        reason=fix_reason,
                        is_delimiter=is_delimiter,
                        delimiter_char=delimiter_char,
                    )

        # Tier 0: 511,076-word Lexicon Matcher (Fast O(1) Dictionary Lookup)
        lex_target, lex_conf, lex_reason = self.lexicon.evaluate(
            token, self._current_layout, is_delimiter=is_delimiter
        )
        if lex_target == "KEEP":
            return SwitchAction(action_type="NONE", reason=lex_reason)

        if lex_target in ("TH", "EN") and lex_target != self._current_layout:
            converted = to_thai(token) if lex_target == "TH" else to_english(token)
            self._record_conversion(token, converted, self._current_layout, lex_target)
            self._current_layout = lex_target
            if lex_target == "TH":
                self._current_token = ""
                self._chars_since_delimiter = 0
            else:
                if in_flight:
                    self._current_token = converted
            return SwitchAction(
                action_type="AUTO_SWITCH",
                original_text=token,
                replacement_text=converted,
                target_layout=lex_target,
                confidence=1.0,
                reason=lex_reason,
                is_delimiter=is_delimiter,
                delimiter_char=delimiter_char,
            )

        # For DEV_TOOL, unverified English tokens are preserved to prevent syntax interference
        is_dev = self.context_mgr.is_dev_tool(proc)
        if is_dev and self._current_layout == "EN":
            return SwitchAction(action_type="NONE", reason=f"Dev tool {proc}: unverified EN token preserved")

        # Tier 1: Phonotactic / Syntactic Rules (Deterministic, 100% confidence)
        rule_verdict = check_tier1_rules(token, self._current_layout, is_word_start=is_word_start)

        if rule_verdict == "SWITCH_TO_EN" and self._current_layout == "TH":
            converted = to_english(token)
            self._record_conversion(token, converted, "TH", "EN")
            self._current_layout = "EN"
            if in_flight:
                self._current_token = converted
            return SwitchAction(
                action_type="AUTO_SWITCH",
                original_text=token,
                replacement_text=converted,
                target_layout="EN",
                confidence=1.0,
                reason="Tier 1 Rule: Impossible Thai phonotactics",
                is_delimiter=is_delimiter,
                delimiter_char=delimiter_char,
            )
        elif rule_verdict == "SWITCH_TO_TH" and self._current_layout == "EN":
            converted = to_thai(token)
            self._record_conversion(token, converted, "EN", "TH")
            self._current_layout = "TH"
            self._current_token = ""
            self._chars_since_delimiter = 0
            return SwitchAction(
                action_type="AUTO_SWITCH",
                original_text=token,
                replacement_text=converted,
                target_layout="TH",
                confidence=1.0,
                reason="Tier 1 Rule: Impossible English syntax / Thai Kedmanee symbols",
                is_delimiter=is_delimiter,
                delimiter_char=delimiter_char,
            )

        # Tier 2: Statistical N-Gram Scorer
        target_layout, confidence, reason = self.scorer.evaluate_preference(token, self._current_layout)

        if target_layout != "KEEP" and target_layout != self._current_layout:
            if confidence >= self.config.auto_switch_threshold:
                converted = to_thai(token) if target_layout == "TH" else to_english(token)
                self._record_conversion(token, converted, self._current_layout, target_layout)
                self._current_layout = target_layout
                if target_layout == "TH":
                    self._current_token = ""
                    self._chars_since_delimiter = 0
                else:
                    if in_flight:
                        self._current_token = converted
                return SwitchAction(
                    action_type="AUTO_SWITCH",
                    original_text=token,
                    replacement_text=converted,
                    target_layout=target_layout,
                    confidence=confidence,
                    reason=f"Tier 2 N-Gram: {reason}",
                    is_delimiter=is_delimiter,
                    delimiter_char=delimiter_char,
                )

        return SwitchAction(action_type="NONE")

    def _record_conversion(
        self, original: str, converted: str, from_layout: str, to_layout: str
    ) -> None:
        self._last_conversion = ConversionRecord(
            original_text=original,
            converted_text=converted,
            from_layout=from_layout,
            to_layout=to_layout,
            timestamp=time.time(),
        )
